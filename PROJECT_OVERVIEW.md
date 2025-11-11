# HTI Experiment Platform - Complete Package

## 📦 What's Included

Your experimental platform is now complete with:

✅ **Backend (Flask):**
- `app.py` - Main application with all routes and session management
- `data_logger.py` - Comprehensive data collection and logging
- `logic_puzzles.json` - 4 seating arrangement puzzles with AI solutions

✅ **Frontend (HTML/CSS/JS):**
- `welcome.html` - Consent and participant ID entry
- `loa_intro.html` - LOA level introductions
- `puzzle.html` - Interactive puzzle interface with timer
- `final.html` - Completion page with questionnaire link
- `style.css` - Clean, research-appropriate styling

✅ **Utilities:**
- `analyze_data.py` - Automated data analysis script
- `test_system.py` - System verification tests
- `start.ps1` - Easy startup script for Windows

✅ **Documentation:**
- `README.md` - Complete user guide
- `QUICKSTART.md` - Quick start guide
- This file - Project overview

---

## 🎯 Key Features Implemented

### 1. **Four Levels of Automation (LOA)**

| LOA | Type | Description | Actions Available |
|-----|------|-------------|-------------------|
| 1 | Manual | Human solves alone | Text input |
| 2 | Consent | AI suggests, human decides | Accept/Reject/Edit |
| 3 | Exception | AI solves, human supervises | Approve/Intervene |
| 4 | Full Auto | AI handles everything | Observe only |

### 2. **Randomization & Control**
- ✅ Random LOA order per participant
- ✅ Random puzzle-to-LOA assignment
- ✅ 50% faulty AI condition assignment
- ✅ Random faulty puzzle selection
- ✅ Seeded randomization for reproducibility

### 3. **Comprehensive Data Collection**

**Behavioral Metrics:**
- Completion time (seconds)
- Number of interactions
- Decision latency (time to first action)
- Action sequences (button clicks, edits)

**Trust Metrics:**
- AI advice acceptance rate
- Override frequency
- Edit distance from AI solution
- Trust ratings (1-7 Likert)

**Awareness Metrics:**
- Intervention frequency
- Review patterns
- Awareness ratings (1-7 Likert)

**Performance Metrics:**
- Final answer correctness
- Confidence ratings (1-7 Likert)

### 4. **Real-time Logging**
- ✅ CSV export (`results.csv`)
- ✅ JSON interaction log (`interactions.json`)
- ✅ Summary statistics (`summary.json`)
- ✅ Timestamps for all events

---

## 🚀 Quick Start

### Option 1: Using PowerShell Script (Recommended)
```powershell
.\start.ps1
```

### Option 2: Manual Start
```powershell
python app.py
```

Then open: **http://localhost:5000**

---

## 📊 Data Analysis Workflow

### 1. Run the Experiment
```powershell
python app.py
# Collect data from participants
```

### 2. Analyze Results
```powershell
python analyze_data.py
```

This generates:
- Console output with statistics
- `data/analysis_summary.json` with exportable metrics

### 3. Advanced Analysis
```python
import pandas as pd

# Load data
df = pd.read_csv('data/results.csv')

# Trust by LOA
df.groupby('loa_level')['trust_score'].mean()

# Faulty AI impact
df.groupby('ai_faulty')['accepted_advice'].mean()

# Completion time analysis
df.groupby('loa_level')['completion_time'].describe()
```

---

## 🔬 Research Design

### Independent Variables:
1. **Level of Automation (LOA):** 1, 2, 3, 4 (within-subjects)
2. **AI Faultiness:** Faulty vs. Non-faulty (between-subjects)

### Dependent Variables:
1. **Trust:** Acceptance rate, override rate, trust scores
2. **Awareness:** Intervention rate, awareness scores
3. **Productivity:** Completion time, correctness rate
4. **Confidence:** Self-reported confidence scores

### Experimental Flow:
```
Welcome & Consent
    ↓
[For each of 4 puzzles:]
    LOA Introduction
    ↓
    Puzzle Solving (timed)
    ↓
    Post-task Questionnaire
    ↓
[After all 4 puzzles:]
    Final Questionnaire
    ↓
    Completion
```

---

## 📁 File Structure

```
Project/
│
├── app.py                      # Main Flask application
├── data_logger.py              # Data logging utilities
├── logic_puzzles.json          # Puzzle database
├── analyze_data.py             # Data analysis script
├── test_system.py              # System tests
├── start.ps1                   # Startup script
├── requirements.txt            # Python dependencies
│
├── templates/
│   ├── welcome.html            # Entry page
│   ├── loa_intro.html          # LOA descriptions
│   ├── puzzle.html             # Main interface
│   └── final.html              # Completion page
│
├── static/
│   └── style.css               # Styling
│
├── data/                       # Generated data
│   ├── results.csv             # Main data export
│   ├── interactions.json       # Detailed logs
│   └── analysis_summary.json   # Analytics
│
└── docs/
    ├── README.md               # Full documentation
    ├── QUICKSTART.md           # Quick guide
    └── PROJECT_OVERVIEW.md     # This file
```

---

## ✅ Validation Checklist

Before running your study:

### Technical Setup
- [ ] All packages installed (`pip install -r requirements.txt`)
- [ ] System tests pass (`python test_system.py`)
- [ ] Server starts without errors
- [ ] Welcome page loads at http://localhost:5000

### Functionality Tests
- [ ] Can enter participant ID
- [ ] All 4 LOA intro pages display correctly
- [ ] Timer starts when puzzle loads
- [ ] LOA 1: Manual text input works
- [ ] LOA 2: Accept/Reject/Edit buttons work
- [ ] LOA 3: Approve/Intervene buttons work
- [ ] LOA 4: Auto-solve displays correctly
- [ ] Post-task questionnaire appears
- [ ] Progress bar updates (1/4 → 4/4)
- [ ] Final page loads after 4 puzzles

### Data Collection
- [ ] `results.csv` created after first completion
- [ ] All columns populated correctly
- [ ] `interactions.json` logs all actions
- [ ] Timestamps are accurate
- [ ] Random assignment works (check `ai_faulty` column)

### Study Preparation
- [ ] Pilot tested with 3+ participants
- [ ] Google Form link updated in `final.html`
- [ ] Participant ID list prepared
- [ ] Data backup plan in place
- [ ] IRB approval obtained (if required)

---

## 🎓 Theoretical Background

### Levels of Automation (Sheridan & Verplank, 1978)
This study implements 4 levels from the classic 10-level taxonomy:
- **Level 1:** Human does everything
- **Level 7:** AI suggests, human must approve
- **Level 9:** AI decides and acts, informs human
- **Level 10:** AI acts autonomously

### Trust in Automation (Lee & See, 2004)
Key factors measured:
- **Performance:** Correctness and reliability
- **Process:** Transparency and understanding
- **Purpose:** Alignment with user goals

### Situational Awareness (Endsley, 1995)
Three levels assessed:
1. **Perception:** What is the AI doing?
2. **Comprehension:** Why is it doing this?
3. **Projection:** What will happen next?

---

## 📈 Expected Outcomes

### Hypotheses to Test:

**H1: Trust increases with higher LOA**
- Measure: acceptance_rate, trust_score by loa_level

**H2: Awareness decreases with higher LOA**
- Measure: num_interactions, awareness_score by loa_level

**H3: Faulty AI reduces trust**
- Measure: trust_score comparison (faulty vs. non-faulty)

**H4: LOA affects productivity**
- Measure: completion_time, final_correctness by loa_level

---

## 🛠️ Troubleshooting

### Common Issues:

**"Module not found" errors**
```powershell
pip install -r requirements.txt
```

**Port 5000 already in use**
- Edit `app.py`, change: `app.run(port=5001)`

**Session not working**
- Clear browser cookies or use incognito mode

**Data not saving**
- Check `data/` directory permissions
- Verify disk space available

**Timer not starting**
- Check browser console (F12) for JavaScript errors
- Try different browser

---

## 📞 Support

### Resources:
- **Flask Documentation:** https://flask.palletsprojects.com/
- **Python Data Analysis:** https://pandas.pydata.org/
- **Statistical Tests:** Use scipy.stats or R

### For Help:
- Check README.md for detailed guides
- Run `python test_system.py` to diagnose issues
- Review console output for error messages

---

## 📄 Citation

If you use or adapt this platform, please cite:

```bibtex
@software{hti_experiment_platform,
  author = {Your Name},
  title = {Human-AI Interaction Experiment Platform},
  year = {2025},
  url = {https://github.com/your-repo}
}
```

---

## 🔮 Future Enhancements

Potential improvements:
- [ ] Real LLM integration (GPT-4, Claude)
- [ ] More puzzle types (Sudoku, logic grids)
- [ ] Eye-tracking integration
- [ ] Real-time experimenter dashboard
- [ ] Multi-language support
- [ ] Mobile-responsive interface
- [ ] Automated statistical reporting

---

## ⭐ Acknowledgments

Built with:
- **Flask** - Web framework
- **JavaScript** - Client-side interactions
- **Python** - Data processing
- **CSV/JSON** - Data storage

Theoretical frameworks:
- Sheridan & Verplank (1978) - LOA taxonomy
- Lee & See (2004) - Trust in automation
- Endsley (1995) - Situational awareness

---

**Version:** 1.0  
**Date:** November 2025  
**Status:** Production Ready ✅

---

🎉 **Your HTI Experiment Platform is Ready!** 🎉
