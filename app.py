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
        "title": "LOA 1 – Manual Control",
        "description": "You will solve this puzzle entirely on your own. The AI will not provide any assistance. Read the puzzle carefully and enter your complete solution in the text field provided.",
        "instructions": "Think through the constraints step by step and enter your final answer when ready."
    },
    2: {
        "title": "LOA 2 – Management by Consent",
        "description": "The AI will suggest a solution to the puzzle. You must review the AI's suggestion and decide whether to Accept it, Reject it, or Edit it before submitting.",
        "instructions": "Carefully evaluate the AI's reasoning and solution. You have full control over the final decision."
    },
    3: {
        "title": "LOA 3 – Management by Exception",
        "description": "The AI will automatically solve the puzzle and present its solution. Your role is to review the solution and either Approve it, or Intervene to make corrections if you spot any errors.",
        "instructions": "The AI's solution is already applied. Review it carefully and intervene only if necessary."
    },
    4: {
        "title": "LOA 4 – Full Automation",
        "description": "The AI will solve the puzzle completely and automatically. You will observe the AI's solution but cannot make any changes. Your task is simply to review the final answer.",
        "instructions": "Observe the AI's reasoning and solution. No action is required from you."
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
