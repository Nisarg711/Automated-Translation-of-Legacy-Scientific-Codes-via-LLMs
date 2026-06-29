import streamlit as st
import uuid


st.set_page_config(page_title="Automated Legacy Code Translator", layout="wide")

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
    st.session_state['errors_fixes'] = []  # placeholder: will hold RAG-retrieved (error, fix) pairs


def add_thread(thread_id, title="New Translation"):
    if thread_id not in st.session_state['translation_threads']:
        st.session_state['translation_threads'][thread_id] = {
            "title": title,
            "source_lang": None,
            "target_lang": None,
            "source_code": "",
            "translated_code": "",
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


def translate_code(code: str, source_lang: str, target_lang: str, thread_id: str) -> str:
    """
    Placeholder translation call — swap this whole function body for the real pipeline.

    TODO (backend integration):
      This will become a single call into your LangGraph app — one graph,
      not a separate RAG step + separate generation step. Retrieval,
      generation, validation, and the fix-loop are all nodes *inside* that
      one graph; this function just invokes it and unpacks the result, e.g.:

          res = app.invoke(
              {"code": code, "source_lang": source_lang, "target_lang": target_lang},
              config={"configurable": {"thread_id": thread_id}}
          )
          return res["translated_code"]

      Since retrieval happens inside the graph (not here in the frontend),
      if you want the "Retrieved errors & fixes" panel to show anything,
      the graph's final state needs to carry that info back out too —
      e.g. res["retrieved_pairs"] — and you'd set
      st.session_state['errors_fixes'] from that after the invoke call.
      Without that, the panel has nothing to display, since the frontend
      only ever sees what `res` hands back.
    """
    return (
        f"# TODO: backend not connected yet.\n"
        f"# Will translate the {source_lang} code on the left into {target_lang} here.\n"
    )


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

add_thread(st.session_state['thread_id'], st.session_state['title'])

# ------------------------------------------------------------------------------------
# Sidebar UI
# ------------------------------------------------------------------------------------
st.sidebar.title("Automated Legacy Code Translator")

if st.sidebar.button("➕ New Translation"):
    new_translation_session()
    st.rerun()

st.sidebar.subheader("History")
for thid, info in reversed(list(st.session_state['translation_threads'].items())):
    label = info.get("title", "New Translation")
    if st.sidebar.button(str(label), key=thid):
        st.session_state['thread_id'] = thid
        loaded = load_translation(thid)
        st.session_state['title'] = loaded.get("title", "New Translation")
        st.session_state['source_code'] = loaded.get("source_code", "")
        st.session_state['translated_code'] = loaded.get("translated_code", "")
        st.rerun()

# ------------------------------------------------------------------------------------
# language selection
# ------------------------------------------------------------------------------------
st.title("Code Translator")

lang_slot = st.container()
tab_slot=st.container()

with tab_slot: 
    # Input: either Write code or upload file
    input_tab, upload_tab = st.tabs(["✍️ Paste code", "📁 Upload file"])

    with input_tab:
        pasted_code = st.text_area(
        "Write or paste your code here",
        value=st.session_state['source_code'],
        height=300,
        key="pasted_code_area",
        )

    with upload_tab:
        uploaded_file = st.file_uploader(
            "Drop a code file",
            type=list(EXT_TO_LANG.keys()),
        )
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
                st.rerun()
            st.code(uploaded_code, language=ext if ext != "f90" else "fortran")
#plus both selectboxes inside it. This code runs after the upload detection, but visually 
# it still appears above the tabs because lang_slot was created first cuz we created containerss
#in that order
with lang_slot:
    col_lang1, col_lang2 = st.columns(2)
    with col_lang1:
        source_lang = st.selectbox("Source language", LANGUAGES, key="source_lang_select")
    with col_lang2:
        target_lang = st.selectbox(
            "Target language", LANGUAGES, index=1, key="target_lang_select"
        )
#uploaded file takes priority if both inputs are filled
active_code = uploaded_code if (uploaded_file is not None and uploaded_code) else pasted_code

# ------------------------------------------------------------------------------------
# Translate action
# ------------------------------------------------------------------------------------
translate_clicked = st.button("🔁 Translate", type="primary", disabled=not active_code.strip())

if translate_clicked:
    st.session_state['source_code'] = active_code

    with st.spinner("Translating..."):
        # TODO: swap for st.write_stream(...) once the LangGraph app streams tokens,
        # the same way your chatbot does with stream_mode="messages"
        result = translate_code(
            active_code, source_lang, target_lang, st.session_state['thread_id']
        )
        st.session_state['translated_code'] = result

    title = f"{source_lang} → {target_lang}"
    st.session_state['title'] = title
    st.session_state['translation_threads'][st.session_state['thread_id']] = {
        "title": title,
        "source_lang": source_lang,
        "target_lang": target_lang,
        "source_code": active_code,
        "translated_code": st.session_state['translated_code'],
    }
    st.rerun()


if st.session_state['translated_code']:
    st.divider()
    out_col1, out_col2 = st.columns(2)

    with out_col1:
        st.subheader(f"Original ({source_lang})")
        st.code(st.session_state['source_code'], language=source_lang.lower())

    with out_col2:
        st.subheader(f"Translated ({target_lang})")
        st.code(st.session_state['translated_code'], language=target_lang.lower())
        st.download_button(
            "⬇️ Download translated code",
            data=st.session_state['translated_code'],
            file_name=f"translated.{target_lang.lower()}",
        )

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