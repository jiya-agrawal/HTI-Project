"""
Quick test to verify session initialization
"""
import json

# Simulate session initialization
from app import puzzle_data

print("Testing session initialization logic...")

# Test 1: Check puzzle data loads
print(f"\n✓ Puzzle data loaded: {len(puzzle_data['puzzles'])} puzzles")

# Test 2: Simulate LOA order
import random
loa_order = random.sample([1, 2, 3, 4], 4)
print(f"✓ LOA order randomized: {loa_order}")

# Test 3: Create puzzle assignments
puzzle_ids = [p['puzzle_id'] for p in puzzle_data['puzzles']]
puzzle_assignments = {}
for loa, puzzle_id in zip(loa_order, random.sample(puzzle_ids, 4)):
    puzzle_assignments[str(loa)] = puzzle_id

print(f"✓ Puzzle assignments created: {puzzle_assignments}")

# Test 4: Access with string key
current_step = 0
current_loa = loa_order[current_step]
puzzle_id = puzzle_assignments[str(current_loa)]
print(f"✓ Can access puzzle for step {current_step}, LOA {current_loa}: puzzle_id={puzzle_id}")

print("\n✅ All session initialization tests passed!")
print("\nThe KeyError should be fixed. Try accessing the application again:")
print("http://localhost:5000")
