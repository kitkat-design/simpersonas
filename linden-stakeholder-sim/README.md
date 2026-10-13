# Linden Compute – AI Stakeholder Simulation

A small Streamlit app for **AI Driven Decision Making, Session 3** ("Linden Compute expansion
decision"). Five AI personas – Clara Weiss, Daniel Hart, Miriam Keller, Jonas Berg and Elena
Rossi – react to Linden Compute's proposal for a third data centre. You stay the executive team
and make the final recommendation.

## How the app follows the assignment

| Assignment step | In the app |
|---|---|
| 1 Develop the five personas | Tab ①: four-layer profiles, `[Assumption]` labels, what could change each position. Fixed during the run (`sim/personas.py`). |
| 2 Simulate first reactions | Tab ②: you **write and lock predictions first**, then 5 **separate AI calls run in parallel**. Each sees only the shared case facts, the original proposal and its *own* profile – never another reply. Format: position, concern, condition for reconsidering, next action, < 100 words (word count shown). |
| 3 Run a short discussion | Tab ③: up to 2 exchanges. All replies so far are shared; each persona responds to a specific point made by someone else and explains any change in position. Optional clarifying question per exchange; the proposal stays unchanged. |
| 4 Revise the proposal | Tab ④: you write the revised proposal and accepted trade-offs; each persona gives one final reaction using the same profile and full discussion history. First-vs-final comparison table, plus an optional AI comparison that suggests claims to check with real stakeholders. |
| Debrief | Tab 📝: notes for the memo (most influential exchange, unresolved disagreement, assumption to investigate, claim to verify, did the simulation change your decision). Export the full transcript as Markdown. |

## Deploy to Streamlit Community Cloud

1. **Create a GitHub repo** (public or private) and push these files:
   ```bash
   cd linden-stakeholder-sim
   git init && git add . && git commit -m "Linden stakeholder simulation"
   git branch -M main
   git remote add origin https://github.com/<your-user>/linden-stakeholder-sim.git
   git push -u origin main
   ```
   (Or on github.com: *New repository* → *uploading an existing file* → drag in the contents of
   this folder, including the `sim/` and `.streamlit/` folders.)
2. Go to **https://share.streamlit.io** → *Create app* → *Deploy a public app from GitHub*.
3. Pick your repo, branch `main`, main file **`streamlit_app.py`**.
4. Open **Advanced settings → Secrets** and paste:
   ```toml
   OPENROUTER_API_KEY = "sk-or-v1-..."
   ```
   (Optional: `OPENROUTER_MODEL = "anthropic/claude-haiku-5.5"` to change the default model.)
5. Click **Deploy**. Secrets can be edited later under the app's *Settings → Secrets*.

Get an OpenRouter key at https://openrouter.ai/keys and add a few dollars of credit.

## Run locally

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then paste your key
streamlit run streamlit_app.py
```
Without a key the app starts in **demo mode** (placeholder replies) so you can try the flow.

## Tips

- **Cost:** a full run is about 20–25 model calls. With Claude Sonnet 5.5 that is typically well
  under one US dollar; Claude Haiku 5.5 or GPT-6 Luna are much cheaper. Check current prices on
  OpenRouter.
- **Use one model for the whole run** so the comparison between steps is fair.
- **Save your work:** Streamlit Cloud forgets a session on page reload. Use *Download session
  (.json)* in the sidebar and *Restore a saved session* to continue later.
- **See the exact prompts:** Tab ② has an expander showing what a persona receives – useful for
  the debrief question "did the simulation change your decision or repeat our assumptions?"
- **Changing personas or the case:** edit `sim/personas.py` or `sim/case.py` *before* a run,
  then keep them fixed for the exercise.

## Files

```
streamlit_app.py          the app (tabs for steps 1–4 + debrief/export)
sim/case.py               shared case facts + original proposal (fixed)
sim/personas.py           the five four-layer persona profiles (fixed)
sim/prompts.py            prompt templates and reply parsing
sim/llm.py                OpenRouter client (one request per persona, run in parallel)
.streamlit/config.toml    theme
.streamlit/secrets.toml.example   template for the OPENROUTER_API_KEY secret
```
