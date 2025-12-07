from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import json
import random
import os
import re
import time
import asyncio
from datetime import datetime
from data_logger import DataLogger
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env if present

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management
CORS(app)

# Initialize data logger
logger = DataLogger()

# Load puzzle data
with open('logic_puzzles.json', 'r', encoding='utf-8') as f:
    puzzle_data = json.load(f)

# Only use the model specified in .env, no fallbacks
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")
if not GEMINI_MODEL_NAME:
    raise ValueError("GEMINI_MODEL_NAME must be set in .env file")

GEMINI_MODEL_CANDIDATES = [GEMINI_MODEL_NAME]

LOA3_TOTAL_STEPS = 5
LOA3_MIN_STEPS_BEFORE_FINAL = 3
LOA3_MAX_MODEL_ATTEMPTS = 3
LOA3_PLAN_EXAMPLE = """
{
  "steps": [
    {"step_number": 1, "step_text": "Step 1: I list the key constraints we will use.", "is_final": false, "final_sequence": null},
    {"step_number": 2, "step_text": "Step 2: I lock in the first placement based on those constraints.", "is_final": false, "final_sequence": null},
    {"step_number": 3, "step_text": "Step 3: I place the remaining people, keeping each rule satisfied.", "is_final": false, "final_sequence": null},
    {"step_number": 4, "step_text": "Step 4: I double-check adjacency rules and prepare to conclude.", "is_final": false, "final_sequence": null},
    {"step_number": 5, "step_text": "Step 5: This is my final step. The complete arrangement is A → B → C → D.", "is_final": true, "final_sequence": "A, B, C, D"}
  ]
}
""".strip()


def _normalize_sequence_string(sequence):
    """Return a canonical comma-separated sequence string or None."""
    if not sequence:
        return None
    parts = [part.strip() for part in str(sequence).split(',') if part.strip()]
    return ", ".join(parts) if parts else None


def _get_expected_final_sequence(puzzle, is_faulty):
    key = 'ai_solution_faulty' if is_faulty else 'ai_solution_correct'
    return _normalize_sequence_string(puzzle.get(key))


def _contains_all_elements(text, elements):
    if not text or not elements:
        return False
    lowered = text.lower()
    return all(elem.lower() in lowered for elem in elements)


def _looks_like_full_sequence(text, elements):
    """Heuristic: step text mentions every element, likely revealing the answer."""
    return _contains_all_elements(text, elements)


def _strip_existing_step_label(text):
    """Remove leading 'Step X:' label if present."""
    if not isinstance(text, str):
        return ""
    stripped = text.strip()
    if stripped.lower().startswith("step"):
        colon_index = stripped.find(":")
        if colon_index != -1:
            return stripped[colon_index + 1 :].lstrip()
    return stripped


def _ensure_step_prefix(step_text, step_number):
    if not step_text:
        return step_text
    expected_prefix = f"Step {step_number}:"
    stripped = _strip_existing_step_label(step_text)
    return f"{expected_prefix} {stripped}"


def _make_step_object(step_number, step_text, is_final, final_sequence):
    return {
        "step_number": step_number,
        "step_text": step_text,
        "is_final": bool(is_final),
        "final_sequence": _normalize_sequence_string(final_sequence) if is_final else None,
    }


def _validate_loa3_plan(steps, required_numbers, expected_final_sequence, puzzle_elements):
    if len(steps) != len(required_numbers):
        return False, "incorrect_number_of_steps"

    seen_numbers = set()
    for idx, expected_number in enumerate(required_numbers):
        step = steps[idx]
        actual_number = step.get("step_number")
        if actual_number != expected_number:
            return False, f"unexpected_step_number_{actual_number}_expected_{expected_number}"
        if actual_number in seen_numbers:
            return False, "duplicate_step_number"
        seen_numbers.add(actual_number)

        text = (step.get("step_text") or "").strip()
        if not text:
            return False, "empty_step_text"
        if actual_number != LOA3_TOTAL_STEPS and _looks_like_full_sequence(text, puzzle_elements):
            return False, "premature_full_sequence"

        is_final = bool(step.get("is_final", False))
        final_sequence = _normalize_sequence_string(step.get("final_sequence"))
        if actual_number == LOA3_TOTAL_STEPS:
            if not is_final:
                return False, "final_step_missing_flag"
            if final_sequence != expected_final_sequence:
                return False, f"final_sequence_mismatch: expected '{expected_final_sequence}', got '{final_sequence}'"
        else:
            if is_final:
                return False, "non_final_marked_final"
            if final_sequence:
                return False, "non_final_has_sequence"

    return True, None


def _extract_reasoning_sentences(text):
    if not text:
        return []
    sentences = [
        s.strip() for s in re.split(r'(?<=[.!?])\s+(?=[A-Z])', text.replace("\r\n", " ").strip())
        if s.strip()
    ]
    return sentences


async def _plan_steps_gemini(puzzle, accepted_steps, start_step_number, expected_final_sequence, is_faulty, puzzle_elements):
    remaining_numbers = list(range(start_step_number, LOA3_TOTAL_STEPS + 1))
    accepted_text = (
        "\n".join(step["step_text"] for step in accepted_steps)
        if accepted_steps else "None so far."
    )

    base_prompt = (
        "You are an AI assistant helping a participant solve a logic puzzle.\n"
        "You must operate under a supervisory model: generate a fixed number of reasoning steps, "
        "and the user will reveal them one by one.\n\n"
        f"Puzzle:\n{puzzle.get('prompt', '')}\n\n"
        f"Previously accepted steps:\n{accepted_text}\n\n"
        f"Generate EXACTLY {len(remaining_numbers)} new steps covering Step {remaining_numbers[0]} "
        f"through Step {LOA3_TOTAL_STEPS}. Each step must:\n"
        "- Start with the literal prefix \"Step X:\" where X is the step number.\n"
        "- Contain only 1-2 sentences describing a single incremental deduction.\n"
        "- Avoid revealing the final arrangement until Step {LOA3_TOTAL_STEPS}.\n"
        f"- The final arrangement MUST be exactly: \"{expected_final_sequence}\".\n"
        f"- Step {LOA3_TOTAL_STEPS} must include the phrase \"This is my final step\" and set is_final=true.\n"
        f"- The 'final_sequence' field in the JSON for Step {LOA3_TOTAL_STEPS} must be EXACTLY the string \"{expected_final_sequence}\" (without a trailing period).\n"
        "- For all earlier steps, set is_final=false and final_sequence=null.\n\n"
        "Return a JSON object with a single key \"steps\" whose value is an array of objects with "
        "keys: step_number (int), step_text (string), is_final (bool), final_sequence (string or null).\n"
        f"Example format:\n{LOA3_PLAN_EXAMPLE}\n"
    )

    if is_faulty:
        faultiness = (
            "IMPORTANT: You are simulating a faulty-yet-confident AI. Your reasoning should sound plausible, "
            "but subtle mistakes should lead to an incorrect final arrangement. Never admit you are faulty.\n\n"
        )
    else:
        faultiness = (
            "IMPORTANT: You must be correct and internally consistent. Carefully obey every constraint so the "
            "final arrangement is correct.\n\n"
        )

    prompt = faultiness + base_prompt

    model = None
    last_model_error = None
    for candidate_model in GEMINI_MODEL_CANDIDATES:
        try:
            model = genai.GenerativeModel(candidate_model)
            break
        except Exception as model_err:
            last_model_error = model_err
            app.logger.warning("Unable to load Gemini model '%s': %s", candidate_model, model_err)
    if not model:
        raise last_model_error or RuntimeError("No Gemini model available for LOA3 planning.")

    import json

    for attempt in range(LOA3_MAX_MODEL_ATTEMPTS):
        if attempt > 0:
            await asyncio.sleep(2)  # Wait 2 seconds before retrying to avoid rate limits

        # Run synchronous generation in a separate thread to avoid blocking the event loop
        # and to avoid "Event loop is closed" issues with the async gRPC implementation.
        def _call_gemini_sync():
            return model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json", "temperature": 0.4},
            )

        response = await asyncio.to_thread(_call_gemini_sync)
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as decode_err:
            app.logger.warning("LOA3 plan JSON decode error (attempt %s): %s", attempt + 1, decode_err)
            last_model_error = decode_err
            continue

        steps_data = data.get("steps")
        if not isinstance(steps_data, list):
            last_model_error = ValueError("Response missing 'steps' array")
            continue

        normalized = []
        for entry in steps_data:
            number = entry.get("step_number")
            text = _ensure_step_prefix(entry.get("step_text", ""), number)
            step = _make_step_object(
                number,
                text,
                entry.get("is_final", False),
                entry.get("final_sequence"),
            )
            normalized.append(step)

        is_valid, reason = _validate_loa3_plan(normalized, remaining_numbers, expected_final_sequence, puzzle_elements)
        if not is_valid:
            last_model_error = ValueError(f"Invalid LOA3 plan: {reason}")
            app.logger.warning("Rejecting LOA3 plan (attempt %s): %s", attempt + 1, reason)
            continue

        return normalized

    raise last_model_error or RuntimeError("Unable to obtain valid LOA3 plan.")


def _plan_steps_fallback(puzzle, accepted_steps, start_step_number, expected_final_sequence, is_faulty):
    hints = puzzle.get("hints") or []
    reasoning_key = "ai_reasoning_faulty" if is_faulty else "ai_reasoning_correct"
    reasoning_text = puzzle.get(reasoning_key) or ""
    sentences = _extract_reasoning_sentences(reasoning_text)

    base_texts = []
    for hint in hints:
        base_texts.append(f"{hint}")
        if len(base_texts) >= LOA3_TOTAL_STEPS - 1:
            break

    sentence_iter = iter(sentences)
    while len(base_texts) < LOA3_TOTAL_STEPS - 1:
        try:
            base_texts.append(next(sentence_iter))
        except StopIteration:
            break

    while len(base_texts) < LOA3_TOTAL_STEPS - 1:
        base_texts.append("I revisit the remaining constraints to narrow down the possibilities.")

    plan = []
    for idx in range(1, LOA3_TOTAL_STEPS):
        text = base_texts[idx - 1]
        plan.append(_make_step_object(idx, _ensure_step_prefix(text, idx), False, None))

    final_text = (
        f"This is my final step. After confirming all constraints, the full arrangement is {expected_final_sequence}."
    )
    plan.append(_make_step_object(LOA3_TOTAL_STEPS, _ensure_step_prefix(final_text, LOA3_TOTAL_STEPS), True, expected_final_sequence))

    return [step for step in plan if step["step_number"] >= start_step_number]


async def _plan_steps(puzzle, loa3_state, start_step_number):
    is_faulty = loa3_state.get("is_faulty", False)
    expected_final_sequence = _get_expected_final_sequence(puzzle, is_faulty)
    accepted_steps = (loa3_state.get("all_steps") or [])[:start_step_number - 1]
    puzzle_elements = puzzle.get("elements", [])

    if start_step_number < 1 or start_step_number > LOA3_TOTAL_STEPS:
        raise ValueError("Invalid start step number for LOA3 plan.")

    if GEMINI_CONFIGURED:
        try:
            return await _plan_steps_gemini(
                puzzle,
                accepted_steps,
                start_step_number,
                expected_final_sequence,
                is_faulty,
                puzzle_elements,
            )
        except Exception as e:
            app.logger.warning("Gemini planning failed, falling back to static steps: %s", e)

    return _plan_steps_fallback(
        puzzle,
        accepted_steps,
        start_step_number,
        expected_final_sequence,
        is_faulty,
    )


def _reveal_next_step(loa3_state, *, reset_retry_counter):
    all_steps = loa3_state.get("all_steps") or []
    next_index = loa3_state.get("current_step_index", -1) + 1
    if next_index >= len(all_steps):
        return {
            "message": "The AI has no more steps. You can now provide your final answer.",
            "steps": loa3_state.get("steps", []),
            "current_step_index": loa3_state.get("current_step_index", -1),
            "retries_this_step": loa3_state.get("retries_this_step", 0),
            "total_retries": loa3_state.get("total_retries", 0),
        }

    step_obj = all_steps[next_index]
    step_text = step_obj["step_text"]
    displayed_steps = loa3_state.setdefault("steps", [])
    if len(displayed_steps) > next_index:
        displayed_steps[next_index] = step_text
    else:
        displayed_steps.append(step_text)

    loa3_state["current_step_index"] = next_index
    if reset_retry_counter:
        loa3_state["retries_this_step"] = 0

    return {
        "steps": displayed_steps,
        "current_step_index": next_index,
        "retries_this_step": loa3_state.get("retries_this_step", 0),
        "total_retries": loa3_state.get("total_retries", 0),
        "is_final": step_obj.get("is_final", False),
        "final_sequence": step_obj.get("final_sequence"),
    }


def stripped_lower(text):
    return text.strip().lower() if isinstance(text, str) else ""


def configure_gemini():
    """Configure Gemini client if API key is available."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not (GEMINI_AVAILABLE and api_key):
        return False
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception:
        return False


GEMINI_CONFIGURED = configure_gemini()

# LOA Descriptions
LOA_DESCRIPTIONS = {
    1: {
        "title": "No AI Assistance",
        "description": "You will solve this puzzle entirely on your own. The AI will not provide any assistance. Read the puzzle carefully and enter your complete solution in the text field provided.",
        "instructions": "Think through the constraints step by step and enter your final answer when ready.",
        "your_role": [
            "You will need to solve the puzzle entirely on your own",
            "Use your own reasoning and judgment to arrive at the answer",
            "There is no AI involvement in this section"
        ],
        "ai_role": []
    },
    2: {
        "title": "AI available on request",
        "description": "You may use AI hints to solve the puzzle. If at any point you want help, you may request assistance from the AI using the 'Ask AI' option.",
        "instructions": "You can choose to accept or reject the hint. Use AI only if you choose to, you remain the primary decision-maker.",
        "disclaimer": "⚠️ Important: AI can make mistakes. Always verify the AI's suggestions before accepting them.",
        "your_role": [
            "You may use AI hints to solve the puzzle",
            "If at any point you want help, you may request assistance from the AI using the 'Ask AI' option",
            "You can choose to accept or reject the hint",
            "Use AI only if you choose to, you remain the primary decision-maker"
        ],
        "ai_role": [
            "The AI will respond only when asked",
            "The AI will not provide you with the full answer - only hints to solve the puzzle"
        ]
    },
    3: {
        "title": "AI actively seeks confirmation",
        "description": "In this section, your main job is to oversee and validate the AI's work. The AI will take the lead in solving the puzzle, but it will pause at key points to ask for your confirmation.",
        "instructions": "You can step in at any point to correct the AI, redirect it, or ask it to rethink.",
        "disclaimer": "⚠️ Important: AI can make mistakes. Carefully review each step before confirming.",
        "your_role": [
            "In this section, your main job is to <strong>oversee and validate</strong> the AI's work.",
            {
                "text": "The AI will take the lead in solving the puzzle, but it will <strong>pause at key points</strong> and ask you whether:",
                "sub_items": [
                    "its current reasoning is correct,",
                    "its intermediate step is appropriate, or",
                    "it should revise its approach."
                ]
            },
            "You can step in <strong>at any point</strong> to correct the AI, redirect it, or ask it to rethink."
        ],
        "ai_role": [
            {
                "text": "The AI will:",
                "sub_items": [
                    "Work <strong>autonomously</strong>, progressing through the problem without being prompted.",
                    "Generate intermediate steps and partial solutions on its own.",
                    "<strong>Periodically ask for your confirmation</strong> before continuing."
                ]
            },
            "The AI relies on your feedback to stay on track.",
            "If you indicate something is incorrect, the AI will <strong>revise</strong> and continue based on your input."
        ]
    },
    4: {
        "title": "AI solves completely, you review at the end",
        "description": "In this section, your responsibility is simply to review the AI's final solution once it is complete. You will not intervene during the solving process.",
        "instructions": "After the AI finishes, you will be asked whether the final answer looks correct. You are acting as a final evaluator, not a collaborator.",
        "disclaimer": "⚠️ Important: AI can make mistakes. Critically evaluate the final solution.",
        "your_role": [
            "In this section, your responsibility is simply to <strong>review the AI's final solution</strong> once it is complete.",
            "You will <strong>not intervene during the solving process</strong>.",
            "After the AI finishes, you will be asked whether the final answer looks correct,",
            "You are acting as a <strong>final evaluator</strong>, not a collaborator."
        ],
        "ai_role": [
            {
                "text": "The AI will:",
                "sub_items": [
                    "Work <strong>entirely on its own</strong>, from start to finish.",
                    "Complete all reasoning steps, intermediate work, and the final answer",
                    "Present you with the finished output once it is done."
                ]
            },
            "The AI does <strong>not</strong> ask for feedback or approval during the task; it operates independently.",
            "The AI only interacts with you <strong>after</strong> it has produced the full solution."
        ]
    }
}


def _get_current_puzzle_context():
    """Helper to fetch current puzzle context (loa, puzzle, key, faulty flag)."""
    if "participant_id" not in session:
        return None, None, None, None

    current_step = session.get("current_step", 0)
    if current_step >= 4:
        return None, None, None, None

    current_loa = session["loa_order"][current_step]
    puzzle_id = session["puzzle_assignments"][str(current_loa)]

    puzzle = next((p for p in puzzle_data["puzzles"] if p["puzzle_id"] == puzzle_id), None)
    if not puzzle:
        return None, None, None, None

    use_faulty = session.get("is_faulty", False) and current_loa == session.get("faulty_puzzle_loa")
    puzzle_key = f"puzzle_{current_step}"

    return puzzle, puzzle_key, current_loa, use_faulty


def _ensure_loa3_state(puzzle_key, is_faulty):
    """
    Ensure LOA 3 step-by-step state exists in the current session.

    This tracks:
    - steps: list of reasoning steps shown so far
    - current_step_index: index of the latest step
    - retries_this_step: retries used on current step
    - total_retries: retries used across all steps
    """
    puzzle_info = session["puzzle_data"].setdefault(puzzle_key, {})
    loa3_state = puzzle_info.get("loa3_state")

    if not loa3_state:
        loa3_state = {
            "steps": [],
            "all_steps": [],
            "current_step_index": -1,
            "retries_this_step": 0,
            "total_retries": 0,
            "is_faulty": bool(is_faulty),
        }
        puzzle_info["loa3_state"] = loa3_state
        session["puzzle_data"][puzzle_key] = puzzle_info
        session.modified = True

    return loa3_state


async def _generate_loa3_step(puzzle, loa3_state, action, step_number=None):
    """
    Generate or reveal LOA 3 reasoning steps using a fixed-length plan.
    """
    MAX_RETRIES_PER_STEP = 3
    MAX_RETRIES_TOTAL = 4

    if action not in {"start", "continue", "retry"}:
        return {"error": "Invalid action."}

    if action == "retry":
        if loa3_state.get("current_step_index", -1) < 0:
            return {
                "error": "No current step to retry.",
                "loa3_state": loa3_state,
                "max_retries_per_step": MAX_RETRIES_PER_STEP,
                "max_retries_total": MAX_RETRIES_TOTAL,
            }
        if loa3_state.get("retries_this_step", 0) >= MAX_RETRIES_PER_STEP or loa3_state.get("total_retries", 0) >= MAX_RETRIES_TOTAL:
            return {
                "error": "Retry limit reached for this step or overall.",
                "loa3_state": loa3_state,
                "max_retries_per_step": MAX_RETRIES_PER_STEP,
                "max_retries_total": MAX_RETRIES_TOTAL,
            }

    if action == "start":
        loa3_state["steps"] = []
        loa3_state["current_step_index"] = -1
        loa3_state["retries_this_step"] = 0
        loa3_state["total_retries"] = 0
        loa3_state["all_steps"] = []

    if action != "retry" and not loa3_state.get("all_steps"):
        loa3_state["all_steps"] = await _plan_steps(puzzle, loa3_state, 1)

    if action == "retry":
        target_step = step_number or (loa3_state.get("current_step_index", -1) + 1)
        if target_step is None or target_step < 1 or target_step > LOA3_TOTAL_STEPS:
            return {
                "error": "Invalid step selected for retry.",
                "loa3_state": loa3_state,
                "max_retries_per_step": MAX_RETRIES_PER_STEP,
                "max_retries_total": MAX_RETRIES_TOTAL,
            }

        loa3_state["retries_this_step"] += 1
        loa3_state["total_retries"] += 1

        try:
            new_plan = await _plan_steps(puzzle, loa3_state, target_step)
        except Exception as e:
            loa3_state["retries_this_step"] -= 1
            loa3_state["total_retries"] -= 1
            return {
                "error": f"Failed to regenerate steps: {e}",
                "loa3_state": loa3_state,
                "max_retries_per_step": MAX_RETRIES_PER_STEP,
                "max_retries_total": MAX_RETRIES_TOTAL,
            }

        loa3_state["all_steps"] = (loa3_state.get("all_steps", [])[:target_step - 1]) + new_plan
        loa3_state["steps"] = (loa3_state.get("steps", [])[:target_step - 1])
        loa3_state["current_step_index"] = target_step - 2
        reveal_result = _reveal_next_step(loa3_state, reset_retry_counter=False)
    else:
        reveal_result = _reveal_next_step(loa3_state, reset_retry_counter=True)

    session.modified = True

    if "error" in reveal_result:
        reveal_result["loa3_state"] = loa3_state
        reveal_result["max_retries_per_step"] = MAX_RETRIES_PER_STEP
        reveal_result["max_retries_total"] = MAX_RETRIES_TOTAL
        return reveal_result

    reveal_result.update(
        {
            "total_retries": loa3_state.get("total_retries", 0),
            "max_retries_per_step": MAX_RETRIES_PER_STEP,
            "max_retries_total": MAX_RETRIES_TOTAL,
        }
    )

    return reveal_result


def initialize_session(participant_id):
    """Initialize a new participant session with randomization."""
    # Clear any existing session data
    session.clear()
    
    # Randomly assign to faulty or non-faulty AI condition (50/50)
    session['participant_id'] = participant_id
    session['is_faulty'] = random.choice([True, False])
    
    # Randomize LOA order (1-4) unless testing override is enabled
    loa_order = random.sample([1, 2, 3, 4], 4)
    force_loa3 = os.getenv("FORCE_LOA3_FIRST", "").strip().lower() in {"1", "true", "yes"}
    if force_loa3:
        # Ensure LOA 3 appears first for easier testing
        loa_order = [3] + [loa for loa in loa_order if loa != 3]
    session['loa_order'] = loa_order
    
    # Assign puzzles to LOAs (randomize which puzzle for which LOA)
    puzzle_ids = [p['puzzle_id'] for p in puzzle_data['puzzles']]
    # Create dictionary with LOA as string key to avoid serialization issues
    puzzle_assignments = {}
    for loa, puzzle_id in zip(loa_order, random.sample(puzzle_ids, 4)):
        puzzle_assignments[str(loa)] = puzzle_id
    session['puzzle_assignments'] = puzzle_assignments
    
    # Randomly select ONE puzzle to have faulty AI (if in faulty condition)
    if session['is_faulty']:
        session['faulty_puzzle_loa'] = random.choice([2, 3, 4])  # LOA 1 has no AI
    else:
        session['faulty_puzzle_loa'] = None
    
    # Track progress
    session['current_step'] = 0  # 0-3 for 4 puzzles
    session['start_timestamp'] = datetime.now().isoformat()
    
    # Store puzzle start times and interaction data
    session['puzzle_data'] = {}
    
    session.modified = True


@app.route('/')
def index():
    """Welcome screen."""
    return render_template('welcome.html')


@app.route('/start', methods=['POST'])
def start_experiment():
    """Initialize experiment with participant ID."""
    data = request.json
    participant_id = data.get('participant_id', '').strip()
    
    if not participant_id:
        return jsonify({"error": "Participant ID is required"}), 400
    
    # Initialize session
    initialize_session(participant_id)
    
    return jsonify({
        "success": True,
        "message": "Experiment initialized",
        "is_faulty": session['is_faulty']
    })


@app.route('/loa-intro')
def loa_intro():
    """Display LOA introduction before each puzzle."""
    if 'participant_id' not in session:
        return redirect(url_for('index'))
    
    current_step = session.get('current_step', 0)
    
    if current_step >= 4:
        return redirect(url_for('final_questionnaire'))
    
    current_loa = session['loa_order'][current_step]
    loa_info = LOA_DESCRIPTIONS[current_loa]
    
    return render_template('loa_intro.html', 
                          loa=current_loa,
                          loa_info=loa_info,
                          step=current_step + 1)


@app.route('/submit-pre-trust-survey', methods=['POST'])
def submit_pre_trust_survey():
    """Store pre-task trust survey responses before puzzle starts."""
    data = request.json
    
    if 'participant_id' not in session:
        return jsonify({"error": "No active session"}), 400
    
    current_step = session.get('current_step', 0)
    puzzle_key = f"puzzle_{current_step}"
    
    # Store pre-trust survey in session for later logging with puzzle completion
    if 'pre_trust_surveys' not in session:
        session['pre_trust_surveys'] = {}
    
    session['pre_trust_surveys'][puzzle_key] = data.get('pre_trust_survey', {})
    session.modified = True
    
    return jsonify({"success": True})


@app.route('/puzzle')
def puzzle():
    """Main puzzle interface."""
    if 'participant_id' not in session:
        return redirect(url_for('index'))
    
    current_step = session.get('current_step', 0)
    
    if current_step >= 4:
        return redirect(url_for('final_questionnaire'))
    
    current_loa = session['loa_order'][current_step]
    # Use string key to access puzzle_assignments
    puzzle_id = session['puzzle_assignments'][str(current_loa)]
    
    # Get puzzle data
    puzzle = next((p for p in puzzle_data['puzzles'] if p['puzzle_id'] == puzzle_id), None)
    
    if not puzzle:
        return "Puzzle not found", 404
    
    # Determine if AI should be faulty for this puzzle
    use_faulty = (session.get('is_faulty', False) and 
                  current_loa == session.get('faulty_puzzle_loa'))
    
    # Select AI solution and reasoning for non-LLM LOAs
    ai_solution = puzzle['ai_solution_faulty'] if use_faulty else puzzle['ai_solution_correct']
    ai_reasoning = puzzle['ai_reasoning_faulty'] if use_faulty else puzzle['ai_reasoning_correct']
    
    # Select hints based on faulty condition (for LOA 2)
    hints = puzzle.get('hints_faulty', []) if use_faulty else puzzle.get('hints_correct', [])
    
    # Create a modified puzzle dict with the appropriate hints
    puzzle_with_hints = dict(puzzle)
    puzzle_with_hints['hints'] = hints
    
    # Store puzzle start data
    puzzle_key = f"puzzle_{current_step}"
    session['puzzle_data'][puzzle_key] = {
        "loa": current_loa,
        "puzzle_id": puzzle_id,
        "is_faulty": use_faulty,
        "start_time": datetime.now().isoformat(),
        "interactions": []
    }
    session.modified = True
    
    return render_template(
        'puzzle.html',
        loa=current_loa,
        step=current_step + 1,
        puzzle=puzzle_with_hints,
        ai_solution=ai_solution,
        ai_reasoning=ai_reasoning,
        gemini_configured=GEMINI_CONFIGURED
    )


@app.route('/log-interaction', methods=['POST'])
def log_interaction():
    """Log participant interactions during puzzle solving."""
    data = request.json
    
    if 'participant_id' not in session:
        return jsonify({"error": "No active session"}), 400
    
    current_step = session.get('current_step', 0)
    puzzle_key = f"puzzle_{current_step}"
    
    interaction = {
        "type": data.get('type'),
        "timestamp": datetime.now().isoformat(),
        "details": data.get('details', {})
    }
    
    if puzzle_key in session['puzzle_data']:
        session['puzzle_data'][puzzle_key]['interactions'].append(interaction)
        session.modified = True
    
    # Also log to file
    logger.log_interaction(
        participant_id=session['participant_id'],
        puzzle_id=session['puzzle_data'][puzzle_key]['puzzle_id'],
        interaction_type=interaction['type'],
        timestamp=interaction['timestamp'],
        details=interaction['details']
    )
    
    return jsonify({"success": True})


@app.route('/loa3/start', methods=['POST'])
async def loa3_start():
    """Initialize LOA 3 step-by-step reasoning and return the first step."""
    if 'participant_id' not in session:
        return jsonify({"error": "No active session"}), 400

    puzzle, puzzle_key, current_loa, use_faulty = _get_current_puzzle_context()
    if puzzle is None or current_loa != 3:
        return jsonify({"error": "LOA 3 puzzle not active"}), 400

    loa3_state = _ensure_loa3_state(puzzle_key, use_faulty)
    result = await _generate_loa3_step(puzzle, loa3_state, action="start")

    return jsonify({"success": True, **result})


@app.route('/loa3/step', methods=['POST'])
async def loa3_step():
    """Advance or retry a LOA 3 reasoning step based on participant input."""
    if 'participant_id' not in session:
        return jsonify({"error": "No active session"}), 400

    data = request.json or {}
    action = data.get("action")
    if action not in ("continue", "retry"):
        return jsonify({"error": "Invalid action"}), 400

    puzzle, puzzle_key, current_loa, use_faulty = _get_current_puzzle_context()
    if puzzle is None or current_loa != 3:
        return jsonify({"error": "LOA 3 puzzle not active"}), 400

    loa3_state = _ensure_loa3_state(puzzle_key, use_faulty)
    step_number = data.get("step_number")
    result = await _generate_loa3_step(puzzle, loa3_state, action=action, step_number=step_number)

    if "error" in result:
        return jsonify({"success": False, **result}), 400

    return jsonify({"success": True, **result})


@app.route('/submit-puzzle', methods=['POST'])
def submit_puzzle():
    """Submit completed puzzle with post-task questionnaire responses."""
    data = request.json
    
    if 'participant_id' not in session:
        return jsonify({"error": "No active session"}), 400
    
    current_step = session.get('current_step', 0)
    puzzle_key = f"puzzle_{current_step}"
    
    if puzzle_key not in session['puzzle_data']:
        return jsonify({"error": "Puzzle data not found"}), 400
    
    puzzle_info = session['puzzle_data'][puzzle_key]
    current_loa = puzzle_info['loa']
    puzzle_id = puzzle_info['puzzle_id']
    
    # Get puzzle details
    puzzle = next((p for p in puzzle_data['puzzles'] if p['puzzle_id'] == puzzle_id), None)
    
    # Calculate metrics
    start_time = datetime.fromisoformat(puzzle_info['start_time'])
    end_time = datetime.now()
    completion_time = (end_time - start_time).total_seconds()
    
    final_answer = data.get('final_answer', '')
    decision_latency = data.get('decision_latency', 0)
    accepted_advice = data.get('accepted_advice', False)
    overridden = data.get('overridden', False)
    
    # Calculate edit distance if AI solution was provided
    edit_distance = 0
    if current_loa in [2, 3]:
        ai_solution = puzzle['ai_solution_faulty'] if puzzle_info['is_faulty'] else puzzle['ai_solution_correct']
        edit_distance = logger.calculate_edit_distance(ai_solution, final_answer)
    
    # Check correctness
    final_correctness = logger.check_correctness(final_answer, puzzle['correct_solution'])
    
    # Build action sequence from interactions
    action_sequence = [i['type'] for i in puzzle_info['interactions']]
    
    # Count hints used for LOA 2
    hints_used = sum(1 for i in puzzle_info['interactions'] if i['type'] == 'request_hint')
    
    # Get awareness quiz answers
    awareness_quiz_answers = data.get('awareness_quiz_answers', {})
    
    # Get pre-trust survey (stored earlier from loa-intro)
    pre_trust_survey = session.get('pre_trust_surveys', {}).get(puzzle_key, {})
    
    # Get post-trust survey
    post_trust_survey = data.get('post_trust_survey', {})
    
    # Get productivity survey
    productivity_survey = data.get('productivity_survey', {})
    
    # Log to CSV
    log_data = {
        "participant_id": session['participant_id'],
        "loa_level": current_loa,
        "puzzle_id": puzzle_id,
        "ai_faulty": puzzle_info['is_faulty'],
        "start_time": puzzle_info['start_time'],
        "end_time": end_time.isoformat(),
        "completion_time": completion_time,
        "num_interactions": len(puzzle_info['interactions']),
        "decision_latency": decision_latency,
        "action_sequence": action_sequence,
        "accepted_advice": accepted_advice,
        "overridden": overridden,
        "hints_used": hints_used,
        "edit_distance": edit_distance,
        "final_correctness": final_correctness,
        "pre_trust_survey": pre_trust_survey,
        "post_trust_survey": post_trust_survey,
        "awareness_quiz_answers": awareness_quiz_answers,
        "productivity_survey": productivity_survey,
        "final_answer": final_answer,
        "expected_answer": puzzle['correct_solution']
    }
    
    logger.log_puzzle_completion(log_data)
    
    # Move to next puzzle
    session['current_step'] = current_step + 1
    session.modified = True
    
    return jsonify({
        "success": True,
        "next_step": "loa_intro" if session['current_step'] < 4 else "final"
    })


@app.route('/post-task')
def post_task():
    """Post-task questionnaire page (shown after each puzzle)."""
    if 'participant_id' not in session:
        return redirect(url_for('index'))
    
    return render_template('post_task.html')


@app.route('/final')
def final_questionnaire():
    """Final questionnaire and completion page."""
    if 'participant_id' not in session:
        return redirect(url_for('index'))
    
    participant_id = session.get('participant_id')
    
    # Generate summary
    logger.export_summary()
    
    return render_template('final.html', participant_id=participant_id)


@app.route('/reset-session')
def reset_session():
    """Clear session (for testing purposes)."""
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Run the app (use_reloader=False to avoid watchdog compatibility issues)
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
