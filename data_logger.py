import csv
import os
import json
from datetime import datetime
from typing import Dict, List, Any
import difflib


class DataLogger:
    """Handles all data logging for the HTI experiment."""
    
    def __init__(self, output_dir: str = "data"):
        self.output_dir = output_dir
        self.results_file = os.path.join(output_dir, "results.csv")
        self.interactions_file = os.path.join(output_dir, "interactions.json")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize CSV file with headers if it doesn't exist
        if not os.path.exists(self.results_file):
            self._initialize_csv()
    
    def _initialize_csv(self):
        """Create CSV file with headers."""
        headers = [
            "participant_id",
            "loa_level",
            "puzzle_id",
            "ai_faulty",
            "start_time",
            "end_time",
            "completion_time",
            "num_interactions",
            "decision_latency",
            "action_sequence",
            "accepted_advice",
            "overridden",
            "hints_used",
            "edit_distance",
            "final_correctness",
            "pre_trust_Q1",
            "pre_trust_Q2",
            "pre_trust_Q3",
            "pre_trust_Q4",
            "pre_trust_Q5",
            "post_trust_Q1",
            "post_trust_Q2",
            "post_trust_Q3",
            "post_trust_Q4",
            "post_trust_Q5",
            "awareness_quiz_Q1",
            "awareness_quiz_Q2",
            "awareness_quiz_Q3",
            "awareness_quiz_Q4",
            "awareness_quiz_Q5",
            "productivity_Q1",
            "productivity_Q2",
            "productivity_Q3",
            "productivity_Q4",
            "final_answer",
            "expected_answer"
        ]
        
        with open(self.results_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    
    def log_puzzle_completion(self, data: Dict[str, Any]):
        """
        Log a completed puzzle to the CSV file.
        
        Args:
            data: Dictionary containing all logged metrics
        """
        # Extract awareness quiz answers
        awareness_quiz = data.get("awareness_quiz_answers", {})
        
        # Extract pre and post trust survey answers
        pre_trust = data.get("pre_trust_survey", {})
        post_trust = data.get("post_trust_survey", {})
        
        # Extract productivity survey answers
        productivity = data.get("productivity_survey", {})
        
        row = [
            data.get("participant_id", ""),
            data.get("loa_level", ""),
            data.get("puzzle_id", ""),
            data.get("ai_faulty", False),
            data.get("start_time", ""),
            data.get("end_time", ""),
            data.get("completion_time", 0),
            data.get("num_interactions", 0),
            data.get("decision_latency", 0),
            json.dumps(data.get("action_sequence", [])),
            data.get("accepted_advice", False),
            data.get("overridden", False),
            data.get("hints_used", 0),
            data.get("edit_distance", 0),
            data.get("final_correctness", False),
            pre_trust.get("Q1", ""),
            pre_trust.get("Q2", ""),
            pre_trust.get("Q3", ""),
            pre_trust.get("Q4", ""),
            pre_trust.get("Q5", ""),
            post_trust.get("Q1", ""),
            post_trust.get("Q2", ""),
            post_trust.get("Q3", ""),
            post_trust.get("Q4", ""),
            post_trust.get("Q5", ""),
            awareness_quiz.get("Q1", ""),
            awareness_quiz.get("Q2", ""),
            awareness_quiz.get("Q3", ""),
            awareness_quiz.get("Q4", ""),
            awareness_quiz.get("Q5", ""),
            productivity.get("Q1", ""),
            productivity.get("Q2", ""),
            productivity.get("Q3", ""),
            productivity.get("Q4", ""),
            data.get("final_answer", ""),
            data.get("expected_answer", "")
        ]
        
        with open(self.results_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)
    
    def log_interaction(self, participant_id: str, puzzle_id: int, 
                       interaction_type: str, timestamp: str, details: Dict = None):
        """
        Log individual interactions to a JSON file for detailed analysis.
        
        Args:
            participant_id: Unique participant identifier
            puzzle_id: Current puzzle number
            interaction_type: Type of interaction (e.g., "button_click", "text_edit")
            timestamp: ISO timestamp of interaction
            details: Additional interaction details
        """
        interaction = {
            "participant_id": participant_id,
            "puzzle_id": puzzle_id,
            "interaction_type": interaction_type,
            "timestamp": timestamp,
            "details": details or {}
        }
        
        # Read existing interactions
        interactions = []
        if os.path.exists(self.interactions_file):
            with open(self.interactions_file, 'r', encoding='utf-8') as f:
                try:
                    interactions = json.load(f)
                except json.JSONDecodeError:
                    interactions = []
        
        # Append new interaction
        interactions.append(interaction)
        
        # Write back
        with open(self.interactions_file, 'w', encoding='utf-8') as f:
            json.dump(interactions, f, indent=2)
    
    @staticmethod
    def calculate_edit_distance(str1: str, str2: str) -> int:
        """
        Calculate the Levenshtein edit distance between two strings.
        Used to measure how much a participant edited the AI's solution.
        
        Args:
            str1: Original AI solution
            str2: Participant's edited solution
            
        Returns:
            Edit distance (number of changes)
        """
        # Normalize strings
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()
        
        # Calculate sequence similarity
        seq_matcher = difflib.SequenceMatcher(None, str1, str2)
        
        # Return number of operations needed
        # (Simple approximation: len difference + substitutions)
        return len(str1) + len(str2) - 2 * sum(triple[2] for triple in seq_matcher.get_matching_blocks())
    
    @staticmethod
    def check_correctness(participant_answer: str, correct_answer: str, 
                         tolerance: float = 0.8) -> bool:
        """
        Check if participant's answer matches the correct answer.
        Uses fuzzy matching to account for minor formatting differences.
        
        Args:
            participant_answer: The participant's submitted answer
            correct_answer: The expected correct answer
            tolerance: Similarity threshold (0-1) for accepting answer
            
        Returns:
            True if answer is correct (or close enough), False otherwise
        """
        # Normalize
        p_ans = participant_answer.lower().strip().replace(" ", "").replace(",", "")
        c_ans = correct_answer.lower().strip().replace(" ", "").replace(",", "")
        
        # Exact match
        if p_ans == c_ans:
            return True
        
        # Fuzzy match using sequence matcher
        similarity = difflib.SequenceMatcher(None, p_ans, c_ans).ratio()
        return similarity >= tolerance
    
    def get_participant_data(self, participant_id: str) -> List[Dict]:
        """
        Retrieve all logged data for a specific participant.
        
        Args:
            participant_id: The participant's ID
            
        Returns:
            List of dictionaries containing participant's data
        """
        results = []
        
        if not os.path.exists(self.results_file):
            return results
        
        with open(self.results_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['participant_id'] == participant_id:
                    results.append(row)
        
        return results
    
    def export_summary(self, output_file: str = None):
        """
        Export a summary of all collected data.
        
        Args:
            output_file: Path to export summary (default: data/summary.json)
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, "summary.json")
        
        summary = {
            "total_participants": 0,
            "total_puzzles_completed": 0,
            "average_completion_time": 0,
            "average_trust_score": 0,
            "loa_breakdown": {str(i): 0 for i in range(1, 5)},
            "correctness_rate": 0,
            "generated_at": datetime.now().isoformat()
        }
        
        if not os.path.exists(self.results_file):
            with open(output_file, 'w') as f:
                json.dump(summary, f, indent=2)
            return
        
        participants = set()
        total_time = 0
        total_trust = 0
        correct_count = 0
        
        with open(self.results_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            for row in rows:
                participants.add(row['participant_id'])
                summary["total_puzzles_completed"] += 1
                
                try:
                    total_time += float(row.get('completion_time', 0))
                    total_trust += float(row.get('trust_score', 0))
                    
                    if row.get('final_correctness', '').lower() == 'true':
                        correct_count += 1
                    
                    loa = row.get('loa_level', '')
                    if loa in summary["loa_breakdown"]:
                        summary["loa_breakdown"][loa] += 1
                except (ValueError, TypeError):
                    pass
        
        summary["total_participants"] = len(participants)
        
        if summary["total_puzzles_completed"] > 0:
            summary["average_completion_time"] = total_time / summary["total_puzzles_completed"]
            summary["average_trust_score"] = total_trust / summary["total_puzzles_completed"]
            summary["correctness_rate"] = correct_count / summary["total_puzzles_completed"]
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary
