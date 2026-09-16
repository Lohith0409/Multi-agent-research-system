import streamlit as st
import time
from agents import run_search, run_reader, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Simple, clean CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #e8e8eb;
}

.stApp {
    background: #0f1117;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 3rem 4rem; max-width: 980px; }

/* ── Header ── */
.header {
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #23262f;
    margin-bottom: 2rem;
}
.header .tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #5b8def;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.header h1 {
    font-size: 2.1rem;
    font-weight: 700;
    color: #f2f3f5;
    margin: 0 0 0.4rem;
    letter-spacing: -0.02em;
}
.header p {
    color: #8b8f9c;
    font-size: 0.95rem;
    margin: 0;
    max-width: 560px;
    line-height: 1.5;
}

/* ── Inputs ── */
.stTextInput > label {
    font-size: 0.8rem !important;
    color: #b0b3bd !important;
    font-weight: 500 !important;
}
.stTextInput > div > div > input {
    background: #171a21 !important;
    border: 1px solid #2a2d38 !important;
    border-radius: 8px !important;
    color: #f2f3f5 !important;
    padding: 0.65rem 0.9rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #5b8def !important;
    box-shadow: 0 0 0 2px rgba(91,141,239,0.15) !important;
}

.stButton > button {
    background: #5b8def !important;
    color: #fff !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.65rem 1.5rem !important;
    transition: background 0.15s !important;
}
.stButton > button:hover {
    background: #4a7bdc !important;
}

/* ── Pipeline steps: simple horizontal row ── */
.pipeline-row {
    display: flex;
    gap: 0.75rem;
    margin: 1.5rem 0 2rem;
}
.step-chip {
    flex: 1;
    background: #171a21;
    border: 1px solid #23262f;
    border-radius: 8px;
    padding: 0.75rem 0.9rem;
    text-align: left;
}
.step-chip.running {
    border-color: #5b8def;
    background: #171d2b;
}
.step-chip.done {
    border-color: #34a870;
    background: #131d18;
}
.step-chip .step-title {
    font-size: 0.82rem;
    font-weight: 600;
    color: #f2f3f5;
    margin-bottom: 0.2rem;
}
.step-chip .step-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.05em;
    color: #5c6070;
}
.step-chip.running .step-status { color: #5b8def; }
.step-chip.done .step-status { color: #34a870; }

/* ── Section labels ── */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #5c6070;
    margin: 2rem 0 0.75rem;
}

/* ── Result panels ── */
.panel {
    background: #171a21;
    border: 1px solid #23262f;
    border-radius: 10px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1rem;
}
.panel.report { border-left: 3px solid #5b8def; }
.panel.critic { border-left: 3px solid #34a870; }
.panel-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #f2f3f5;
    margin-bottom: 1rem;
}
.result-text {
    font-size: 0.9rem;
    line-height: 1.7;
    color: #c4c7d0;
    white-space: pre-wrap;
}

/* ── Markdown content (final report & critic feedback) ── */
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: #f2f3f5 !important;
    font-weight: 700 !important;
}
.stMarkdown p, .stMarkdown li {
    color: #d5d7dd !important;
    line-height: 1.7 !important;
}
.stMarkdown strong {
    color: #f2f3f5 !important;
}
.stMarkdown table {
    color: #d5d7dd !important;
}
.stMarkdown th {
    color: #f2f3f5 !important;
    background: #1c1f28 !important;
}
.stMarkdown td {
    color: #d5d7dd !important;
    border-color: #23262f !important;
}

/* Expander */
details summary {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #8b8f9c !important;
}

/* Footer */
.footer-note {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #3d404a;
    text-align: center;
    margin-top: 3rem;
}
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header">
    <div class="tag">Multi-Agent Research System</div>
    <h1>ResearchMind</h1>
    <p>Four agents work together — searching, reading, writing, and critiquing — to produce a research report on any topic.</p>
</div>
""", unsafe_allow_html=True)


# ── Input ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([5, 1.2])
with col1:
    topic = st.text_input(
        "Research topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
        label_visibility="collapsed",
    )
with col2:
    run_btn = st.button("Run Research", use_container_width=True)

st.caption("Try: LLM agents 2025 · CRISPR gene editing · Fusion energy progress")


# ── Pipeline status row ──────────────────────────────────────────────────────
r = st.session_state.results
steps = [("search", "Search"), ("reader", "Reader"), ("writer", "Writer"), ("critic", "Critic")]

def step_state(step):
    if step in r:
        return "done"
    if st.session_state.running:
        for k, _ in steps:
            if k not in r:
                return "running" if k == step else "waiting"
    return "waiting"

chip_html = '<div class="pipeline-row">'
for key, label in steps:
    state = step_state(key)
    status_text = {"waiting": "WAITING", "running": "RUNNING", "done": "DONE"}[state]
    chip_html += f"""
    <div class="step-chip {state}">
        <div class="step-title">{label}</div>
        <div class="step-status">{status_text}</div>
    </div>"""
chip_html += "</div>"
st.markdown(chip_html, unsafe_allow_html=True)


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input

    with st.spinner("Search Agent is working…"):
        results["search"] = run_search(topic_val)
        st.session_state.results = dict(results)

    with st.spinner("Reader Agent is scraping top resources…"):
        results["reader"] = run_reader(results["search"])
        st.session_state.results = dict(results)

    with st.spinner("Writer is drafting the report…"):
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined
        })
        st.session_state.results = dict(results)

    with st.spinner("Critic is reviewing the report…"):
        results["critic"] = critic_chain.invoke({
            "report": results["writer"]
        })
        st.session_state.results = dict(results)

    st.session_state.running = False
    st.session_state.done = True
    st.rerun()


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    if "search" in r:
        with st.expander("Search results (raw)"):
            st.markdown(f'<div class="result-text">{r["search"]}</div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("Scraped content (raw)"):
            st.markdown(f'<div class="result-text">{r["reader"]}</div>', unsafe_allow_html=True)

    if "writer" in r:
        st.markdown('<div class="section-label">Final Report</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel report">', unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.download_button(
            label="Download report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown('<div class="section-label">Critic Feedback</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel critic">', unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown('</div>', unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<div class="footer-note">ResearchMind · LangChain multi-agent pipeline · Streamlit</div>', unsafe_allow_html=True)