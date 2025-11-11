"""
Test script for HTI Experiment Platform
Run this to verify all components are working correctly
"""

import sys
import os
import json

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_test(test_name, passed):
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{test_name}: {status}")

def test_imports():
    """Test if all required packages are installed."""
    print_header("Testing Package Imports")
    
    tests = {
        "Flask": False,
        "Flask-CORS": False,
        "JSON": False,
        "Datetime": False
    }
    
    try:
        import flask
        tests["Flask"] = True
    except ImportError:
        pass
    
    try:
        import flask_cors
        tests["Flask-CORS"] = True
    except ImportError:
        pass
    
    try:
        import json
        tests["JSON"] = True
    except ImportError:
        pass
    
    try:
        from datetime import datetime
        tests["Datetime"] = True
    except ImportError:
        pass
    
    for test_name, passed in tests.items():
        print_test(test_name, passed)
    
    return all(tests.values())

def test_file_structure():
    """Test if all required files exist."""
    print_header("Testing File Structure")
    
    required_files = {
        "app.py": os.path.exists("app.py"),
        "data_logger.py": os.path.exists("data_logger.py"),
        "logic_puzzles.json": os.path.exists("logic_puzzles.json"),
        "requirements.txt": os.path.exists("requirements.txt"),
        "templates/welcome.html": os.path.exists("templates/welcome.html"),
        "templates/loa_intro.html": os.path.exists("templates/loa_intro.html"),
        "templates/puzzle.html": os.path.exists("templates/puzzle.html"),
        "templates/final.html": os.path.exists("templates/final.html"),
        "static/style.css": os.path.exists("static/style.css"),
        "data/ directory": os.path.exists("data")
    }
    
    for file_name, exists in required_files.items():
        print_test(file_name, exists)
    
    return all(required_files.values())

def test_puzzle_data():
    """Test if puzzle data is valid."""
    print_header("Testing Puzzle Data")
    
    tests = {
        "JSON file loads": False,
        "Has 'puzzles' key": False,
        "Has 4+ puzzles": False,
        "All puzzles have required fields": False
    }
    
    try:
        with open('logic_puzzles.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        tests["JSON file loads"] = True
        
        if 'puzzles' in data:
            tests["Has 'puzzles' key"] = True
            
            if len(data['puzzles']) >= 4:
                tests["Has 4+ puzzles"] = True
            
            required_fields = ['puzzle_id', 'prompt', 'ai_solution_correct', 
                              'ai_solution_faulty', 'correct_solution']
            
            all_valid = True
            for puzzle in data['puzzles']:
                for field in required_fields:
                    if field not in puzzle:
                        all_valid = False
                        break
            
            tests["All puzzles have required fields"] = all_valid
    
    except Exception as e:
        print(f"{Colors.RED}Error loading puzzle data: {e}{Colors.END}")
    
    for test_name, passed in tests.items():
        print_test(test_name, passed)
    
    return all(tests.values())

def test_data_logger():
    """Test data logger functionality."""
    print_header("Testing Data Logger")
    
    tests = {
        "DataLogger imports": False,
        "Can initialize": False,
        "Can calculate edit distance": False,
        "Can check correctness": False
    }
    
    try:
        from data_logger import DataLogger
        tests["DataLogger imports"] = True
        
        logger = DataLogger(output_dir="data")
        tests["Can initialize"] = True
        
        # Test edit distance
        dist = DataLogger.calculate_edit_distance("Hello", "Hallo")
        tests["Can calculate edit distance"] = (dist >= 0)
        
        # Test correctness check
        is_correct = DataLogger.check_correctness("Alice, Bob, Charlie", "Alice, Bob, Charlie")
        tests["Can check correctness"] = is_correct
        
    except Exception as e:
        print(f"{Colors.RED}Error testing data logger: {e}{Colors.END}")
    
    for test_name, passed in tests.items():
        print_test(test_name, passed)
    
    return all(tests.values())

def test_flask_routes():
    """Test Flask application routes."""
    print_header("Testing Flask Routes")
    
    tests = {
        "App imports": False,
        "Has index route": False,
        "Has start route": False,
        "Has loa-intro route": False,
        "Has puzzle route": False,
        "Has submit-puzzle route": False
    }
    
    try:
        from app import app
        tests["App imports"] = True
        
        # Get all registered routes
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        
        tests["Has index route"] = any('/' == r for r in routes)
        tests["Has start route"] = any('/start' in r for r in routes)
        tests["Has loa-intro route"] = any('/loa-intro' in r for r in routes)
        tests["Has puzzle route"] = any('/puzzle' in r for r in routes)
        tests["Has submit-puzzle route"] = any('/submit-puzzle' in r for r in routes)
        
    except Exception as e:
        print(f"{Colors.RED}Error testing Flask routes: {e}{Colors.END}")
    
    for test_name, passed in tests.items():
        print_test(test_name, passed)
    
    return all(tests.values())

def display_summary(all_tests_passed):
    """Display final summary."""
    print_header("TEST SUMMARY")
    
    if all_tests_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED{Colors.END}")
        print(f"\n{Colors.CYAN}Your experiment platform is ready!{Colors.END}")
        print(f"\nTo start the server, run:")
        print(f"{Colors.YELLOW}python app.py{Colors.END}")
        print(f"\nThen open your browser to:")
        print(f"{Colors.YELLOW}http://localhost:5000{Colors.END}\n")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.END}")
        print(f"\n{Colors.YELLOW}Please fix the issues above before running the experiment.{Colors.END}\n")

def main():
    """Run all tests."""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("="*60)
    print("🧪 HTI EXPERIMENT - SYSTEM TEST")
    print("="*60)
    print(f"{Colors.END}")
    
    results = []
    
    results.append(test_imports())
    results.append(test_file_structure())
    results.append(test_puzzle_data())
    results.append(test_data_logger())
    results.append(test_flask_routes())
    
    all_passed = all(results)
    display_summary(all_passed)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
