# Human-AI Interaction Experiment Platform

## 📋 Overview

This is a web-based experimental platform designed for studying **Human-AI Interaction** with a focus on:
- **Automation levels** (Levels of Automation - LOA 1-4)
- **Trust in AI systems**
- **Situational awareness**
- **Task productivity and correctness**

Participants solve logic-based seating arrangement puzzles under different levels of AI automation, with automatic data collection for research analysis.

---

## 🎯 Features

### ✅ Complete Participant Flow
- Welcome screen with consent information
- Randomized LOA presentation order
- 4 logic puzzles with varying AI automation levels
- Automatic timing and interaction logging
- Post-task Likert-scale questionnaires
- Final questionnaire integration

### 🤖 Four Levels of Automation (LOA)

1. **LOA 1 - Manual Control:** Participant solves puzzle independently
2. **LOA 2 - Management by Consent:** AI suggests solution, participant accepts/rejects/edits
3. **LOA 3 - Management by Exception:** AI auto-solves, participant can intervene
4. **LOA 4 - Full Automation:** AI solves automatically, participant observes

### 📊 Automatic Data Collection

The system logs:
- Participant ID and session timestamps
- Completion time per puzzle
- Number of interactions (clicks, edits)
- Decision latency (time to first action)
- Action sequences
- AI advice acceptance/override rates
- Edit distance from AI solution
- Final answer correctness
- Trust, confidence, and awareness scores (1-7 Likert scales)

### 🔬 A/B Testing Support

- **50% of participants** randomly assigned to "faulty AI" condition
- Faulty AI provides incorrect solutions for one puzzle
- Controlled randomization with seeded values
- All conditions logged for analysis

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
   ```powershell
   cd "d:\SEMESTER7\HTI\Project"
   ```

2. **Install required Python packages:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Verify the directory structure:**
   ```
   Project/
   ├── app.py                    # Main Flask application
   ├── data_logger.py            # Data logging utilities
   ├── logic_puzzles.json        # Puzzle data and AI solutions
   ├── requirements.txt          # Python dependencies
   ├── templates/
   │   ├── welcome.html          # Welcome & consent screen
   │   ├── loa_intro.html        # LOA introduction page
   │   ├── puzzle.html           # Main puzzle interface
   │   └── final.html            # Completion & final questionnaire
   ├── static/
   │   └── style.css             # Styling
   └── data/
       ├── results.csv           # (Generated) Main data export
       ├── interactions.json     # (Generated) Detailed interactions
       └── summary.json          # (Generated) Experiment summary
   ```

---

## ▶️ Running the Experiment

### Start the Server

```powershell
python app.py
```

The server will start at: **http://localhost:5000**

### Access the Experiment

1. Open a web browser
2. Navigate to: `http://localhost:5000`
3. Enter participant ID when prompted (e.g., `P001`, `P002`, etc.)
4. Follow the on-screen instructions

### For Testing

To reset the session and start fresh:
- Visit: `http://localhost:5000/reset-session`

---

## 📂 Data Output

### results.csv

Main data file with columns:
- `participant_id`: Unique participant identifier
- `loa_level`: Level of automation (1-4)
- `puzzle_id`: Which puzzle was presented
- `ai_faulty`: Whether AI gave faulty solution (True/False)
- `start_time`: ISO timestamp when puzzle started
- `end_time`: ISO timestamp when puzzle ended
- `completion_time`: Time taken in seconds
- `num_interactions`: Count of all interactions
- `decision_latency`: Time to first decision (seconds)
- `action_sequence`: JSON array of interaction types
- `accepted_advice`: Whether participant accepted AI solution
- `overridden`: Whether participant overrode AI
- `edit_distance`: Levenshtein distance between AI and final answer
- `final_correctness`: Whether answer was correct
- `trust_score`: Trust rating (1-7)
- `confidence_score`: Confidence rating (1-7)
- `awareness_score`: Awareness rating (1-7)
- `final_answer`: Participant's final solution
- `expected_answer`: Correct solution

### interactions.json

Detailed log of every interaction with timestamps and metadata.

### summary.json

Aggregated statistics:
- Total participants
- Total puzzles completed
- Average completion time
- Average trust scores
- LOA breakdown
- Correctness rate

---

## 🧪 Experimental Design

### Randomization

1. **LOA Order:** Each participant receives all 4 LOAs in random order
2. **Puzzle Assignment:** Puzzles are randomly assigned to LOAs
3. **Faulty AI:** 50% chance of being in faulty condition
4. **Faulty Puzzle:** If faulty, one puzzle (LOA 2, 3, or 4) has incorrect AI solution

### Metrics Calculated

**Trust Indicators:**
- AI advice acceptance rate
- Override frequency
- Decision latency
- Edit severity (edit distance)

**Awareness Indicators:**
- Number of interventions
- Review time before decision
- Correctness detection (for faulty AI)

**Productivity Indicators:**
- Completion time
- Final answer correctness
- Efficiency (time vs. LOA)

---

## 🎨 Customization

### Adding New Puzzles

Edit `logic_puzzles.json`:

```json
{
  "puzzle_id": 5,
  "prompt": "Your puzzle description...",
  "ai_solution_correct": "Correct answer",
  "ai_solution_faulty": "Incorrect answer",
  "ai_reasoning_correct": "Reasoning for correct solution",
  "ai_reasoning_faulty": "Flawed reasoning",
  "correct_solution": "Expected correct answer",
  "explanation": "Why this is correct"
}
```

### Modifying LOA Descriptions

Edit the `LOA_DESCRIPTIONS` dictionary in `app.py`.

### Changing Questionnaire Items

Modify the questionnaire modal in `templates/puzzle.html`.

### Integrating External Questionnaire

Update the link in `templates/final.html`:

```html
<a href="https://forms.gle/YOUR_FORM_ID?entry.1234567890={{ participant_id }}" ...>
```

**Note:** Pre-fill participant ID using Google Forms' URL parameters.

---

## 🔧 Troubleshooting

### Port Already in Use

If port 5000 is occupied, change the port in `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Session Issues

Clear browser cookies or use incognito mode.

### Data Not Saving

Ensure the `data/` directory has write permissions.

### Timer Not Working

Check browser JavaScript console for errors (F12 → Console).

---

## 📊 Data Analysis Tips

### Loading Data in Python

```python
import pandas as pd

# Load results
df = pd.read_csv('data/results.csv')

# Filter by LOA
loa2_data = df[df['loa_level'] == 2]

# Calculate metrics
avg_trust = df.groupby('loa_level')['trust_score'].mean()
acceptance_rate = df.groupby('loa_level')['accepted_advice'].mean()
```

### Statistical Tests

- **Trust across LOAs:** ANOVA or Kruskal-Wallis
- **Faulty vs. Non-Faulty:** Independent t-test
- **Completion Time:** Mixed-effects model with LOA as predictor

---

## 🛡️ Ethics & Privacy

- No personally identifiable information is collected
- Participant IDs should be anonymized codes
- Data stored locally (not transmitted externally)
- Consent information provided on welcome screen
- Participants can withdraw at any time

---

## 📝 Citation

If you use this platform in your research, please cite:

```
[Your Name], [Year]. Human-AI Interaction Experiment Platform.
GitHub: [Repository URL]
```

---

## 🤝 Support

For questions or issues:
- Check the troubleshooting section
- Review Flask documentation: https://flask.palletsprojects.com/
- Contact: [Your Email]

---

## 📄 License

This project is intended for research and educational purposes.

---

## 🎓 Research Context

This platform was developed for studying:
- **Sheridan & Verplank's (1978)** Levels of Automation framework
- **Endsley's (1995)** Situational Awareness model
- **Lee & See's (2004)** Trust in Automation theory
- Human factors in AI-assisted decision making

---

## ✨ Future Enhancements

Potential additions:
- Real-time LLM integration instead of static AI responses
- Eye-tracking integration
- More puzzle types (Sudoku, riddles, etc.)
- Multi-session support
- Real-time dashboard for researchers
- Automatic statistical analysis

---

**Version:** 1.0  
**Last Updated:** November 2025  
**Built with:** Flask, JavaScript, HTML/CSS
