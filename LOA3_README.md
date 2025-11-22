# LOA 3 Step-by-Step Overhaul (Branch `loa3-madhav`)

This branch implements the full LOA 3 supervisory experience described in `LOA3_FIX_PROMPT.md`. Below is a summary of the major changes and how to test them.

## What's New

1. **Single-Call Planning:** `_generate_loa3_step` now plans the entire 5-step reasoning sequence in one Gemini call (or deterministic fallback) and reveals one step per user action. Retries regenerate steps `n..5` so the participant truly supervises.
2. **Strict Prompting & Validation:** The Gemini prompt enforces micro-steps, deferred final answers, and conditional faulty/correct behavior. The final step always matches `ai_solution_correct`/`ai_solution_faulty`.
3. **Retry UX Improvements:** The frontend locks the Retry button until the new step arrives, shows the regenerated step in green, and resets retry counters appropriately.
4. **Fallback Consistency:** When Gemini is unavailable, we synthesize five deterministic steps from puzzle hints/reasoning text and still respect the faulty condition.
5. **Testing Helpers:** Optional `.env` flags `GEMINI_MODEL_NAME` and `FORCE_LOA3_FIRST` make it easy to pin the model and jump straight into LOA 3 during manual testing.

## Key Files

- `app.py`
  - `_plan_steps_gemini` / `_plan_steps_fallback`: produce 5-step plans (Steps 1-5) with schema validation.
  - `_generate_loa3_step`: manages plan storage, reveals steps, handles retries, and enforces retry limits.
  - `initialize_session`: accepts `FORCE_LOA3_FIRST` so LOA 3 can run first when testing.
- `templates/puzzle.html`
  - Updated LOA 3 JS to call the new endpoints, pass `step_number` on retries, highlight regenerated steps, and disable Retry while waiting.
- `static/style.css`
  - `.hint-item.highlight-step` styles revised steps with a green accent.

## Environment / How to Test

1. **.env setup (repo root):**
   - Create `.env` if missing and add:
     ```
     GEMINI_API_KEY=your_key_here
     GEMINI_MODEL_NAME=models/gemini-2.5-flash   # optional but recommended
     FORCE_LOA3_FIRST=false                     # keep false for real runs; set true only when you want LOA 3 first
     ```
   - Do not commit `.env`. For temporary overrides, export vars in your shell instead.

2. **Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Ensure `google-generativeai` and `python-dotenv` install cleanly.

3. **Manual walk-through:**
   - Start the server from repo root: `python app.py`.
   - Visit `http://localhost:5000`, enter a participant ID, and proceed to LOA 3.
   - Click **Start AI** → only Step 1 should display.
   - Use **Continue** to reveal Steps 2-5; the final step auto-fills the drag-and-drop.
   - Use **Retry** on Step *n*: the button disables until the new step arrives (highlighted green), and Steps *n..5* update together.
   - Use `/reset-session` between runs to see both faulty and non-faulty conditions.

4. **Data integrity:** confirm `results.csv` still records `ai_faulty`, `action_sequence`, decision latency, etc.

## Notes / Follow-ups
- If Gemini model names change, set `GEMINI_MODEL_NAME` in `.env` (e.g., `models/gemini-2.5-flash`).
- Consider adding a spinner/toast for the retry wait if we want more user feedback.
- Future work could extend the plan/reveal pattern to other LOAs or add automated tests around `_plan_steps_*`.

