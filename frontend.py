import streamlit as st
import uuid
from tempbackend import app
from tempbackend import parse_tests_from_string

st.set_page_config(page_title="Automated Legacy Code Translator", layout="wide")

# ------------------------------------------------------------------------------------
# Custom CSS — typography, accent color, and structural refinements only.
# Base colors intentionally left to Streamlit's native light/dark theme switcher.
# ------------------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

/* Typography */
html, body, [data-testid="stApp"] {
    font-family: 'Inter', sans-serif;
}
h1 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1.6rem !important;
    letter-spacing: -0.5px !important;
}
h2, h3 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.2px !important;
}

/* Code blocks — monospace font */
[data-testid="stCode"] code,
[data-testid="stTextArea"] textarea {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12.5px !important;
}

/* Translate button — amber accent */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #f1c40f, #e67e22) !important;
    color: #111 !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    border: none !important;
    border-radius: 6px !important;
    letter-spacing: 0.3px !important;
    transition: box-shadow 0.2s ease, transform 0.15s ease !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    box-shadow: 0 0 24px #f1c40f55 !important;
    transform: translateY(-1px) !important;
}

/* Tabs — amber active indicator */
[data-testid="stTabs"] [aria-selected="true"] {
    color: #e67e22 !important;
    border-bottom-color: #e67e22 !important;
}

/* Sidebar history buttons — left-aligned, subtle */
[data-testid="stSidebar"] .stButton button:not([kind="primary"]) {
    width: 100%;
    text-align: left;
    border-radius: 6px;
    font-size: 13px;
    padding: 7px 12px;
    transition: background 0.15s ease;
}

/* Output section dot labels */
.output-label {
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #94a3b8;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.output-label::before {
    content: '';
    display: inline-block;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #f1c40f;
    flex-shrink: 0;
}

/* Status badge pills */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    font-family: 'Inter', sans-serif;
    margin-bottom: 16px;
}
.status-pass {
    background: #dcfce744;
    border: 1px solid #16a34a66;
    color: #16a34a;
}
.status-fail {
    background: #ffedd544;
    border: 1px solid #ea580c66;
    color: #ea580c;
}

/* Accent divider line */
.accent-divider {
    height: 2px;
    background: linear-gradient(90deg, #f1c40f66, transparent);
    border-radius: 2px;
    margin-bottom: 20px;
}

/* Eyebrow label above main title */
.eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #f1c40f;
    margin-bottom: 2px;
}
</style>
""", unsafe_allow_html=True)

LANGUAGES = ["Python", "C", "C++", "Java", "Fortran", "JavaScript", "Go", "Rust", "C#"]

# File extension:used to prefill the source language when a file is uploaded
EXT_TO_LANG = {
    "py": "Python", "c": "C", "cpp": "C++",
    "java": "Java", "f90": "Fortran", "f": "Fortran",
    "js": "JavaScript", "go": "Go", "rs": "Rust", "cs": "C#",
}

def generate_thread_id():
    return str(uuid.uuid4())


def new_translation_session():
    """Starts a fresh translation thread, same role as clear_chat() in your chatbot."""
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    st.session_state['title'] = "New Translation"
    add_thread(thread_id, st.session_state['title'])
    st.session_state['source_code'] = ""
    st.session_state['translated_code'] = ""
    st.session_state['tests'] = []
    st.session_state['errors_fixes'] = []  # placeholder: will hold RAG-retrieved (error, fix) pairs
    st.session_state['legacy_output'] = ""
    st.session_state['translated_output'] = ""


def add_thread(thread_id, title="New Translation"):
    if thread_id not in st.session_state['translation_threads']:
        st.session_state['translation_threads'][thread_id] = {
            "title": title,
            "source_lang": None,
            "target_lang": None,
            "source_code": "",
            "translated_code": "",
            "legacy_output": "",
            "translated_output": ""
        }


def load_translation(thread_id):
    """
    TODO: once LangGraph persistence (MemorySaver / PostgresStore) is wired in,
    swap this for something like:

        res = app.get_state(config={"configurable": {"thread_id": thread_id}})
        return res.values

    For now it just reads back from in-memory session state (lost on refresh,
    same limitation your chatbot would have without a real checkpointer).
    """
    return st.session_state['translation_threads'].get(thread_id, {})


def translate_code(code, source_lang, target_lang, thread_id, tests=[]) -> dict:
    result = app.invoke(
        {
            "input_code": code,
            "inp_lang": source_lang.lower(),
            "target_lang": target_lang.lower(),
            "legacy_output": "",
            "translated_output": "",
            "retrieved_context": [],    # NEW
            "error_snippet": "",        # NEW
            "last_feedback": [],        # NEW
        },
        config={
            "configurable": {
                "thread_id": thread_id,
                "provider": "groq",
                # "model_id": "llama-3.3-70b-versatile",
                "model_id": "openai/gpt-oss-120b",
                # "model_id":"qwen/qwen3.6-27b",
                # "model_id": "llama-3.1-8b-instant",
                "tests": tests,   # placeholder until UI supports test input
            }
        }
    )
    print(result)
    # TODO: also pull result["retrieved_pairs"] here once RAG is in
    return result


# ------------------------------------------------------------------------------------
# Session state init
# ------------------------------------------------------------------------------------
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'title' not in st.session_state:
    st.session_state['title'] = "New Translation"

if 'translation_threads' not in st.session_state:
    st.session_state['translation_threads'] = {}

if 'source_code' not in st.session_state:
    st.session_state['source_code'] = ""

if 'translated_code' not in st.session_state:
    st.session_state['translated_code'] = ""

if 'last_uploaded_name' not in st.session_state:
    st.session_state['last_uploaded_name'] = None

if 'errors_fixes' not in st.session_state:
    st.session_state['errors_fixes'] = []  # placeholder for RAG-retrieved error/fix pairs

if 'tests' not in st.session_state:
    st.session_state['tests'] = []

if 'attempt_count' not in st.session_state:
    st.session_state['attempt_count'] = 0

if 'passed' not in st.session_state:
    st.session_state['passed'] = None

if 'legacy_output' not in st.session_state:
    st.session_state['legacy_output'] = ""

if 'translated_output' not in st.session_state:
    st.session_state['translated_output'] = ""

add_thread(st.session_state['thread_id'], st.session_state['title'])

# ------------------------------------------------------------------------------------
# Sidebar UI
# ------------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("#### 🔬 BMP Translator")
    st.markdown("<div style='height:2px;background:linear-gradient(90deg,#f1c40f,transparent);border-radius:2px;margin-bottom:20px'></div>", unsafe_allow_html=True)

    if st.button("➕ New Translation", type="primary", use_container_width=True):
        new_translation_session()
        st.rerun()

    st.markdown("<div style='margin-top:20px;margin-bottom:6px;font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:#94a3b8;font-family:Inter,sans-serif'>History</div>", unsafe_allow_html=True)

    for thid, info in reversed(list(st.session_state['translation_threads'].items())):
        label = info.get("title", "New Translation")
        if st.button(str(label), key=thid, use_container_width=True):
            st.session_state['thread_id'] = thid
            loaded = load_translation(thid)
            st.session_state['title'] = loaded.get("title", "New Translation")
            st.session_state['source_code'] = loaded.get("source_code", "")
            st.session_state['translated_code'] = loaded.get("translated_code", "")
            st.rerun()

# ------------------------------------------------------------------------------------
# Main header
# ------------------------------------------------------------------------------------
st.markdown("<div class='eyebrow'>Automated Legacy Code</div>", unsafe_allow_html=True)
st.title("Translator & Executor")
st.markdown("<div class='accent-divider'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------------
# Language selection
# ------------------------------------------------------------------------------------
lang_slot = st.container()
tab_slot = st.container()

with tab_slot:
    # Input: either Write code or upload file
    input_tab, upload_tab = st.tabs(["✍️  Paste code", "📁  Upload file"])

    with input_tab:
        pasted_code = st.text_area(
            "Write or paste your code here",
            value=st.session_state['source_code'],
            height=300,
            key="pasted_code_area",
            placeholder="// paste your legacy code here...",
        )

    with upload_tab:
        uploaded_file = st.file_uploader(
            "Drop a code file",
            type=list(EXT_TO_LANG.keys()),
        )
        uploaded_test_file = st.file_uploader(
            "Drop a test file",
            type=".txt"
        )
        uploaded_test = None
        if uploaded_test_file is not None:
            uploaded_test = uploaded_test_file.read().decode("utf-8")
            st.session_state['tests'] = parse_tests_from_string(uploaded_test)
            st.caption(f"✅ {len(st.session_state['tests'])} test case(s) loaded")
        uploaded_code = None
        if uploaded_file is not None:
            uploaded_code = uploaded_file.read().decode("utf-8")
            ext = uploaded_file.name.split(".")[-1].lower()
            guessed_lang = EXT_TO_LANG.get(ext)
            if guessed_lang and st.session_state.get('last_uploaded_name') != uploaded_file.name:
                st.session_state['last_uploaded_name'] = uploaded_file.name
                st.session_state['source_lang_select'] = guessed_lang
                st.caption(f"Detected source language from extension: **{guessed_lang}** "
                           f"(adjust the dropdown above if this is wrong)")
                st.rerun()  #st.session_state values absolutely persist when you call st.rerun()
            st.code(uploaded_code, language=ext if ext != "f90" else "fortran")

#plus both selectboxes inside it. This code runs after the upload detection, but visually
# it still appears above the tabs because lang_slot was created first cuz we created containers
#in that order
with lang_slot:
    col_lang1, col_arrow, col_lang2 = st.columns([5, 1, 5])
    with col_lang1:
        source_lang = st.selectbox("Source language", LANGUAGES, key="source_lang_select")
    with col_arrow:
        st.markdown("<div style='text-align:center;padding-top:30px;font-size:20px;color:#f1c40f'>→</div>", unsafe_allow_html=True)
    with col_lang2:
        target_lang = st.selectbox("Target language", LANGUAGES, index=1, key="target_lang_select")

#uploaded file takes priority if both inputs are filled
active_code = uploaded_code if (uploaded_file is not None and uploaded_code) else pasted_code

# ------------------------------------------------------------------------------------
# Translate action
# ------------------------------------------------------------------------------------
st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
translate_clicked = st.button("⟳  Translate", type="primary", disabled=not active_code.strip())

if translate_clicked:
    st.session_state['source_code'] = active_code

    with st.spinner("Translating..."):
        # TODO: swap for st.write_stream(...) once the LangGraph app streams tokens,
        # the same way your chatbot does with stream_mode="messages"
        result = translate_code(
            active_code, source_lang, target_lang, st.session_state['thread_id'], st.session_state['tests']
        )
        st.session_state['translated_code'] = result["translated_code"]
        st.session_state['attempt_count'] = result["attempt_count"]
        st.session_state['passed'] = result["passed"]
        st.session_state['legacy_output'] = result["legacy_output"]
        st.session_state['translated_output'] = result["translated_output"]

    title = f"{source_lang} → {target_lang}"
    st.session_state['title'] = title
    st.session_state['translation_threads'][st.session_state['thread_id']] = {
        "title": title,
        "source_lang": source_lang,
        "target_lang": target_lang,
        "source_code": active_code,
        "translated_code": st.session_state['translated_code'],
        "tests": st.session_state['tests'],
        "attempt_count": st.session_state["attempt_count"],
        "passed": st.session_state['passed']
    }
    st.rerun()

# ------------------------------------------------------------------------------------
# Results section
# ------------------------------------------------------------------------------------
if st.session_state['translated_code']:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # Status badge
    attempts = st.session_state['attempt_count']
    if st.session_state["passed"]:
        st.markdown(f"""<span class='status-badge status-pass'>
            ✓ Passed in {attempts} correction attempt{'s' if attempts != 1 else ''}
        </span>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<span class='status-badge status-fail'>
            ⚠ Max attempts reached ({attempts}) — translation may have issues
        </span>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Code panels
    out_col1, out_col2 = st.columns(2)
    with out_col1:
        st.markdown(f"<div class='output-label'>Original · {source_lang}</div>", unsafe_allow_html=True)
        st.code(st.session_state['source_code'], language=source_lang.lower())

    with out_col2:
        st.markdown(f"<div class='output-label'>Translated · {target_lang}</div>", unsafe_allow_html=True)
        st.code(st.session_state['translated_code'], language=target_lang.lower())
        st.download_button(
            "⬇ Download",
            data=st.session_state['translated_code'],
            file_name=f"translated.{target_lang.lower()}",
        )

    st.markdown("<div class='accent-divider' style='margin-top:20px'></div>", unsafe_allow_html=True)

    # Execution output panels
    leg_out_col, trans_out_col = st.columns(2)
    with leg_out_col:
        st.markdown("<div class='output-label'>Execution · Original</div>", unsafe_allow_html=True)
        if st.session_state['legacy_output']:
            st.code(st.session_state['legacy_output'])
        else:
            st.info("Upload a test file to see execution output")

    with trans_out_col:
        st.markdown("<div class='output-label'>Execution · Translated</div>", unsafe_allow_html=True)
        if st.session_state['translated_output']:
            st.code(st.session_state['translated_output'])
        else:
            st.info("Upload a test file to see execution output")

# ------------------------------------------------------------------------------------
# Errors & Fixes panel — placeholder for RAG-retrieved context
# ------------------------------------------------------------------------------------
with st.expander("🧠 Retrieved errors & fixes (RAG)", expanded=False):
    # TODO: once translate_code() actually does retrieval, populate
    # st.session_state['errors_fixes'] with (error, fix) pairs and render them here,
    # e.g. one st.warning(error) + st.success(fix) per retrieved pair, plus maybe
    # a similarity score so you can see what RAG matched on.
    if not st.session_state['errors_fixes']:
        st.caption("Nothing retrieved yet — this fills in once RAG is wired into translate_code().")
    else:
        for err, fix in st.session_state['errors_fixes']:
            st.warning(err)
            st.success(fix)