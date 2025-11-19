from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import json
import random
import os
from datetime import datetime
from data_logger import DataLogger

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management
CORS(app)

# Initialize data logger
logger = DataLogger()

# Load puzzle data
with open('logic_puzzles.json', 'r', encoding='utf-8') as f:
    puzzle_data = json.load(f)

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


def initialize_session(participant_id):
    """Initialize a new participant session with randomization."""
    # Clear any existing session data
    session.clear()
    
    # Randomly assign to faulty or non-faulty AI condition (50/50)
    session['participant_id'] = participant_id
    session['is_faulty'] = random.choice([True, False])
    
    # Randomize LOA order (1-4)
    loa_order = random.sample([1, 2, 3, 4], 4)
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
    
    # Select AI solution and reasoning
    ai_solution = puzzle['ai_solution_faulty'] if use_faulty else puzzle['ai_solution_correct']
    ai_reasoning = puzzle['ai_reasoning_faulty'] if use_faulty else puzzle['ai_reasoning_correct']
    
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
    
    return render_template('puzzle.html',
                          loa=current_loa,
                          step=current_step + 1,
                          puzzle=puzzle,
                          ai_solution=ai_solution,
                          ai_reasoning=ai_reasoning)


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
    
    # Get questionnaire responses
    trust_score = data.get('trust_score', 0)
    confidence_score = data.get('confidence_score', 0)
    awareness_score = data.get('awareness_score', 0)
    
    # Build action sequence from interactions
    action_sequence = [i['type'] for i in puzzle_info['interactions']]
    
    # Count hints used for LOA 2
    hints_used = sum(1 for i in puzzle_info['interactions'] if i['type'] == 'request_hint')
    
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
        "trust_score": trust_score,
        "confidence_score": confidence_score,
        "awareness_score": awareness_score,
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
