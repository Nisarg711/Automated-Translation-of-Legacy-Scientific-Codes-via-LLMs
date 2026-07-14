
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from typing import TypedDict, Annotated,List
from langchain_groq import ChatGroq
from langgraph.graph.message import add_messages
from langgraph.graph import START, END,StateGraph
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
# langchain_huggingface and sentence_transformers are lazy-imported in _get_embedding_model()
# to avoid loading PyTorch (~200MB) at startup — critical for Render's 512MB free tier
from dotenv import load_dotenv
import os
import re
import time
import subprocess
import tracemalloc
import psutil
from huggingface_hub import InferenceClient
# from google import genai
from openai import OpenAI
from dotenv import load_dotenv
from groq import Groq
import psycopg2
from pgvector.psycopg2 import register_vector

import numpy as np
import json
import uuid
from rank_bm25 import BM25Okapi
load_dotenv()

def get_db_connection():
    conn=psycopg2.connect(os.environ["NEON_DATABASE_URL"])
    register_vector(conn)  # critical — tells psycopg2 how to handle vector type
    return conn

_embedding_model = None

def _get_embedding_model():
    """Lazy-load the embedding model — avoids ~200MB memory at startup on Render."""
    global _embedding_model
    if _embedding_model is None:
        from langchain_huggingface import HuggingFaceEmbeddings
        _embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return _embedding_model

def embed_text(text: str) -> np.ndarray:
    embedding = _get_embedding_model().embed_query(text)
    return embedding

def generate_hypothetical_navigator_analysis(
    feedback: list,
    inp_lang: str,
    target_lang: str,
    provider: str,
    model_id: str
) -> str:
    first_fail = feedback[0]
    expected = first_fail.get('expected', '')[:150]
    actual = first_fail.get('actual', '')[:200]

    hyde_prompt = f"""A {inp_lang} to {target_lang} translation failed:
- Expected: {expected}
- Actual: {actual}

Output ONLY a JSON diagnosis in this exact format, nothing else:
{{
  "error_summary": "<one sentence describing what type of translation error this is>",
  "root_cause": "<technical explanation of why {inp_lang} and {target_lang} behave differently here>",
  "fix_hints": ["<specific fix 1>", "<specific fix 2>"]
}}"""

    result = generate_code(hyde_prompt, provider, model_id)
    # extract just the JSON part
    json_match = re.search(r'\{[\s\S]*\}', result or "")
    return json_match.group(0).strip() if json_match else result.strip()

def get_bm25_index(language_pair: str):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT parent_id, navigator_analysis 
                FROM child_vectors
                WHERE language_pair = %s
            """, (language_pair,))
            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows or len(rows) < 2:  # BM25 needs at least 2 documents to be meaningful
        return None, rows

    corpus = [row[1].lower().split() for row in rows]
    try:
        bm25 = BM25Okapi(corpus, epsilon=0.25)
        #Here, this function actually computes IDF for each unique term and also the TFs for each doc
        #as well as stores length and avg length of document.
    except ZeroDivisionError:
        return None, rows   # fall back gracefully — dense retrieval only

    return bm25, rows


def bm25_retrieve(query: str, language_pair: str, k: int = 5) -> list:
    """
    Retrieves top-k results using BM25 scoring.
    Returns list of (parent_id, navigator_analysis, bm25_score) tuples
    sorted by score descending.
    """
    bm25, rows = get_bm25_index(language_pair)
    
    if not rows or bm25 is None:
        return []
    
    # tokenize query the same way as corpus — lowercase + whitespace split
    query_tokens = query.lower().split()
    
    # get BM25 scores for all documents
    scores = bm25.get_scores(query_tokens)
    #It returns a numpy array of length N (one score per document in your corpus), 
    # where each score is the BM25 relevance score of that document against your query. Higher score = more relevant.
    # pair each score with its row and sort descending
    scored = sorted(
        zip(scores, rows),
        key=lambda x: x[0],
        reverse=True
    )
    #You zip each score with its corresponding row (parent_id, navigator_analysis), sort by score descending, 
    # and return the top-k with score > 0 — filtering out documents with zero keyword overlap.
    # return top-k as (parent_id, navigator_analysis, bm25_score)
    return [
        (row[0], row[1], score)
        for score, row in scored[:k]
        if score > 0  # filter out zero-score documents — no keyword overlap at all
    ]
def reciprocal_rank_fusion(
    dense_results: list,      # list of (parent_id, nav_analysis, embedding, similarity)
    bm25_results: list,       # list of (parent_id, nav_analysis, bm25_score)
    k: int = 60               # RRF damping constant — 60 is standard default
) -> list:
    """
    Fuses dense and BM25 ranked lists using Reciprocal Rank Fusion.
    Returns list of (parent_id, rrf_score) sorted by score descending.
    k=60 is the standard RRF constant from the original 2009 paper —
    dampens the impact of very high ranks without ignoring lower ones.
    """
    rrf_scores = {}  # parent_id -> cumulative RRF score

    # score from dense retrieval list
    for rank, result in enumerate(dense_results, start=1):
        parent_id = str(result[0])
        rrf_scores[parent_id] = rrf_scores.get(parent_id, 0) + 1 / (k + rank)

    # score from BM25 retrieval list
    for rank, result in enumerate(bm25_results, start=1):
        parent_id = str(result[0])
        rrf_scores[parent_id] = rrf_scores.get(parent_id, 0) + 1 / (k + rank)

    # sort by combined RRF score descending
    sorted_ids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_ids  # list of (parent_id, rrf_score)

class TranslationState(TypedDict):
    input_code: str
    inp_lang: str
    target_lang: str
    input_path: str         # NEW — legacy code written to disk, set by setup_node
    working_filepath: str   # NEW — server-side temp file, set once in translate_node
    translated_code: str
    feedback: list          # filled by run_tests node
    navigator_analysis: str # filled by navigator node
    attempt_count: int
    max_attempts: int
    passed: bool
    legacy_output:str
    translated_output:str
    retrieved_context:list
    error_snippet: str   # extracted from navigator's relevant_lines, used by store_node
    last_feedback: list   # stores feedback from last failed attempt before fix worked


# Step 1 — Define your State
# Before any nodes, decide what data flows through the graph. Looking at your run_benchmark, the things that get read/written across phases are: input_code, inp_lang, target_lang, translated_code, test_results/feedback, attempt_count, max_attempts, passed. Define this as a TypedDict (this is your single source of truth the whole graph reads/writes — same role as results dict in your notebook, but shared across nodes instead of local to one function).
import tempfile

def get_working_filepath(target_lang: str) -> str:  #This is used for temporary file creation on server side
    ext = get_file_extension(target_lang)
    fd, path = tempfile.mkstemp(suffix=ext)
    os.close(fd)
    return path

def get_file_extension(language):
    extensions = {"python": ".py", "c": ".c", "cpp": ".cpp", "c++": ".cpp", "java": ".java", "go": ".go", "rust": ".rs","fortran": ".f"}
    return extensions.get(language.lower(), ".txt")

def extract_code(llm_output: str) -> str:
    code = llm_output.strip()
    fence_match = re.search(r"```[\w+-]*\n([\s\S]*?)\n```", code)
    if fence_match:
        return fence_match.group(1).strip()
    code = re.sub(r"^```[\w+-]*", "", code)
    code = re.sub(r"```$", "", code)
    return code.strip()

def normalize(output):
    """Normalize output by standardizing spaces and floats for cross-language matching."""
    # Convert to lowercase to avoid case-sensitivity issues
    output = output.lower()
    
    # Process line by line
    lines = [line.strip() for line in output.split('\n')]
    
    normalized_lines = []
    for line in lines:
        if not line:
            continue
            
        # Replace multiple spaces with a single space
        line = re.sub(r'\s+', ' ', line)
        
        # Normalize floats: Strip trailing zeros (e.g., 5.00000000 -> 5.0)
        # Keeps precision intact for exact decimals but normalizes padding
        line = re.sub(r'(\d+\.\d*?[1-9])0+\b', r'\1', line)  # 5.1200 -> 5.12
        line = re.sub(r'(\d+)\.0+\b', r'\1.0', line)         # 5.0000 -> 5.0
        
        normalized_lines.append(line)
        
    return '\n'.join(normalized_lines)

# Add this near your other client initializations
# gemini_api_key = os.getenv("GEMINI_API_KEY")
# gemini_client = genai.Client(api_key=gemini_api_key) if gemini_api_key else None

# Initialize API Clients
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
hf_api_key = os.getenv("HF_API_KEY")
hf_client = InferenceClient(token=hf_api_key) if hf_api_key else None

# Initialize GitHub Models using the standard OpenAI library
github_client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.getenv("GITHUB_API_KEY")
)

# OpenRouter acts exactly like OpenAI, just point it to their base URL
openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)


def generate_code(prompt, provider, model_id):
    """Universal function to call different LLM APIs dynamically."""
    provider = provider.strip().lower()

    try:
        if provider == "groq":
            response = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model_id,
                temperature=0.1,
            )
            return response.choices[0].message.content or ""

        elif provider == "gemini":
            if not gemini_client:
                raise ValueError("Gemini client not initialized. Check your API key.")
            response = gemini_client.models.generate_content(
                model=model_id,
             contents=prompt,
            )
            return response.text or ""
        
        elif provider == "github":
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = github_client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=model_id,
                        temperature=0.1,
                    )
                    return response.choices[0].message.content or ""
                except Exception as e:
                    if "429" in str(e) and attempt < max_retries - 1:
                        print(f"    ⏳ GitHub limit hit. Cooling down for 10s...")
                        time.sleep(10)
                    else:
                        print(f"    ❌ GitHub Error: {str(e)}")
                        return ""
            return ""
        
        elif provider == "openrouter":
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = openrouter_client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=model_id,
                        temperature=0.1,
                        timeout=45.0
                    )
                    # DEFENSIVE CHECK: Prevent NoneType crashes
                    if hasattr(response, 'choices') and response.choices:
                        return response.choices[0].message.content or ""
                    else:
                        print(f"    ⚠️ OpenRouter returned empty object. Retrying...")
                        time.sleep(5)
                except Exception as e:
                    if "429" in str(e) and attempt < max_retries - 1:
                        print(f"    ⚠️ OpenRouter busy. Retrying in 5s (Attempt {attempt + 1})...")
                        time.sleep(5)
                    else:
                        print(f"    ❌ OpenRouter Error: {str(e)}")
                        return ""
            
            # THE FIX: If it tries 3 times and still gets empty objects, safely return empty string
            print(f"    ❌ OpenRouter Failed all retries.")
            return ""

        elif provider == "huggingface":
            if not hf_client:
                raise ValueError("HF_API_KEY not found or client not initialized.")
            
            try:
                # The official SDK handles the URLs, headers, and routing automatically
                response = hf_client.chat_completion(
                    model=model_id,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2048,
                    temperature=0.1
                )
                return response.choices[0].message.content or ""
            
            except Exception as e:
                error_msg = str(e)
                if "503" in error_msg or "loading" in error_msg.lower():
                    print(f"    ⏳ HF Model {model_id} is currently waking up on their servers. Try again in 20s.")
                else:
                    print(f"    ❌ HF Error: {error_msg}")
                return ""
            
            res = requests.post(url, headers=headers, json=payload, timeout=120)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            elif res.status_code == 503:
                print("    ⚠️ HF Model is loading, skipping for now...")
                return ""
            else:
                print(f"    ❌ HF Error: {res.status_code} - {res.text}")
                return ""

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    except Exception as e:
        print(f"    ❌ API Error ({provider} - {model_id}): {str(e)}")
        return ""


def parse_tests(test_file):
    if not os.path.exists(test_file): return []
    with open(test_file, "r") as f:
        lines = f.readlines()
    if not lines: return []
    t = int(lines[0].strip())
    tests = []
    for i in range(1, t + 1):
        tests.append(lines[i].strip().replace('\\n', '\n') + '\n')
    return tests

def parse_tests_from_string(content: str) -> list:
    lines = content.splitlines()
    if not lines:
        return []
    test_count = int(lines[0].strip())
    body_lines = lines[1:]
    if not body_lines:
        return []

    # old format: one line per test case with \n literals
    # detect by checking if any line contains literal \n
    if any('\\n' in line for line in body_lines):
        return [body_lines[i].strip().replace('\\n', '\n') + '\n'
                for i in range(min(test_count, len(body_lines)))]

    # new format: test cases separated by blank lines
    tests = []
    current_case = []
    for line in body_lines:
        if line.strip() == "":
            if current_case:
                tests.append('\n'.join(current_case).rstrip() + '\n')
                current_case = []
        else:
            current_case.append(line)
    if current_case:
        tests.append('\n'.join(current_case).rstrip() + '\n')

    return tests[:test_count]

def run_program(language, filepath, input_data, timeout=5):
    """A unified runner that returns (output, error_message)."""
    lang = language.lower()
    if not os.path.exists(filepath): return "", "File not found"
    
    try:
        if lang == "python":
            res = subprocess.run(["python", filepath], input=input_data, text=True, capture_output=True, timeout=timeout,  cwd=os.path.dirname(filepath))  # run in same dir as the compiled binary)
            return res.stdout.strip(), res.stderr if res.returncode != 0 else None
            
        elif lang in ["c", "cpp", "c++"]:
            exe = filepath + ".out"
            if lang == "c":
                compiler = "gcc"
                std_flag = "-std=c11"
            else:
                compiler = "g++"
                std_flag = "-std=c++17"

            comp = subprocess.run(
                [compiler, std_flag, filepath, "-o", exe],
                capture_output=True, text=True
            )
            if comp.returncode != 0:
                return "", f"Compile error: {comp.stderr}"
            res = subprocess.run(
                [exe], input=input_data, text=True,
                capture_output=True, timeout=timeout,
                cwd=os.path.dirname(filepath)
            )
            return res.stdout.strip(), res.stderr if res.returncode != 0 else None
            
        elif lang in ["fortran", "f77", "f90"]:
            exe = "./a.out"
            comp = subprocess.run(["gfortran", filepath, "-o", exe], capture_output=True, text=True)
            if comp.returncode != 0: return "", f"Compile error: {comp.stderr}"
            res = subprocess.run([exe], input=input_data, text=True, capture_output=True, timeout=timeout)
            return res.stdout.strip(), res.stderr if res.returncode != 0 else None


        elif lang == "java":
            file_dir = os.path.dirname(filepath) or "."
            file_name = os.path.basename(filepath)
            with open(filepath, 'r') as f: java_code = f.read()
            class_match = re.search(r'public\s+class\s+(\w+)', java_code)
            classname = class_match.group(1) if class_match else file_name.replace(".java", "")
            comp = subprocess.run(["javac", file_name], cwd=file_dir, capture_output=True, text=True)
            if comp.returncode != 0: return "", f"Compile error: {comp.stderr}"
            res = subprocess.run(["java", classname], input=input_data, text=True, capture_output=True, timeout=timeout, cwd=file_dir)
            return res.stdout.strip(), res.stderr if res.returncode != 0 else None
            
    except subprocess.TimeoutExpired:
        return "", "Timeout"
    except Exception as e:
        return "", str(e)
    
    return "", f"Language {lang} not supported in runner"



def setup_node(state: TranslationState, config: RunnableConfig) -> dict:
    ...
    input_path = get_working_filepath(state["inp_lang"])  # reuse same helper, just keyed on inp_lang's extension
    with open(input_path, "w") as f:
        f.write(state["input_code"])

    return {
        "input_path": input_path,
        "max_attempts": config["configurable"].get("max_attempts", 5),  # default matches your notebook's max_attempts=5
    }

def translate_node(state: TranslationState, config: RunnableConfig) -> dict:
    # Pull static config (provider, model_id) the same way you'll pull tests later
    provider = config["configurable"]["provider"]
    model_id = config["configurable"]["model_id"]
    inp_lng=state['inp_lang']
    target_lng=state['target_lang']
    input_code=state['input_code']
    prompt = f''' You are an exceptionally intelligent coding assistant acting as a literal syntax compiler for code translation. You consistently deliver accurate translations while maintaining the original code's exact functionality, output format, and numerical precision.

Please translate this {inp_lng} code to {target_lng}. Follow these CRITICAL guidelines:

1) **COMPLETE PROGRAM**: Translate the ENTIRE program including ALL subroutines/functions/methods, initialization, calculations, and display/output routines. Do NOT omit any functions or return partial code. The output must be a complete, executable program.

2) **LITERAL MATHEMATICS (NO HALLUCINATIONS)**: Translate mathematical operations, formulas, and variable assignments EXACTLY as they appear in the source code. 
   - DO NOT substitute formulas from your own knowledge. 
   - Preserve all numeric constants and precision multipliers exactly.
   - Example: `0.5 * dt * dx` stays as `0.5 * dt * dx` (do not simplify differently).

3) **EXACT I/O & PROMPTS**: Every input must produce IDENTICAL output byte-for-byte in strict test environments.
   - Read inputs dynamically in the same order as the original. NEVER hardcode test values.
   - Preserve every single print statement, prompt string, and delimiter exactly.
   - Do NOT add extra newlines unless they exist in the source. Handle line-by-line input correctly.

4) **DISPLAY/PRINT LOOPS WITH STRIDE**: When translating loops that print values with a stride pattern (e.g., printing every nth element):
   - Preserve the stride/step calculation precisely.
   - DO NOT print every single value if the original prints selectively—this guarantees test failures.
   - Translate format specifications to exact target equivalents (e.g., Fortran `format(f10.4,' | ',f15.2)` becomes Python `print(f"{{val1:10.4f}} | {{val2:15.2f}}")`).

5) **OUTPUT FORMAT**: Preserve EXACT formatting:
   - Decimal precision (2 decimals, 4 decimals, etc.).
   - Field widths, padding, string formatting, and alignment.

6) **ARRAYS & INDEXING (CRITICAL BOUNDS)**: 
   - Identify the source language's indexing system (e.g., 1-based vs 0-based).
   - Convert array access appropriately for the target language.
   - strictly adjust loop boundaries to prevent off-by-one errors. If a source loop runs exactly 19 times, the target loop MUST run exactly 19 times.

7) **STRUCTURE**: 
   - Maintain overall organization (subroutines/functions/methods, main logic/entry point).
   - Use appropriate language constructs (classes if needed for state management).
   - Keep method/function names and parameter names clear and meaningful.

8) **NUMERICAL OPERATIONS**: 
   - Preserve numeric types (integer, float, double precision).
   - Preserve integer division semantics strictly according to the source language rules.
   - Preserve floating-point precision and rounding behavior.

9) **LANGUAGE-SPECIFIC CONVERSIONS**: 
   - Translate language constructs appropriately (e.g., COMMON blocks to classes, modules to namespaces).
   - Convert language-specific keywords and syntax to exact target language equivalents.

10) **LIBRARIES & IMPORTS**: Include all necessary imports/headers/libraries needed for the algorithms to run.

11) **OUTPUT**: Return ONLY the complete translated code in a single code block. NO explanations, NO extra text, NO incomplete snippets.

12) **DO NOT**: 
    - Optimize or refactor algorithms.
    - Change output stride/sampling patterns.
    - Omit any functions, subroutines, or methods.
    - Change the program flow or control structure.
13) **STRICT I/O SEPARATION**: 
    - In Python, NEVER put prompt strings inside the `input()` function (e.g., NO `input("Enter value:")`).
    - You MUST separate prompts and inputs. Use `print("Enter value:")` followed by `val = input()`. This perfectly mimics Fortran's `print *` newline behavior.
    
14) **NO HELPFUL TEXT**: Do not add helpful text like `(y/n)` or `...` to the prompts. Translate the strings exactly as they appear in the original source, character for character.
15) MULTI-VARIABLE INPUTS (CRITICAL): Fortran's read(*,*) a, b reads tokens across multiple newlines. Python's input().split() only reads a single line. You MUST perfectly mimic Fortran by printing the original prompt string ONCE, followed by separate input() calls for each variable.
BAD: a, b = input("Enter a and b: ").split()
GOOD: > print("Enter a and b: ")
a = type(input().strip())
b = type(input().strip())

"16) **DIVISION BY ZERO (IEEE 754)**: Fortran natively handles division by zero by evaluating to `Infinity` and propagating `NaN`s, whereas Python crashes with `ZeroDivisionError`. If a formula may divide by zero, you MUST handle it by returning `float('inf')` (or `-inf` based on the numerator) to perfectly match Fortran's behavior. NEVER add an epsilon (e.g., `+ 1e-6`) or return 0, as this causes numerical explosions and OverflowErrors in physics loops.\n",
17) **C TARGET - printf FORMAT STRINGS (CRITICAL)**:
   - NEVER split a printf format string across multiple lines.
   - The \n escape sequence inside printf MUST be written as \\n within 
     the format string on a SINGLE line.
   - CORRECT:   printf("%20.10f%20.10f%20.10f\n", t, theta, omega);
   - INCORRECT: printf("%20.10f%20.10f%20.10f\\n
                       ", t, theta, omega);
   - Every printf call must open and close its format string on the same line.
   - This applies to ALL printf/fprintf calls without exception.

   18) **FORTRAN TO C - OUTPUT PRESERVATION**:
   - Fortran write(*,'(3f20.10)') a, b, c translates to 
     printf("%20.10f%20.10f%20.10f\n", a, b, c); — keep the printf, 
     do NOT remove it.
   - Only remove printf calls that were added as interactive prompts 
     (e.g. "Enter value ->"). Never remove data output statements.
   - Fortran format specifiers map directly: f20.10 → %20.10f, 
     e12.5 → %12.5e, i5 → %5d.

     CRITICAL: You must output the COMPLETE translated code with no truncation.
Every function must be fully closed with its closing brace.
Never end your response mid-function. If the code is long, prioritize
completeness over comments.
Code to Translate: {input_code} '''

    raw_output = generate_code(prompt, provider, model_id)
    translated_code = extract_code(raw_output)

    working_filepath = get_working_filepath(state["target_lang"])
    with open(working_filepath, "w") as f:
        f.write(translated_code)
    '''One thing to flag for later (not now): since working_filepath is a real file on the server's disk, 
you'll eventually want cleanup logic — delete it once a translation run reaches END (success or max-attempts-exhausted), 
so temp files don't pile up once this is hosted and getting real traffic.
 Worth a TODO comment, not a blocker right now.
 '''
    return {
    "translated_code": translated_code,
    "working_filepath": working_filepath,
    "attempt_count": 0,
}




def run_tests_node(state: TranslationState, config: RunnableConfig) -> dict:
    tests = config["configurable"].get("tests", [])
    if not tests:
        return {"feedback": [], "passed": True}

    feedback = []
    legacy_blocks = []
    translated_blocks = []
    for i, input_data in enumerate(tests, 1):
        legacy_out, legacy_err = run_program(state["inp_lang"], state["input_path"], input_data)
        if legacy_err:
            print(f"[run_tests_node] Legacy execution error on test {i}: {legacy_err}")
        translated_out, err = run_program(state["target_lang"], state["working_filepath"], input_data)
        # ... rest unchanged

        norm_legacy = normalize(legacy_out)
        norm_translated = normalize(translated_out)
        legacy_blocks.append(f"--- Test {i} ---\n{norm_legacy}")
        translated_blocks.append(f"--- Test {i} ---\n{norm_translated}")

        if err or norm_legacy != norm_translated:
            def truncate_text(text, limit=1000):
                    if not text: return ""
                    if len(text) <= limit: return text
                    return text[:200] + "\n... [TRUNCATED] ...\n" + text[-800:]

            feedback.append({
                    "test": i, 
                    "input": input_data.replace('\n', '\\n'), 
                    "expected": truncate_text(norm_legacy), 
                    "actual": truncate_text(norm_translated) if not err else f"ERROR: {truncate_text(err)}"
                })
            pass

    return {
        "feedback": feedback,
        "passed": len(feedback) == 0,
        "last_feedback": feedback if len(feedback) > 0 else state.get("last_feedback", []),
        "legacy_output":"\n".join(legacy_blocks),
        "translated_output":"\n".join(translated_blocks)
    }


def store_experience(
    language_pair: str,
    navigator_analysis: str,
    error_snippet: str,
    working_fix_snippet: str,
    test_feedback: str,
    attempt_number: int
) -> None:
    embedding = np.array(embed_text(navigator_analysis))  # embed the child chunk
    
    '''
    runs only on successful fix, writes the (navigator_analysis, fixed_code_diff) pair to vector store.
    Second, conn.commit() is inside the try block and conn.close() is in finally — this ensures the connection 
    always closes even if an exception occurs mid-insert, preventing connection leaks, which matter once 
    this is deployed on Render and handling multiple users.
    '''
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Step 1: insert parent document first, get back its ID
            cur.execute("""
                INSERT INTO parent_documents 
                    (language_pair, navigator_analysis, error_snippet, 
                     working_fix_snippet, test_feedback, attempt_number)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (language_pair, navigator_analysis, error_snippet,
                  working_fix_snippet, test_feedback, attempt_number))
            
            parent_id = cur.fetchone()[0]
            
            # Step 2: insert child vector with reference to parent
            cur.execute("""
    INSERT INTO child_vectors 
        (parent_id, language_pair, navigator_analysis, embedding)
    VALUES (%s, %s, %s, %s::vector)
""", (parent_id, language_pair, navigator_analysis, embedding.tolist()))
            
            conn.commit()
    finally:
        conn.close()

def retrieve_similar_experiences(
    language_pair: str,
    navigator_analysis: str,
    k: int = 5,
) -> list[dict]:
    #MMR: maximal Marginal relevance
    #<=> is PGVector's cosine distance operator — lower value means more similar. 
    # 1 - (embedding <=> query) converts it to cosine similarity — higher value means more similar. 
    # Both are used here for clarity: ordering by distance, returning similarity score.

    query_embedding = np.array(embed_text(navigator_analysis))
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Step 1: metadata pre-filter + vector similarity search
            # Only searches within the same language pair — hard constraint
            #-------- THis is dense retrieval ------
            cur.execute("""
    SELECT 
        c.parent_id,
        c.navigator_analysis,
        c.embedding,
        1 - (c.embedding <=> %s::vector) AS similarity
    FROM child_vectors c
    WHERE c.language_pair = %s
    ORDER BY c.embedding <=> %s::vector
    LIMIT %s
""", (query_embedding.tolist(), language_pair, query_embedding.tolist(), k))
            
            dense_results = cur.fetchall()
            
            if not dense_results:
                return []
            
            # --- BM25 retrieval ---
            bm25_results = bm25_retrieve(navigator_analysis, language_pair, k=k)

                        # --- RRF fusion ---
            fused = reciprocal_rank_fusion(dense_results, bm25_results)

            # take top k after fusion
            top_ids = [parent_id for parent_id, _ in fused[:2]]
            
            cur.execute("""
            SELECT 
                language_pair, navigator_analysis, error_snippet,
                working_fix_snippet, test_feedback, attempt_number
            FROM parent_documents
            WHERE id = ANY(%s::uuid[])
        """, (top_ids,))
            
            parents = cur.fetchall()
            
            return [
                {
                    "language_pair": p[0],
                    "navigator_analysis": p[1],
                    "error_snippet": p[2],
                    "working_fix_snippet": p[3],
                    "test_feedback": p[4],
                    "attempt_number": p[5],
                }
                for p in parents
            ]
    finally:
        conn.close()

def retrieve_node(state:TranslationState,config:RunnableConfig)->dict:
    '''
     runs before navigator, queries vector store, injects results into state
     Uses HyDE: generates a hypothetical navigator analysis from the current
    feedback, then embeds that for retrieval — bridges the query/document
    space mismatch between raw feedback text and stored navigator analyses.
    '''
    language_pair = f"{state['inp_lang']}→{state['target_lang']}"
    provider = config["configurable"]["provider"]
    model_id = config["configurable"]["model_id"]
    if not state["feedback"]:
        return {"retrieved_context": []}  
   
    hypothetical_analysis=generate_hypothetical_navigator_analysis(
        feedback=state['feedback'],
        inp_lang=state['inp_lang'],
        target_lang=state['target_lang'],
        provider=provider,
        model_id=model_id
    )

    if state.get("navigator_analysis") and state['navigator_analysis'].strip():
        query=state['navigator_analysis']
        print("[retrieve_node] Using real navigator analysis from previous attempt")
    else:
        query=generate_hypothetical_navigator_analysis(
        feedback=state['feedback'],
        inp_lang=state['inp_lang'],
        target_lang=state['target_lang'],
        provider=provider,
        model_id=model_id
    )
    print("[retrieve_node] Using HyDE — first failure, no prior analysis")

    experiences = retrieve_similar_experiences(
        language_pair=language_pair,
        navigator_analysis=query, 
        k=5
    )

    print(f"[retrieve_node] Retrieved {len(experiences)} experiences")
    return {"retrieved_context": experiences}

def extract_error_snippet(navigator_analysis: str, translated_code: str) -> str:
    try:
        # navigator_analysis is already parsed JSON string
        analysis = json.loads(navigator_analysis)
        relevant = analysis.get("relevant_lines", {})
        start = int(relevant.get("start", 1)) - 1  # convert 1-indexed to 0-indexed
        end = int(relevant.get("end", 30))
        
        lines = translated_code.splitlines()
        snippet = "\n".join(lines[start:end])
        return snippet
    except (json.JSONDecodeError, KeyError, ValueError):
        # fallback: return first 30 lines if JSON parsing fails
        return "\n".join(translated_code.splitlines()[:30])
    

def store_node(state: TranslationState, config: RunnableConfig) -> dict:
    # only store if a fix was actually needed — attempt_count=0 means
    # first translation passed, nothing useful to store
    if state["attempt_count"] == 0:
        return {}
    
    language_pair = f"{state['inp_lang']}→{state['target_lang']}"
        # re-extract same line range but from the final working code
    working_fix = extract_error_snippet(
        state["navigator_analysis"],  # contains relevant_lines range
        state["translated_code"]      # now the FIXED version after driver succeeded
    )


    
    store_experience(
        language_pair=language_pair,
        navigator_analysis=state["navigator_analysis"],
        error_snippet=state["error_snippet"],    # broken snippet (from navigator run)
        working_fix_snippet=working_fix,         # fixed snippet (same lines, working code)
        test_feedback=str(state['last_feedback']),
        attempt_number=state["attempt_count"]
    )
    
    return {}   # store_node doesn't update any state field
 
def navigator_node(state: TranslationState, config: RunnableConfig) -> dict:
    provider = config["configurable"]["provider"]
    model_id = config["configurable"]["model_id"]
    
    feedback=state['feedback']
    inp_lng=state['inp_lang']
    input_code=state['input_code']
    translated_code=state['translated_code']
    target_lng=state['target_lang']
        # build retrieved context string only if experiences exist
    retrieved_context_str = ""
    if state["retrieved_context"]:
        retrieved_context_str = "RELEVANT PAST FIXES (use these as hints):\n"
        for i, exp in enumerate(state["retrieved_context"], 1):
            retrieved_context_str += f"""
    Past Fix {i}:
    -  What went wrong: {exp['navigator_analysis'][:300]}
    - Failing snippet:
    {exp['error_snippet'][:200]}
    - Working fix:
    {exp['working_fix_snippet'][:200]}

    ---"""
    nav_prompt = f'''You are an expert code translation debugging assistant. Analyze failed test cases and identify the ROOT CAUSE of differences between the {inp_lng} and {target_lng} code.

{retrieved_context_str}
ANALYZE THE FOLLOWING FATAL ERRORS:
1. **Dropped I/O**: Did the code skip reading a variable entirely?
2. **NameError**: Did a subroutine try to accept variables that weren't defined yet?
3. **SyntaxError (Global/Parameter)**: Did the code declare a variable as `global` while also passing it as a function parameter?
4. **ValueError (unpacking)**: Did Python use `.split()` on a single line when inputs are on multiple lines?
5. **Off-By-One Bounds**: Did a loop start at 1 instead of 0, skipping the initial state?
6. **Concatenated Prompts**: Did the diff show multiple prompts merged onto one line (e.g., `+ prompt 1 -> prompt 2 ->`)? This means the LLM incorrectly used `input("prompt")` instead of `print()`.
7. **Missing Data Rows**: Did Python print the first and last values but skip the middle ones? Check the display loop's stride calculation (e.g., `max(1, n//20)`).

Provide STRICT JSON with actionable fix hints:
{{
  "error_summary": "...",
  "affected_lines": "...",
  "root_cause": "...",
  "fix_hints": ["hint 1", "hint 2"],
  "relevant_lines": {{"start": <integer>, "end": <integer>}}
}}

"relevant_lines" must point to the EXACT lines of the error in the translated code.
If root_cause mentions 'main function', relevant_lines must point to where main() 
starts and ends in the translated code — NOT to other functions.
Count the actual line numbers in the translated code provided above before setting 
start and end. Double-check: does the code at lines start→end actually contain 
the error described in root_cause? If not, recount.

Failed Test Case(s):
{feedback}

Legacy Code ({inp_lng}):
{input_code}

Translated Code ({target_lng}):
{translated_code}
'''

    navigator_raw = generate_code(nav_prompt, provider, model_id)

    # Same JSON-extraction fallback as your original
    json_match = re.search(r'\{[\s\S]*\}', navigator_raw or "")
    navigator_analysis = json_match.group(0) if json_match else (navigator_raw or "").strip()

    return {
    "navigator_analysis": navigator_analysis,
    "error_snippet": extract_error_snippet(navigator_analysis, state["translated_code"])
}


def driver_node(state: TranslationState,config: RunnableConfig) -> dict:
    provider = config["configurable"]["provider"]
    model_id = config["configurable"]["model_id"]
    target_lng=state['target_lang']
    inp_lng=state['inp_lang']
    input_code=state['input_code']
    translated_code=state['translated_code']
    navigator_analysis=state['navigator_analysis']
    feedback=state['feedback']

    driver_prompt = f'''The translated {target_lng} code failed the test cases against the original {inp_lng} code.
**Original Legacy Code ({inp_lng}):**
{input_code}
**Current Translated Code to Fix ({target_lng}):**
{translated_code}
Navigator Analysis:
{navigator_analysis}

Failed Tests:
{feedback}

CRITICAL FIX REQUIREMENTS:
1. **Apply Navigator Fixes**: Implement the exact logic and boundary fixes identified by the Navigator.
2. **DO NOT HARDCODE VALUES**: The code must continue to read from standard input and process dynamic test cases. Hardcoding to pass a specific test is strictly prohibited.
3. **PRESERVE ENTIRE STRUCTURE**: You must return the FULL, runnable program, including all imports, initializations, standard input reading, and printing. Do not omit or truncate any functions.
4. **EXACT FUNCTIONALITY**: Do not change the underlying algorithm or overall structure.
5. **BYTE-FOR-BYTE MATCH**: Fix the output formatting, precision, spacing, and loop bounds so the output matches the expected test output identically.
6. FIXING VALUEERRORS (I/O): If you see ValueError: not enough values to unpack, it means the test case provided inputs on multiple newlines. Fix this by explicitly reading across multiple lines (e.g., calling input().strip() sequentially). DO NOT split the original print() statement into multiple new prompt strings. You must print the exact original string once, then capture the variables.
7. INTERLEAVED I/O RULE: Legacy Fortran frequently interleaves reading from the terminal (read(5,*)) and reading from external files (open(1...), read(1,*)). When translating to Python, or when suggesting fixes for Python input handling, you MUST NOT use sys.stdin.read(), sys.stdin.readlines(), or sys.stdin iterators. You must use sequential input().strip() calls for terminal inputs to ensure the standard input buffer is perfectly preserved while the external file is being read.

Return ONLY the fully corrected, executable {target_lng} code in a single code block. NO explanations, NO markdown outside the code block.'''

    candidate_code = extract_code(generate_code(driver_prompt, provider, model_id))

    # Mirrors: `if not candidate_code: continue` — but a graph node can't
    # "continue" a Python loop. Simplest equivalent: if empty, just keep
    # the previous translated_code unchanged (don't overwrite with garbage)
    new_code = candidate_code if candidate_code else state["translated_code"]

    with open(state["working_filepath"], "w") as f:
        f.write(new_code)

    return {
        "translated_code": new_code,
        "attempt_count": state["attempt_count"] + 1,
    }



def route_after_tests(state: TranslationState) -> str:
    if state["passed"]:
        return "end"
    if state["attempt_count"] >= state["max_attempts"]:
        return "end"
    return "retrieve"          # subsequent failures — go straight to navigator

graph = StateGraph(TranslationState)

graph.add_node("setup", setup_node)
graph.add_node("translate", translate_node)
graph.add_node("run_tests", run_tests_node)
graph.add_node("navigator", navigator_node)
graph.add_node("driver", driver_node)
graph.add_node("retrieve", retrieve_node)
graph.add_node("store", store_node)

graph.set_entry_point("setup")
graph.add_edge("setup", "translate")
graph.add_edge("translate", "run_tests")
graph.add_edge("store", END)

graph.add_conditional_edges(
    "run_tests",
      route_after_tests,
    {
        "end": "store",      # always go to store first, store decides whether to write
        "retrieve": "retrieve",
    }
)
graph.add_edge("retrieve", "navigator")
graph.add_edge("navigator", "driver")
graph.add_edge("driver", "run_tests")   # loop back

#The psycopg_pool package is an optional,
# highly performant connection pool library built for Psycopg 3. It maintains a cache of open PostgreSQL database connections to minimize latency, eliminate overhead from frequently creating new connections, and support high-concurrency environments
_checkpoint_pool = ConnectionPool(
    conninfo=os.environ["NEON_DATABASE_URL"],
    max_size=20,
    kwargs={"autocommit": True, "prepare_threshold": 0},
    # Neon suspends/drops idle connections server-side; without a check
    # callback, getconn() never notices and hands out a dead socket, which
    # then blows up as "SSL connection has been closed unexpectedly" on
    # whatever query runs first (see auth.py's get_db_connection for the
    # same failure mode on the psycopg2 pool).
    check=ConnectionPool.check_connection,
)
checkpointer = PostgresSaver(_checkpoint_pool)
checkpointer.setup()  # idempotent — creates langgraph's checkpoint tables if missing
app = graph.compile(checkpointer=checkpointer)


# import uuid

# folder_path = "Sample_Codes/Physics_Sample_Codes/Lorenz_Map/"
# input_path = os.path.join(folder_path, "lorenz_map.f")
# test_file = os.path.join(folder_path, "tests.txt")

# input_code = open(input_path, "r").read()
# thread_id = str(uuid.uuid4())

# result = app.invoke(
#     {
#         "input_code": input_code,
#         "inp_lang": "fortran",
#         "target_lang": "python",
#     },
#     config={
#         "configurable": {
#             "thread_id": thread_id,
#             "provider": "groq",
#             "model_id": "llama-3.3-70b-versatile",
#             "tests": parse_tests(test_file),
#         }
#     }
# )

# print(result["translated_code"])
# print(f"Passed: {result['passed']}, Attempts used: {result['attempt_count']}")
