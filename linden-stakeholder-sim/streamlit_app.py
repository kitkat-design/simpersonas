"""Linden Compute – AI stakeholder simulation (AI Driven Decision Making, Session 3).

Run locally:   streamlit run streamlit_app.py
Secrets:       OPENROUTER_API_KEY (required for real runs), OPENROUTER_MODEL (optional)
"""

from __future__ import annotations

import datetime as dt
import json

import streamlit as st

from sim import prompts
from sim.case import CASE_FACTS, CASE_TITLE, ORIGINAL_PROPOSAL
from sim.llm import LLMClient
from sim.personas import PERSONA_ORDER, PERSONAS

st.set_page_config(page_title="Linden Stakeholder Simulation", page_icon="🏗️", layout="wide")

MAX_EXCHANGES = 2
MODEL_OPTIONS = {
    "anthropic/claude-sonnet-5.5": "Claude Sonnet 5.5 (recommended)",
    "anthropic/claude-haiku-5.5": "Claude Haiku 5.5 (cheapest, fast)",
    "openai/gpt-6-luna": "GPT-6 Luna (cheap)",
    "google/gemini-3.8-flash": "Gemini 3.8 Flash",
    "__custom__": "Custom model id…",
}
DEBRIEF_FIELDS = {
    "db_influential": "Exchange that most influenced you (and why)",
    "db_disagreement": "One unresolved disagreement",
    "db_assumption": "One assumption to investigate",
    "db_claim": "A claim you would check with real stakeholders",
    "db_changed": "Did the simulation change your decision, or mainly repeat your own assumptions?",
}
STATE_DEFAULTS = {
    "predictions_locked": False,
    "predictions": {},
    "first": {},
    "first_errors": {},
    "exchanges": [],
    "final": {},
    "final_errors": {},
    "final_revised": "",
    "final_tradeoffs": "",
    "analysis": "",
    "log": [],
}


# ------------------------------------------------------------------ helpers
def init_state() -> None:
    for k, v in STATE_DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = json.loads(json.dumps(v))


def secret(name: str, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:  # noqa: BLE001 - no secrets file locally
        return default


def reflow(text: str) -> str:
    """Turn the hard-wrapped plain-text case/profile into readable markdown."""
    blocks: list[str] = []
    cur: int | None = None
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            blocks.append("")
            cur = None
            continue
        if s.isupper() and len(s) < 60:
            blocks.append(f"\n**{s.title()}**")
            cur = None
            continue
        if s.startswith("- "):
            blocks.append(s)
            cur = len(blocks) - 1
            continue
        if cur is not None and (raw.startswith("  ") or not blocks[cur].startswith("- ")):
            blocks[cur] += " " + s
            continue
        blocks.append(s)
        cur = len(blocks) - 1
    md = "\n".join(blocks).replace("$", "\\$")
    return md.replace("[Assumption]", ":orange-background[Assumption]")


def name(pid: str) -> str:
    return PERSONAS[pid]["name"]


def log(step: str, model: str) -> None:
    st.session_state.log.append({"step": step, "model": model,
                                 "time": dt.datetime.now().isoformat(timespec="seconds")})


def render_reply(text: str, fields: list[str], limit: int | None = None) -> None:
    parsed = prompts.parse_fields(text, fields)
    if any(parsed.values()):
        for f in fields:
            if parsed[f]:
                st.markdown(f"**{f}:** {parsed[f]}")
    else:
        st.markdown(text)
    if limit:
        wc = prompts.word_count(text)
        colour = "green" if wc <= limit else "red"
        st.caption(f":{colour}[{wc} words] (limit {limit})")


def persona_header(pid: str) -> None:
    p = PERSONAS[pid]
    st.markdown(f"#### {p['icon']} {p['name']}")
    st.caption(p["role"])


def run_jobs(client: LLMClient, jobs: dict[str, tuple[str, str]], label: str):
    with st.spinner(f"{label} – {len(jobs)} separate AI call(s) running in parallel…"):
        return client.map(jobs)


def split_results(results):
    ok = {k: v for k, v in results.items() if isinstance(v, str)}
    err = {k: str(v) for k, v in results.items() if not isinstance(v, str)}
    return ok, err


def comparison_rows() -> list[dict]:
    rows = []
    for pid in PERSONA_ORDER:
        first = prompts.parse_fields(st.session_state.first.get(pid, ""), prompts.FIRST_FIELDS)
        final = prompts.parse_fields(st.session_state.final.get(pid, ""), prompts.FINAL_FIELDS)
        rows.append({
            "Persona": name(pid),
            "Your prediction": st.session_state.predictions.get(pid, "") or "—",
            "First position": first["Position"] or "—",
            "Final position": final["Position"] or "—",
            "Change since first reaction": final["Change since first reaction"] or "—",
        })
    return rows


def md_table(rows: list[dict]) -> str:
    if not rows:
        return ""
    cols = list(rows[0])
    esc = lambda s: str(s).replace("|", "\\|").replace("\n", " ")  # noqa: E731
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(esc(r[c]) for c in cols) + " |" for r in rows]
    return "\n".join(out)


def build_markdown() -> str:
    s = st.session_state
    lines = [f"# {CASE_TITLE} – AI stakeholder simulation transcript",
             f"_Exported {dt.datetime.now():%Y-%m-%d %H:%M}_", ""]
    if s.log:
        models = sorted({e['model'] for e in s.log})
        lines += [f"Model(s) used: {', '.join(models)}", ""]
    lines += ["## Step 1 – Personas", ""]
    for pid in PERSONA_ORDER:
        p = PERSONAS[pid]
        lines += [f"### {p['name']} – {p['role']}", "", p["profile"].strip(), ""]
    lines += ["## Original proposal", "", ORIGINAL_PROPOSAL.strip(), ""]
    lines += ["## Step 2 – Predictions (made before using AI)", ""]
    for pid in PERSONA_ORDER:
        lines.append(f"- **{name(pid)}:** {s.predictions.get(pid, '') or '—'}")
    lines += ["", "## Step 2 – First reactions (independent AI calls)", ""]
    for pid in PERSONA_ORDER:
        lines += [f"### {name(pid)}", "", s.first.get(pid, "—").strip(), ""]
    lines += ["## Step 3 – Discussion", ""]
    if not s.exchanges:
        lines += ["_Not run._", ""]
    for i, ex in enumerate(s.exchanges, 1):
        lines += [f"### Exchange {i}", ""]
        if ex.get("question"):
            lines += [f"_Clarifying question from the executive team:_ {ex['question']}", ""]
        for pid in PERSONA_ORDER:
            lines += [f"**{name(pid)}**", "", ex["replies"].get(pid, "—").strip(), ""]
    lines += ["## Step 4 – Revised proposal", "", s.final_revised.strip() or "_Not written._", "",
              "### Trade-offs accepted", "", s.final_tradeoffs.strip() or "—", "",
              "### Final reactions", ""]
    for pid in PERSONA_ORDER:
        lines += [f"#### {name(pid)}", "", s.final.get(pid, "—").strip(), ""]
    if s.final:
        lines += ["### First vs final", "", md_table(comparison_rows()), ""]
    if s.analysis:
        lines += ["## AI comparison (assistant's suggestion, not the team's conclusion)", "",
                  s.analysis.strip(), ""]
    lines += ["## Debrief notes (executive team)", ""]
    for key, label in DEBRIEF_FIELDS.items():
        lines += [f"**{label}**", "", s.get(key, "") or "—", ""]
    return "\n".join(lines)


def export_json() -> str:
    s = st.session_state
    data = {k: s[k] for k in STATE_DEFAULTS}
    data["widgets"] = {k: s.get(k, "") for k in
                       list(DEBRIEF_FIELDS) + ["revised_text", "tradeoffs_text"]
                       + [f"pred_{pid}" for pid in PERSONA_ORDER]}
    data["exported"] = dt.datetime.now().isoformat(timespec="seconds")
    return json.dumps(data, indent=2, ensure_ascii=False)


def import_json(raw: bytes) -> None:
    data = json.loads(raw)
    for k in STATE_DEFAULTS:
        if k in data:
            st.session_state[k] = data[k]
    for k, v in data.get("widgets", {}).items():
        st.session_state[k] = v


# ------------------------------------------------------------------ app
init_state()
S = st.session_state

# ---- sidebar: settings -----------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    secret_key = secret("OPENROUTER_API_KEY")
    if secret_key:
        st.success("OpenRouter key loaded from secrets.")
        api_key = secret_key
    else:
        st.info("No OPENROUTER_API_KEY secret found.")
        api_key = st.text_input("OpenRouter API key (not stored)", type="password")

    default_model = secret("OPENROUTER_MODEL", "anthropic/claude-sonnet-5.5")
    keys = list(MODEL_OPTIONS)
    if default_model not in MODEL_OPTIONS:
        keys.insert(0, default_model)
    choice = st.selectbox("Model", keys, index=0 if default_model not in MODEL_OPTIONS
                          else keys.index(default_model),
                          format_func=lambda k: MODEL_OPTIONS.get(k, k))
    model = st.text_input("OpenRouter model id", "anthropic/claude-opus-5.5") \
        if choice == "__custom__" else choice
    st.caption("Use the same model for the whole exercise so results are comparable.")

    set_temp = st.checkbox("Set temperature", value=False,
                           help="Some models ignore this. Off = the model's default.")
    temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.1) if set_temp else None
    demo = st.toggle("Demo mode (no API calls)", value=not bool(api_key),
                     help="Fills replies with placeholders so you can try the flow for free.")

    st.divider()
    st.subheader("💾 Save / restore")
    st.download_button("Download session (.json)", export_json(),
                       file_name="linden_simulation_session.json", mime="application/json")
    up = st.file_uploader("Restore a saved session", type="json")
    if up is not None and st.button("Restore this session"):
        import_json(up.getvalue())
        st.rerun()
    if st.button("🗑️ Reset everything"):
        for k in list(S.keys()):
            del S[k]
        st.rerun()
    st.caption("Streamlit Cloud forgets a session when the page is reloaded – "
               "download the .json to keep your work.")

client = LLMClient(api_key, model, demo=demo, temperature=temperature)

# ---- header -------------------------------------------------------------------
st.title("🏗️ Linden Compute – Stakeholder Simulation")
st.markdown(
    "Five AI personas react to Linden Compute's data-centre proposal. **Each persona is a "
    "separate AI call** that sees only the shared case facts, the proposal and its *own* "
    "profile. You remain the executive team and make the final recommendation."
)
if demo:
    st.warning("Demo mode is on – replies are placeholders. Turn it off in the sidebar for a "
               "real run.", icon="🧪")

done_first = len(S.first) == len(PERSONA_ORDER)
tabs = st.tabs(["① Personas", "② First reactions", "③ Discussion",
                "④ Revised proposal", "📝 Debrief & export"])

# ---- 1. personas ----------------------------------------------------------------
with tabs[0]:
    st.subheader("Step 1 – The five personas")
    st.caption("Four layers per profile: interests · history with the company · personality "
               "and behaviour · power and relationships, plus what could change the position. "
               ":orange-background[Assumption] marks the team's additions. Profiles and case "
               "facts are fixed during the exercise (edit `sim/personas.py` to change them).")
    with st.expander("Shared case facts (given to every persona)"):
        st.markdown(reflow(CASE_FACTS))
    with st.expander("Original proposal", expanded=True):
        st.markdown(reflow(ORIGINAL_PROPOSAL))
    cols = st.columns(2)
    for i, pid in enumerate(PERSONA_ORDER):
        with cols[i % 2]:
            with st.container(border=True):
                persona_header(pid)
                with st.expander("Profile"):
                    st.markdown(reflow(PERSONAS[pid]["profile"]))

# ---- 2. first reactions -----------------------------------------------------------
with tabs[1]:
    st.subheader("Step 2 – Simulate first reactions")
    st.markdown("**2a. Predict first.** Before using AI, write what you expect each person to "
                "say. Your predictions are locked before the AI runs.")
    pcols = st.columns(2)
    for i, pid in enumerate(PERSONA_ORDER):
        with pcols[i % 2]:
            st.text_area(f"{PERSONAS[pid]['icon']} {name(pid)} – your prediction",
                         key=f"pred_{pid}", height=90, disabled=S.predictions_locked,
                         placeholder="Position, main concern…")
    if not S.predictions_locked:
        if st.button("🔒 Lock predictions", type="primary"):
            S.predictions = {pid: S.get(f"pred_{pid}", "") for pid in PERSONA_ORDER}
            S.predictions_locked = True
            st.rerun()
    else:
        st.success("Predictions locked.")

    st.markdown("**2b. Collect independent first reactions.** Five separate calls, run at the "
                "same time; no persona sees another reply. Each reply: position, concern, "
                "condition for reconsidering, next action – under 100 words.")
    with st.expander("🔍 See the exact prompt a persona receives"):
        ppid = st.selectbox("Persona", PERSONA_ORDER, format_func=name, key="prompt_view")
        st.code(prompts.system_prompt(ppid), language=None)
        st.code(prompts.first_reaction_prompt(ORIGINAL_PROPOSAL), language=None)

    c1, c2 = st.columns([1, 1])
    run_first = c1.button("▶️ Run first reactions", type="primary",
                          disabled=not S.predictions_locked or bool(S.first and not S.first_errors),
                          help=None if S.predictions_locked else "Lock your predictions first.")
    retry_first = c2.button("↻ Retry failed personas", disabled=not S.first_errors)
    if run_first or retry_first:
        targets = list(S.first_errors) if retry_first else PERSONA_ORDER
        jobs = {pid: (prompts.system_prompt(pid), prompts.first_reaction_prompt(ORIGINAL_PROPOSAL))
                for pid in targets}
        ok, err = split_results(run_jobs(client, jobs, "Collecting first reactions"))
        S.first.update(ok)
        S.first_errors = err
        log("first reactions", "demo" if demo else model)
        st.rerun()

    for pid, msg in S.first_errors.items():
        st.error(f"{name(pid)}: {msg}")
    if S.first:
        cols = st.columns(2)
        for i, pid in enumerate([p for p in PERSONA_ORDER if p in S.first]):
            with cols[i % 2]:
                with st.container(border=True):
                    persona_header(pid)
                    render_reply(S.first[pid], prompts.FIRST_FIELDS, limit=100)
        if done_first:
            st.markdown("**Prediction vs AI first reaction**")
            st.table([{"Persona": name(pid),
                       "Your prediction": S.predictions.get(pid, "") or "—",
                       "AI position": prompts.parse_fields(S.first[pid], prompts.FIRST_FIELDS)
                       ["Position"] or "—"} for pid in PERSONA_ORDER])

# ---- 3. discussion ---------------------------------------------------------------
with tabs[2]:
    st.subheader("Step 3 – Short discussion")
    st.markdown("Up to two exchanges. All first reactions are shared; each persona responds "
                "to a **specific point made by someone else** and explains any change in "
                "position. Each exchange uses the completed previous exchange as context. "
                "The proposal stays unchanged; you may add one clarifying question per exchange.")
    if not done_first:
        st.info("Complete Step 2 first.")
    for i, ex in enumerate(S.exchanges, 1):
        st.markdown(f"### Exchange {i}")
        if ex.get("question"):
            st.markdown(f"*Your clarifying question:* {ex['question']}")
        for pid, msg in ex.get("errors", {}).items():
            st.error(f"{name(pid)}: {msg}")
        fields = list(prompts.DISCUSSION_FIELDS)
        if ex.get("question"):
            fields.insert(2, "Answer to question")
        cols = st.columns(2)
        for j, pid in enumerate([p for p in PERSONA_ORDER if p in ex["replies"]]):
            with cols[j % 2]:
                with st.container(border=True):
                    persona_header(pid)
                    render_reply(ex["replies"][pid], fields, limit=120)

    last_incomplete = bool(S.exchanges and S.exchanges[-1].get("errors"))
    if done_first and S.exchanges:
        c1, c2 = st.columns(2)
        if last_incomplete and c1.button("↻ Retry failed personas in last exchange"):
            ex = S.exchanges[-1]
            previous = S.exchanges[:-1]
            jobs = {pid: (prompts.system_prompt(pid),
                          prompts.discussion_prompt(pid, ORIGINAL_PROPOSAL, S.first, previous,
                                                    len(S.exchanges), ex.get("question", "")))
                    for pid in ex["errors"]}
            ok, err = split_results(run_jobs(client, jobs, "Retrying"))
            ex["replies"].update(ok)
            ex["errors"] = err
            st.rerun()
        if c2.button("Discard last exchange"):
            S.exchanges.pop()
            st.rerun()

    if done_first and len(S.exchanges) < MAX_EXCHANGES and not last_incomplete:
        n = len(S.exchanges) + 1
        st.markdown(f"### Run exchange {n}")
        q = st.text_input("Optional clarifying question to all personas (proposal stays "
                          "unchanged)", key=f"q_ex{n}")
        if st.button(f"▶️ Run exchange {n}", type="primary"):
            jobs = {pid: (prompts.system_prompt(pid),
                          prompts.discussion_prompt(pid, ORIGINAL_PROPOSAL, S.first,
                                                    S.exchanges, n, q))
                    for pid in PERSONA_ORDER}
            ok, err = split_results(run_jobs(client, jobs, f"Running exchange {n}"))
            S.exchanges.append({"question": q.strip(), "replies": ok, "errors": err})
            log(f"exchange {n}", "demo" if demo else model)
            st.rerun()
    elif len(S.exchanges) >= MAX_EXCHANGES:
        st.success("Both exchanges complete. Move on to Step 4.")

# ---- 4. revised proposal ---------------------------------------------------------
with tabs[3]:
    st.subheader("Step 4 – Revise the proposal")
    st.markdown("As the executive team, write the revised proposal and the trade-offs you "
                "accept. You can change scale, timing, spending commitments or how Linden works "
                "with these stakeholders – explain the business consequences. Each persona then "
                "gives one final reaction using the same profile and the full discussion history.")
    if not done_first:
        st.info("Complete Step 2 first (Step 3 is strongly recommended).")
    st.text_area("Revised proposal", key="revised_text", height=220,
                 placeholder="e.g. Phase 1: … MW, committed only after … ; Phase 2 gated on …")
    st.text_area("Trade-offs you accept (and their business consequences)", key="tradeoffs_text",
                 height=140)
    revised = S.get("revised_text", "")
    tradeoffs = S.get("tradeoffs_text", "")
    if S.final and (revised != S.final_revised or tradeoffs != S.final_tradeoffs):
        st.warning("The text above differs from the version the personas reacted to. "
                   "Re-run to collect reactions to the new version.")
    c1, c2 = st.columns(2)
    run_final = c1.button("▶️ Collect final reactions", type="primary",
                          disabled=not done_first or not revised.strip())
    retry_final = c2.button("↻ Retry failed personas", key="retry_final",
                            disabled=not S.final_errors)
    if run_final or retry_final:
        if run_final:
            S.final, S.analysis = {}, ""
            S.final_revised, S.final_tradeoffs = revised, tradeoffs
        targets = list(S.final_errors) if retry_final else PERSONA_ORDER
        jobs = {pid: (prompts.system_prompt(pid),
                      prompts.final_prompt(pid, ORIGINAL_PROPOSAL, S.final_revised,
                                           S.final_tradeoffs, S.first, S.exchanges))
                for pid in targets}
        ok, err = split_results(run_jobs(client, jobs, "Collecting final reactions"))
        S.final.update(ok)
        S.final_errors = err
        log("final reactions", "demo" if demo else model)
        st.rerun()

    for pid, msg in S.final_errors.items():
        st.error(f"{name(pid)}: {msg}")
    if S.final:
        cols = st.columns(2)
        for i, pid in enumerate([p for p in PERSONA_ORDER if p in S.final]):
            with cols[i % 2]:
                with st.container(border=True):
                    persona_header(pid)
                    render_reply(S.final[pid], prompts.FINAL_FIELDS, limit=100)
        st.markdown("### First vs final reactions")
        st.table(comparison_rows())

        st.markdown("### Optional: AI comparison")
        st.caption("A neutral assistant compares first and final reactions and suggests claims "
                   "to check with real stakeholders. Treat it as a prompt for your own "
                   "judgement, not as your conclusion.")
        if st.button("Generate comparison", disabled=len(S.final) < len(PERSONA_ORDER)):
            with st.spinner("Comparing…"):
                try:
                    S.analysis = client.chat(prompts.ANALYST_SYSTEM, prompts.analyst_prompt(
                        ORIGINAL_PROPOSAL, S.final_revised, S.first, S.exchanges, S.final))
                    log("comparison", "demo" if demo else model)
                except Exception as e:  # noqa: BLE001
                    st.error(str(e))
            st.rerun()
        if S.analysis:
            with st.container(border=True):
                st.markdown(S.analysis)

# ---- 5. debrief & export ----------------------------------------------------------
with tabs[4]:
    st.subheader("Debrief notes & export")
    st.markdown("Notes for your one-page decision memo. They are included in the export.")
    if S.exchanges:
        st.caption("Exchanges you can cite: " + ", ".join(
            f"Exchange {i}" for i in range(1, len(S.exchanges) + 1)))
    for key, label in DEBRIEF_FIELDS.items():
        st.text_area(label, key=key, height=90)
    st.divider()
    md = build_markdown()
    c1, c2 = st.columns(2)
    c1.download_button("⬇️ Download full transcript (.md)", md,
                       file_name="linden_simulation_transcript.md", mime="text/markdown")
    c2.download_button("⬇️ Download session (.json)", export_json(),
                       file_name="linden_simulation_session.json", mime="application/json", key="json_main")
    with st.expander("Preview transcript"):
        st.markdown(md)
