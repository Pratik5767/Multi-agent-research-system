import streamlit as st
import time
from src.agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain
from langchain_core.messages import ToolMessage



# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    color: #c9d6cf;
}

.stApp {
    background:
        radial-gradient(ellipse at 50% -10%, rgba(79,209,165,0.09), transparent 45%),
        repeating-linear-gradient(180deg, rgba(255,255,255,0.012) 0px, rgba(255,255,255,0.012) 1px, transparent 1px, transparent 3px),
        #0a0d0b;
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.3rem 3rem 4rem; max-width: 1180px; }

@keyframes blink-dot {
    0%, 100% { opacity: 1; box-shadow: 0 0 6px currentColor; }
    50% { opacity: 0.35; box-shadow: 0 0 2px currentColor; }
}

/* ── System status bar ── */
.sysbar {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    color: #5c6d63;
    padding-bottom: 0.9rem;
    text-transform: uppercase;
}
.sysbar .dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #4fd1a5;
    color: #4fd1a5;
    animation: blink-dot 1.6s infinite ease-in-out;
}
.sysbar .sep { opacity: 0.4; }

/* ── Hero header ── */
.hero {
    padding: 0.4rem 0 1.8rem;
    border-bottom: 1px solid #1e2a23;
    margin-bottom: 2rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 1.5rem;
}
.hero h1 {
    font-family: 'Rajdhani', sans-serif;
    font-size: clamp(2.2rem, 5vw, 3.6rem);
    font-weight: 700;
    letter-spacing: 0.01em;
    line-height: 1;
    color: #eef5f0;
    margin: 0;
    text-transform: uppercase;
}
.hero h1 .brk { color: #3a463e; font-weight: 500; }
.hero h1 span { color: #4fd1a5; }
.hero-sub {
    font-size: 0.82rem;
    font-weight: 400;
    color: #6f7d74;
    max-width: 340px;
    line-height: 1.7;
    text-align: right;
}
.hero-sub b { color: #9fb0a5; }

/* ── Divider ── */
.divider {
    height: 1px;
    background: #1e2a23;
    margin: 2.5rem 0;
}

/* ── Corner-bracket panel mixin ── */
.hud-panel {
    position: relative;
    background: #10140f;
    border: 1px solid #1e2a23;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
}
.hud-panel::before, .hud-panel::after,
.hud-panel .c2::before, .hud-panel .c2::after {
    content: '';
    position: absolute;
    width: 14px; height: 14px;
    border-color: #4fd1a5;
    border-style: solid;
    border-width: 0;
}
.hud-panel::before { top: -1px; left: -1px; border-top-width: 2px; border-left-width: 2px; }
.hud-panel::after { top: -1px; right: -1px; border-top-width: 2px; border-right-width: 2px; }
.hud-panel .c2::before { bottom: -1px; left: -1px; border-bottom-width: 2px; border-left-width: 2px; }
.hud-panel .c2::after { bottom: -1px; right: -1px; border-bottom-width: 2px; border-right-width: 2px; }

/* ── Streamlit input overrides ── */
.stTextInput > div > div > input {
    background: #0a0d0b !important;
    border: 1px solid #263229 !important;
    border-radius: 0px !important;
    color: #eef5f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.92rem !important;
    padding: 0.85rem 1rem !important;
    transition: all 0.15s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: #4fd1a5 !important;
    box-shadow: 0 0 0 1px #4fd1a5, 0 0 16px rgba(79,209,165,0.15) !important;
}
.stTextInput > label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    color: #4fd1a5 !important;
    font-weight: 600 !important;
}
.stTextInput > label::before { content: '> '; }

/* ── Button ── */
.stButton > button {
    background: transparent !important;
    color: #4fd1a5 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase;
    border: 1px solid #4fd1a5 !important;
    border-radius: 0px !important;
    padding: 0.75rem 2.2rem !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    width: 100%;
}
.stButton > button:hover {
    background: rgba(79,209,165,0.1) !important;
    box-shadow: 0 0 18px rgba(79,209,165,0.22) !important;
}
.stButton > button:active {
    background: rgba(79,209,165,0.22) !important;
}

/* ── Pipeline step nodes (timeline) ── */
.pipeline-rail {
    position: relative;
    padding-left: 1.6rem;
}
.pipeline-rail::before {
    content: '';
    position: absolute;
    left: 5px; top: 6px; bottom: 6px;
    width: 1px;
    background: #1e2a23;
}
.step-card {
    position: relative;
    background: #10140f;
    border: 1px solid #1e2a23;
    padding: 0.95rem 1.3rem;
    margin-bottom: 0.75rem;
    margin-left: 1.6rem;
    transition: border-color 0.2s ease, background 0.2s ease;
    overflow: hidden;
}
.step-dot {
    position: absolute;
    left: -1.6rem; top: 50%;
    transform: translateY(-50%);
    width: 9px; height: 9px;
    border-radius: 50%;
    background: #2a3730;
    border: 1px solid #465850;
}
.step-card.active { border-color: #4fd1a5; background: #101a15; animation: card-pulse 1.8s ease-in-out infinite; }
.step-card.active .step-dot { background: #e8a94c; border-color: #e8a94c; animation: blink-dot 1.1s infinite ease-in-out; color: #e8a94c; }
.step-card.done { border-color: #2c4a3b; }
.step-card.done .step-dot { background: #4fd1a5; border-color: #4fd1a5; }

@keyframes card-pulse {
    0%, 100% { box-shadow: 0 0 0 1px rgba(79,209,165,0.18), 0 0 12px rgba(79,209,165,0.06); }
    50% { box-shadow: 0 0 0 1px rgba(79,209,165,0.5), 0 0 26px rgba(79,209,165,0.22); }
}
@keyframes scan-move {
    0% { left: -35%; }
    100% { left: 115%; }
}
.scan-bar {
    position: absolute;
    top: 0; bottom: 0;
    width: 35%;
    background: linear-gradient(90deg, transparent, rgba(79,209,165,0.22), transparent);
    animation: scan-move 1.5s linear infinite;
    pointer-events: none;
}
@keyframes dot-pulse {
    0%, 80%, 100% { opacity: 0.2; }
    40% { opacity: 1; }
}
.dot-anim {
    display: inline-block;
    animation: dot-pulse 1.2s infinite ease-in-out;
}
@keyframes check-pop {
    0% { opacity: 0; transform: scale(0.6); }
    60% { opacity: 1; transform: scale(1.15); }
    100% { opacity: 1; transform: scale(1); }
}
.check-pop { display: inline-block; animation: check-pop 0.35s ease-out; }

.step-header {
    display: flex;
    align-items: baseline;
    gap: 0.7rem;
    margin-bottom: 0.15rem;
    position: relative;
    z-index: 1;
}
.step-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: #5c6d63;
}
.step-card.active .step-num { color: #e8a94c; }
.step-card.done .step-num { color: #4fd1a5; }
.step-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: #eef5f0;
    text-transform: uppercase;
}
.step-status {
    margin-left: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.64rem;
    letter-spacing: 0.1em;
    font-weight: 600;
}
.status-waiting  { color: #465850; }
.status-running  { color: #e8a94c; }
.status-done     { color: #4fd1a5; }
.step-desc {
    font-size: 0.78rem;
    color: #5c6d63;
    margin-top: 0.35rem;
    position: relative;
    z-index: 1;
}

/* ── Result panels ── */
.result-panel {
    background: #0d1210;
    border: 1px solid #1e2a23;
    border-left: 2px solid #4fd1a5;
    padding: 1.4rem 1.6rem;
    margin-top: 0.6rem;
    margin-bottom: 1.2rem;
}
.result-panel-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #4fd1a5;
    margin-bottom: 0.9rem;
}
.result-panel-title::before { content: '$ cat '; color: #465850; }
.result-content {
    font-size: 0.86rem;
    line-height: 1.7;
    color: #a9b8ae;
    white-space: pre-wrap;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Report & feedback panels ── */
.report-panel, .feedback-panel {
    position: relative;
    background: #0d1210;
    border: 1px solid #1e2a23;
    padding: 2rem 2.4rem;
    margin-top: 1rem;
}
.report-panel::before, .report-panel::after,
.feedback-panel::before, .feedback-panel::after {
    content: '';
    position: absolute;
    width: 14px; height: 14px;
    border-style: solid;
    border-width: 0;
}
.report-panel::before { top: -1px; left: -1px; border-top: 2px solid #e8a94c; border-left: 2px solid #e8a94c; }
.report-panel::after { bottom: -1px; right: -1px; border-bottom: 2px solid #e8a94c; border-right: 2px solid #e8a94c; }
.feedback-panel::before { top: -1px; left: -1px; border-top: 2px solid #4fd1a5; border-left: 2px solid #4fd1a5; }
.feedback-panel::after { bottom: -1px; right: -1px; border-bottom: 2px solid #4fd1a5; border-right: 2px solid #4fd1a5; }

.panel-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.panel-label.orange { color: #e8a94c; }
.panel-label.green { color: #4fd1a5; }
.panel-label::before { content: '▸'; }

/* ── Expander ── */
details {
    background: #0d1210;
    border-radius: 0px;
    padding: 0.3rem 0.9rem;
    border: 1px solid #1e2a23;
}
details summary {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.74rem !important;
    font-weight: 600 !important;
    color: #8fa298 !important;
    letter-spacing: 0.08em !important;
    cursor: pointer;
}

/* ── Section heading ── */
.section-heading {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #eef5f0;
    margin: 1.2rem 0 1.1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.section-heading::before {
    content: '';
    width: 8px; height: 8px;
    background: #4fd1a5;
}

/* ── Example chips ── */
.chip {
    background: transparent;
    border: 1px solid #263229;
    border-radius: 0px;
    padding: 0.32rem 0.75rem;
    font-size: 0.72rem;
    color: #7f9186;
    font-family: 'JetBrains Mono', monospace;
    cursor: default;
}

/* ── Toast-style notice ── */
.notice {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #465850;
    text-align: left;
    margin-top: 3rem;
    letter-spacing: 0.04em;
    border-top: 1px solid #1e2a23;
    padding-top: 1rem;
}
.notice::before { content: '$ '; color: #4fd1a5; }
</style>
""", unsafe_allow_html=True)


# ── Helper: build step card HTML ─────────────────────────────────────────────
def step_card_html(num: str, title: str, state: str, desc: str = ""):
    card_cls = {"running": "active", "done": "done"}.get(state, "")

    if state == "running":
        status_html = (
            '<span class="step-status status-running">EXECUTING'
            '<span class="dot-anim">.</span>'
            '<span class="dot-anim" style="animation-delay:0.2s">.</span>'
            '<span class="dot-anim" style="animation-delay:0.4s">.</span>'
            '</span>'
        )
    elif state == "done":
        status_html = '<span class="step-status status-done"><span class="check-pop">✓</span> COMPLETE</span>'
    else:
        status_html = '<span class="step-status status-waiting">STANDBY</span>'

    scan_html = '<div class="scan-bar"></div>' if state == "running" else ""
    desc_html = f"<div class='step-desc'>{desc}</div>" if desc else ""

    return (
        f'<div class="step-card {card_cls}">'
        f'{scan_html}'
        f'<div class="step-dot"></div>'
        f'<div class="step-header">'
        f'<span class="step-num">{num}</span>'
        f'<span class="step-title">{title}</span>'
        f'{status_html}'
        f'</div>'
        f'{desc_html}'
        f'</div>'
    )


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── System status bar ─────────────────────────────────────────────────────────
st.markdown("""
<div class="sysbar">
    <span class="dot"></span> SYSTEM ONLINE
    <span class="sep">//</span> AGENTS: 4 REGISTERED
    <span class="sep">//</span> RUNTIME: LANGCHAIN
</div>
""", unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div>
        <h1><span class="brk">[</span>RESEARCH<span>::AGENT</span><span class="brk">]</span></h1>
    </div>
    <p class="hero-sub">
        <b>4 agents</b> on one pipeline — search, read,
        write, critique — filed as a single report.
    </p>
</div>
""", unsafe_allow_html=True)


# ── Step metadata (num label, title, description) ─────────────────────────────
STEP_META = {
    "search": ("AGENT_01 :: SEARCH", "Search Agent", "Gathers recent web information"),
    "reader": ("AGENT_02 :: READ", "Reader Agent", "Scrapes & extracts deep content"),
    "writer": ("AGENT_03 :: WRITE", "Writer Chain", "Drafts the full research report"),
    "critic": ("AGENT_04 :: CRITIQUE", "Critic Chain", "Reviews & scores the report"),
}


# ── Layout: input left, pipeline right ───────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.4, 4])

with col_input:
    st.markdown('<div class="hud-panel"><div class="c2">', unsafe_allow_html=True)

    topic = st.text_input(
        "Query",
        placeholder="e.g. Roadmap for AGI development in next 5 years",
        key="topic_input",
        label_visibility="visible",
    )

    run_btn = st.button(
        "► Initiate Pipeline",
        use_container_width=True
    )

    st.markdown('</div></div>', unsafe_allow_html=True)

    # Example chips
    st.markdown(
        '<div style="display:flex;gap:0.5rem;flex-wrap:wrap;align-items:center;margin-bottom:1.5rem;">'
        '<span style="font-family:\'JetBrains Mono\',monospace;font-size:0.66rem;color:#465850;letter-spacing:0.1em;">'
        'SAMPLE_QUERIES:'
        '</span>',
        unsafe_allow_html=True
    )

    examples = [
        "Future of LLM in Tech Industry",
        "All Lastest AI Agents in 2026",
        "Roadmap for AGI development in next 5 years",
    ]

    for ex in examples:
        st.markdown(f'<span class="chip">{ex}</span>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

with col_pipeline:
    st.markdown(
        '<div class="section-heading">Agent Pipeline</div>',
        unsafe_allow_html=True
    )

    r = st.session_state.results

    def s(step):
        if not r:
            return "waiting"

        steps = ["search", "reader", "writer", "critic"]

        if step in r:
            return "done"

        if st.session_state.running:
            for k in steps:
                if k not in r:
                    return "running" if k == step else "waiting"

        return "waiting"

    st.markdown('<div class="pipeline-rail">', unsafe_allow_html=True)

    # One persistent placeholder per step, so its content can be updated
    # in place (waiting → running → done) without a full page rerun.
    step_slots = {key: st.empty() for key in STEP_META}

    for key, (num, title, desc) in STEP_META.items():
        step_slots[key].markdown(step_card_html(num, title, s(key), desc), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def set_step_state(step_key: str, state: str):
    """Update a single pipeline box in place (waiting / running / done)."""
    num, title, desc = STEP_META[step_key]
    step_slots[step_key].markdown(step_card_html(num, title, state, desc), unsafe_allow_html=True)


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


    # ── Step 1: Search ──
    set_step_state("search", "running")

    search_agent = build_search_agent()

    sr = search_agent.invoke({
        "messages": [
            ("user",
             f"Find recent, reliable and detailed information about: {topic_val}")
        ]
    })

    tool_output = [
        m.content for m in sr['messages'] if isinstance(m, ToolMessage)
    ]

    results["search"] = "\n\n".join(tool_output) if tool_output else sr["messages"][-1].content
    st.session_state.results = dict(results)
    set_step_state("search", "done")


    # ── Step 2: Reader ──
    set_step_state("reader", "running")

    reader_agent = build_reader_agent()

    rr = reader_agent.invoke({
        "messages": [(
            "user",
            f"Based on the following search results about '{topic_val}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{results['search'][:1500]}"
        )]
    })

    tool_output = [
        m.content for m in rr['messages'] if isinstance(m, ToolMessage)
    ]

    results["reader"] = "\n\n".join(tool_output) if tool_output else rr["messages"][-1].content
    st.session_state.results = dict(results)
    set_step_state("reader", "done")


    # ── Step 3: Writer ──
    set_step_state("writer", "running")

    research_combined = (
        f"SEARCH RESULTS:\n{results['search']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
    )

    results["writer"] = writer_chain.invoke({
        "topic": topic_val,
        "research": research_combined
    })

    st.session_state.results = dict(results)
    set_step_state("writer", "done")


    # ── Step 4: Critic ──
    set_step_state("critic", "running")

    results["critic"] = critic_chain.invoke({
        "report": results["writer"]
    })

    st.session_state.results = dict(results)
    set_step_state("critic", "done")

    st.session_state.running = False
    st.session_state.done = True
    st.rerun()


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="section-heading">Output Log</div>',
        unsafe_allow_html=True
    )

    # Raw outputs
    if "search" in r:
        with st.expander("🔍 Search Results (raw)", expanded=False):
            st.markdown(
                '<div class="result-panel">'
                '<div class="result-panel-title">search_agent.out</div>'
                f'<div class="result-content">{r["search"]}</div>'
                '</div>',
                unsafe_allow_html=True
            )

    if "reader" in r:
        with st.expander("📄 Scraped Content (raw)", expanded=False):

            st.markdown(
                '<div class="result-panel">'
                '<div class="result-panel-title">reader_agent.out</div>'
                f'<div class="result-content">{r["reader"]}</div>'
                '</div>',
                unsafe_allow_html=True
            )

    # Final report
    if "writer" in r:

        st.markdown(
            '<div class="report-panel">'
            '<div class="panel-label orange">Final Research Report</div>',
            unsafe_allow_html=True
        )

        st.markdown(r["writer"])

        st.markdown("</div>", unsafe_allow_html=True)

        # Download button
        st.download_button(
            label="⬇ Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    # Critic feedback
    if "critic" in r:

        st.markdown(
            '<div class="feedback-panel">'
            '<div class="panel-label green">Critic Feedback</div>',
            unsafe_allow_html=True
        )

        st.markdown(r["critic"])

        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    pipeline exited 0 · researchagent · langchain multi-agent runtime
</div>
""", unsafe_allow_html=True)