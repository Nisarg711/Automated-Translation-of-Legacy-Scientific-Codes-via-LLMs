import streamlit as st
import os
import uuid
from tempbackend import app
from tempbackend import parse_tests_from_string
from auth import register_user, authenticate_user_with_token, verify_access_token
from streamlit_cookies_manager import EncryptedCookieManager

st.set_page_config(page_title="Automated Legacy Code Translator", layout="wide")

cookies = EncryptedCookieManager(
    password=os.environ["JWT_SECRET"],
    prefix="bmp_auth",
)

cookies_ready = cookies.ready()

# ------------------------------------------------------------------------------------
# Custom CSS — typography, accent color, structural refinements, and auth page styles.
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

/* ---- Auth landing page styles ---- */
.auth-container {
    max-width: 440px;
    margin: 60px auto 0 auto;
    padding: 40px 36px 32px 36px;
    border: 1px solid rgba(241, 196, 15, 0.15);
    border-radius: 16px;
    background: rgba(255,255,255,0.02);
    backdrop-filter: blur(12px);
}
.auth-brand {
    text-align: center;
    margin-bottom: 8px;
}
.auth-brand .logo-icon {
    font-size: 36px;
    margin-bottom: 4px;
}
.auth-brand h1 {
    font-family: 'Inter', sans-serif !important;
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.3px !important;
    margin: 0 !important;
}
.auth-brand .subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #f1c40f;
    margin-top: 4px;
}
.auth-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #f1c40f44, transparent);
    margin: 20px 0;
}
.guest-section {
    text-align: center;
    margin-top: 8px;
}
.guest-section .label {
    font-size: 11px;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 10px;
}
/* User badge in sidebar */
.user-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    font-family: 'Inter', sans-serif;
    border: 1px solid #f1c40f44;
    color: #f1c40f;
    margin-bottom: 12px;
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
    st.session_state['pending_test_input'] = ""


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
    inputs= {
            "input_code": code,
            "inp_lang": source_lang.lower(),
            "target_lang": target_lang.lower(),
            "legacy_output": "",
            "translated_output": "",
            "retrieved_context": [],    # NEW
            "error_snippet": "",        # NEW
            "last_feedback": [],        # NEW
        }
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
            # node name → human readable status message
    NODE_MESSAGES = {
        "setup":     "⚙️  Setting up environment...",
        "translate": "🔄  Translating code...",
        "run_tests": "🧪  Running test cases...",
        "retrieve":  "🧠  Retrieving similar past fixes...",
        "navigator": "🔍  Diagnosing errors...",
        "driver":    "🔧  Applying fix...",
        "store":     "💾  Storing experience...",
    }
    with st.status("Translating...", expanded=True) as status:
        for updates in app.stream(inputs,config,stream_mode='updates'):
            node_name=list(updates.keys())[0]
            message = NODE_MESSAGES.get(node_name, f"Running {node_name}...")
            st.write(message)
        if node_name=="run_tests":
            node_state = updates[node_name]
            if not node_state.get("passed", True) and node_state.get("feedback"):
                attempt=node_state.get("attempt_count",0)
                failed = len(node_state.get("feedback", []))
                st.write(f"   ↳ {failed} test(s) failed — attempt {attempt + 1}")

    final_state=app.get_state({"configurable":{"thread_id":thread_id}})
    status.update(label="✅ Translation complete!", state="complete", expanded=False)
    result = final_state.values
    st.session_state['errors_fixes'] = result.get("retrieved_context", [])
    print(result)
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
if 'pending_test_input' not in st.session_state:
    st.session_state['pending_test_input'] = ""

if 'attempt_count' not in st.session_state:
    st.session_state['attempt_count'] = 0

if 'passed' not in st.session_state:
    st.session_state['passed'] = None

if 'legacy_output' not in st.session_state:
    st.session_state['legacy_output'] = ""

if 'translated_output' not in st.session_state:
    st.session_state['translated_output'] = ""

# Auth session state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if 'role' not in st.session_state:
    st.session_state['role'] = None  # "user" or "guest"

if 'username' not in st.session_state:
    st.session_state['username'] = None


def sync_auth_from_cookie():
    token = cookies.get("auth_token")
    if not token:
        if st.session_state.get('role') == "guest" and st.session_state.get('authenticated'):
            return
        st.session_state['authenticated'] = False
        st.session_state['role'] = None
        st.session_state['username'] = None
        return

    token_ok, token_data = verify_access_token(token)
    if token_ok:
        st.session_state['authenticated'] = True
        st.session_state['role'] = token_data.get('role', 'user')
        st.session_state['username'] = token_data.get('username')
    else:
        cookies.pop("auth_token", None)
        cookies.save()
        st.session_state['authenticated'] = False
        st.session_state['role'] = None
        st.session_state['username'] = None


def reset_app_state():
    preserved_prefixes = ("EncryptedCookieManager",)
    preserved_keys = {"auth_token"}
    for key in list(st.session_state.keys()):
        if key in preserved_keys or key.startswith(preserved_prefixes):
            continue
        del st.session_state[key]
if cookies_ready:
    sync_auth_from_cookie()

add_thread(st.session_state['thread_id'], st.session_state['title'])


# ====================================================================================
# AUTH LANDING PAGE
# ====================================================================================
def show_auth_page():
    """Render the login / register / guest landing page."""

    # Branding header
    st.markdown("""
    <div class="auth-container">
        <div class="auth-brand">
            <div class="logo-icon">🔬</div>
            <h1>Automated Code Translator and Executor</h1>
            <div class="subtitle">Automated Legacy Code Translation</div>
        </div>
        <div class="auth-divider"></div>
    </div>
    """, unsafe_allow_html=True)

    # Center the form with columns
    _, col_center, _ = st.columns([1.5, 2, 1.5])

    with col_center:
        login_tab, register_tab = st.tabs(["Login", "Register"])

        # ---- Login tab ----
        with login_tab:
            with st.form("login_form", clear_on_submit=False):
                login_user = st.text_input("Username", key="login_username", placeholder="Enter your username")
                login_pass = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
                login_submit = st.form_submit_button("Login", type="primary", use_container_width=True)

            if login_submit:
                success, msg, token = authenticate_user_with_token(login_user, login_pass)
                if success:
                    cookies["auth_token"] = token
                    cookies.save()
                    st.session_state['authenticated'] = True
                    st.session_state['role'] = "user"
                    st.session_state['username'] = login_user.strip()
                    st.rerun()
                else:
                    st.error(msg)

        # ---- Register tab ----
        with register_tab:
            with st.form("register_form", clear_on_submit=False):
                reg_user = st.text_input("Choose a username", key="reg_username", placeholder="Pick a username")
                reg_email = st.text_input("Email", key="reg_email", placeholder="your@email.com")
                reg_pass = st.text_input("Password", type="password", key="reg_password", placeholder="Min 4 characters")
                reg_pass_confirm = st.text_input("Confirm password", type="password", key="reg_password_confirm", placeholder="Re-enter password")
                reg_submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)

            if reg_submit:
                if reg_pass != reg_pass_confirm:
                    st.error("Passwords do not match.")
                else:
                    success, msg = register_user(reg_user, reg_pass, reg_email)
                    if success:
                        st.success("Account created! You can now log in.")
                    else:
                        st.error(msg)

        # ---- Divider ----
        st.markdown("<div class='auth-divider'></div>", unsafe_allow_html=True)

        # ---- Guest button ----
        st.markdown("<div class='guest-section'><div class='label'>or</div></div>", unsafe_allow_html=True)
        if st.button("Continue as Guest", use_container_width=True, key="guest_btn"):
            cookies.pop("auth_token", None)
            cookies.save()
            st.session_state['authenticated'] = True
            st.session_state['role'] = "guest"
            st.session_state['username'] = None
            st.rerun()


# ====================================================================================
# MAIN TRANSLATOR UI (only shown when authenticated)
# ====================================================================================
def show_translator_ui():
    """Render the full translator interface — sidebar, input, output."""

    # ------------------------------------------------------------------------------------
    # Sidebar UI
    # ------------------------------------------------------------------------------------
    with st.sidebar:
        st.markdown("#### Automated Code Translator And Executor")
        st.markdown("<div style='height:2px;background:linear-gradient(90deg,#f1c40f,transparent);border-radius:2px;margin-bottom:12px'></div>", unsafe_allow_html=True)

        # User badge
        if st.session_state['role'] == "guest":
            st.markdown("<span class='user-badge'>👤 Guest</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span class='user-badge'>🔒 {st.session_state['username']}</span>", unsafe_allow_html=True)

        # Logout button
        if st.button("Logout", use_container_width=True, key="logout_btn"):
            cookies.pop("auth_token", None)
            cookies.save()
            reset_app_state()
            st.rerun()

        st.markdown("<div style='height:2px;background:linear-gradient(90deg,#f1c40f22,transparent);border-radius:2px;margin:8px 0 16px 0'></div>", unsafe_allow_html=True)

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
    uploaded_code = None
    uploaded_file = None

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


    test_slot = st.container()
    with test_slot:
        st.markdown("<div style='margin:12px 0 6px 0;font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:#94a3b8;font-family:Inter,sans-serif'>Test Cases</div>", unsafe_allow_html=True)

        tc_col1, tc_col2 = st.columns([1, 1])
        with tc_col1:
            uploaded_test_file = st.file_uploader(
                "Upload a test file",
                type="txt",
                key="test_file_uploader"
            )
            if uploaded_test_file is not None:
                content = uploaded_test_file.read().decode("utf-8")
                st.session_state['tests'] = parse_tests_from_string(content)
                st.caption(f"✅ {len(st.session_state['tests'])} test case(s) loaded from file")

        with tc_col2:
            st.caption("Enter the number of test cases on the first line, then paste each test case separated by a blank line.")
            manual_input = st.text_area(
                "Test input (stdin)",
                height=180,
                placeholder="Example:\n2\n1 2\n3 4\n\n5\n6 7\n8 9\n\nEach test case can span multiple lines. Separate test cases with a blank line.",
                key="manual_test_input_text",
                label_visibility="collapsed"
            )
            load_col, clear_col = st.columns([1, 1])
            with load_col:
                if st.button("📥 Load test cases", use_container_width=True):
                    if manual_input.strip():
                        parsed = parse_tests_from_string(manual_input)
                        st.session_state['tests'] = parsed
                        st.rerun()
            with clear_col:
                if st.button("🗑 Clear all", use_container_width=True):
                    st.session_state['tests'] = []
                    st.rerun()
            # --- Show added test cases ---
        if st.session_state['tests']:
            st.markdown(f"<div style='font-size:11px;color:#94a3b8;margin-top:8px'>{len(st.session_state['tests'])} test case(s) ready</div>", unsafe_allow_html=True)
            for i, t in enumerate(st.session_state['tests'], 1):
                t_col1, t_col2 = st.columns([10, 1])
                with t_col1:
                    st.caption(f"Test {i}:")
                    st.code(t.rstrip(), language="text")
                with t_col2:
                    if st.button("✕", key=f"remove_test_{i}"):
                        st.session_state['tests'].pop(i - 1)
                        st.rerun()


    # ------------------------------------------------------------------------------------
    # Translate action
    # ------------------------------------------------------------------------------------
    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
    translate_clicked = st.button("⟳  Translate", type="primary", disabled=not active_code.strip())

    if translate_clicked:
        st.session_state['source_code'] = active_code

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
                st.info("Add test cases above to see execution output")

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
            if not st.session_state['errors_fixes']:
                st.caption("Nothing retrieved — either no similar past errors exist yet, or this translation passed on first attempt.")
            else:
                st.caption(f"{len(st.session_state['errors_fixes'])} past experience(s) retrieved and used to guide this translation")
                for i, exp in enumerate(st.session_state['errors_fixes'], 1):
                    st.markdown(f"**Past Fix {i}**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("<div class='output-label'>What went wrong</div>", unsafe_allow_html=True)
                        try:
                            import json
                            nav = json.loads(exp['navigator_analysis'])
                            st.caption(nav.get('error_summary', exp['navigator_analysis'][:200]))
                        except:
                            st.caption(exp['navigator_analysis'][:200])
                    with col2:
                        st.markdown("<div class='output-label'>Working fix applied</div>", unsafe_allow_html=True)
                        st.code(exp['working_fix_snippet'], language="python")
                    if i < len(st.session_state['errors_fixes']):
                        st.divider()


# ====================================================================================
# PAGE ROUTER — auth gate
# ====================================================================================
if st.session_state['authenticated']:
    show_translator_ui()
else:
    show_auth_page()