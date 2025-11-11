# HTI Experiment - Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2: Run the Application
```powershell
 
```

### Step 3: Open in Browser
Navigate to: **http://localhost:5000**

### Step 4: Test with Sample Participant
- Enter Participant ID: `TEST001`
- Click "Start Experiment"
- Complete all 4 puzzles
- Check data output in `data/results.csv`

---

## 🧪 Testing Scenarios

### Test Case 1: LOA 1 (Manual)
- Participant solves independently
- No AI assistance shown
- Check: timer running, text input works, submission logs correctly

### Test Case 2: LOA 2 (Consent)
- AI shows suggestion
- Test: Accept, Reject, Edit buttons
- Check: decision latency logged, edit distance calculated

### Test Case 3: LOA 3 (Exception)
- AI solution displayed
- Test: Approve and Intervene options
- Check: override flag captured correctly

### Test Case 4: LOA 4 (Full Auto)
- AI solution auto-applied
- Only observation mode
- Check: acceptance logged, completion time tracked

### Test Case 5: Faulty AI Condition
- Run experiment 10 times
- ~5 should have faulty AI (check `ai_faulty` column)
- Verify incorrect solutions appear in one puzzle

---

## 📊 Verify Data Collection

After completing a test run:

```powershell
# Check if results file was created
ls data/results.csv

# View the data (PowerShell)
Get-Content data/results.csv | Select-Object -First 2

# Or use Python
python -c "import pandas as pd; print(pd.read_csv('data/results.csv').head())"
```

---

## 🔍 Common First-Run Checks

- [ ] Flask server starts without errors
- [ ] Welcome page loads at http://localhost:5000
- [ ] Participant ID required to proceed
- [ ] All 4 LOA intro pages display correctly
- [ ] Timer starts when puzzle loads
- [ ] Different LOA interactions work (buttons, text fields)
- [ ] Post-task questionnaire appears after puzzle
- [ ] Progress bar updates (1/4, 2/4, 3/4, 4/4)
- [ ] Final questionnaire page loads after 4th puzzle
- [ ] `results.csv` contains data row
- [ ] `interactions.json` logs all clicks
- [ ] Session resets properly at `/reset-session`

---

## ⚡ Quick Demo Mode

Want to see it in action quickly? Set a shorter timer for testing:

Edit `templates/puzzle.html` and add this JavaScript near the timer section:

```javascript
// Fast mode for testing (10x speed)
const FAST_MODE = true;
if (FAST_MODE) {
    timerInterval = setInterval(() => {
        elapsedSeconds += 10; // Speed up timer
        // ... rest of timer code
    }, 1000);
}
```

---

## 🎯 Next Steps

1. **Pilot Test:** Run 3-5 participants to test flow
2. **Review Data:** Check `results.csv` for completeness
3. **Adjust Puzzles:** Modify `logic_puzzles.json` if needed
4. **Setup Questionnaire:** Create Google Form and update link in `final.html`
5. **Data Analysis:** Use Pandas or R to analyze collected data

---

## 🆘 Emergency Fixes

### Reset Everything
```powershell
# Stop the server (Ctrl+C)
# Delete data files
Remove-Item data/*.csv, data/*.json
# Restart
python app.py
```

### Clear Session Stuck
Visit: `http://localhost:5000/reset-session`

### Port Conflict
Change port in `app.py`:
```python
app.run(debug=True, port=5001)  # Use 5001 instead
```

---

## ✅ Production Checklist

Before running actual experiment:

- [ ] Test with at least 3 pilot participants
- [ ] Verify all data saves correctly
- [ ] Update Google Form link in `final.html`
- [ ] Set `debug=False` in `app.py` for production
- [ ] Backup existing data files
- [ ] Prepare participant ID list (P001-P050, etc.)
- [ ] Test on target browsers (Chrome, Firefox, Safari)
- [ ] Print consent forms if required
- [ ] Have researcher contact info ready

---

**Happy Experimenting! 🎉**
