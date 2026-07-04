# Automated Translation of Legacy Scientific Codes via LLMs

An advanced, three-phase autonomous agentic framework designed to translate, iteratively debug, and optimize legacy scientific codebases (e.g., Fortran) into modern programming environments like Python without sacrificing mathematical precision or structural correctness.

Developed as a B.Tech Mini Project at Dhirubhai Ambani University under the guidance of Prof. Bhaskar Chaudhury and Research Assistant Libin Varghese with my batchmate Jainil Patel.

---

## 🚀 Motivation
* **Legacy Language Limitations:** Massive scientific codebases remain locked in legacy languages like Fortran, making them hard to port to modern parallel architectures or GPUs.
* **The Skills Gap:** Modern software engineers and researchers are rarely trained in Fortran, creating a severe software sustainability hurdle.
* **High Migration Costs:** Manual translations are incredibly slow, error-prone, and expensive. This pipeline provides a scalable, automated alternative.

---

## 🛠️ Architecture & Methodology
The pipeline operates in three distinct, automated phases to ensure a zero-tolerance, byte-for-byte output match with the legacy system:

1. **Phase 1: Strict Translation:** Enforces rigid, literature-derived prompt rules regarding strict numeric types, array boundaries, language-specific syntax conversions, and precise I/O formatting rules.
2. **Phase 2: Navigator-Driver Error Correction:** If execution testing fails, an independent **Navigator LLM** parses the runtime traceback error to isolate the root cause, outputting clean JSON-formatted hints[cite: 2, 3]. A **Driver LLM** consumes these hints to dynamically repair the broken parts of the program until the verification test suite achieves a 100% match.
3. **Phase 3: Performance Optimization:** Goal in this phase is to enhance the algorithmic performance alongside using human-like exclusionary reasoning to benchmark live time/memory usages. Process is  aborted automatically if modifications trigger harmful over-optimization.

---

## 📈 Cross-Architecture Benchmarking Results
The system was evaluated against multiple open-weight and proprietary models utilizing deterministic algorithms (Binary Search) and multi-method ordinary differential equation (ODE) physics simulations from Giordano & Nakanishi's *Computational Physics*:

### 1. Baseline Verification (Binary Search)
| Model | Compilation / Test Iterations | Legacy Run Time | Translated Run Time |
| :--- | :---: | :---: | :---: |
| **gpt-4o-mini** | 2 | 255.78 ms | 29.12 ms |
| **gpt-4o** | 3 | 255.47 ms | 29.72 ms |
| **llama-3.3-70b-versatile** | 2 | 263.15 ms | 28.17 ms |
| **nemotron-120b** | 1 | 272.05 ms | 29.33 ms |

### 2. Domain-Specific Physics Simulation (`nuclear_decay.f`)
Numerically solves $\frac{dN}{dt} = -\frac{N}{\tau}$ across multiple numerical approximation methods (Euler, 2nd & 4th order Runge-Kutta)[cite: 3]:
* **gpt-4o / llama-3.3-70b-versatile:** Successfully translated with strict byte-for-byte alignment to the underlying mathematical constants and float precision[cite: 3].
---
### Approach used
- Vector store: PGVector on NeonDB
- Embeddings: sentence-transformers/all-MiniLM-L6-v2 via HuggingFace
- Retrieval strategy: metadata pre-filter (language pair) + dense retrieval + MMR
- Storage pattern: parent document retriever (embed error context, retrieve full pair)
# 📚 Parent Document Retriever

## Why not Generic RAG?
limitation of generic rag approach:

- Small chunks improve retrieval accuracy.
- Small chunks often **lack enough context** for the LLM to generate high-quality answers.

---

# Parent Document Retriever

A **Parent Document Retriever** separates:

- **What is searched against**
- **What is returned to the LLM**

Instead of storing only one chunk, it maintains two representations:

- **Child Documents** → Used for semantic search (errors basically)
- **Parent Documents** → Returned as context    (The entire {error, fix} pairs)

```text
Child Chunk
      │
      ▼
Embed Child Chunk
      │
      ▼
Vector Store (Searchable)

──────────────────────────────────────

Full Parent Document
      │
      ▼
Document Store (Keyed by Parent ID)
```

---

## Retrieval Pipeline

```text
User Query
      │
      ▼
Embed Query
      │
      ▼
Search Child Vectors
      │
      ▼
Retrieve Parent IDs
      │
      ▼
Fetch Full Parent Documents
      │
      ▼
Provide Rich Context to the LLM
```

---

# Generic RAG vs Parent Retriever

| Generic RAG | Parent Retriever |
|-------------|------------------|
| Searches chunks | Searches child chunks |
| Returns the same chunk | Returns the full parent document |
| High precision, low context | High precision with rich context |
| May lose surrounding information | Preserves complete context |

---

## Child Document (Search Target)

This contains only the **navigator analysis**.

```text
navigator_analysis
```

This is embedded and stored in the **vector database** because it best represents the error semantics.

---

## Parent Document (Returned Context)

The parent document contains everything needed to solve a similar issue.

```text
{
    navigator_analysis,
    working_fix,
    language_pair,
    attempt_context
}
```

This is stored inside the **Document Store**, indexed using the parent ID.

---

# Retrieval Flow

When a new error arrives:

```text
New Navigator Analysis
           │
           ▼
Generate Embedding
           │
           ▼
Search Similar Navigator Analyses
           │
           ▼
Obtain Matching Parent IDs
           │
           ▼
Retrieve Complete Parent Documents
           │
           ▼
Send Rich Context to the LLM
```

---

# Why This Matters

Suppose the user encounters a new compiler or runtime error.

The goal is **not** to retrieve an isolated chunk.

Instead:

1. Find previous errors with **similar navigator analyses**.
2. Retrieve the **entire debugging context** that solved those errors.
3. Provide the LLM with:
   - Original error analysis
   - Working fix
   - Programming language pair
   - Previous debugging attempts

This enables the model to reason using complete historical solutions instead of incomplete fragments.

---

# Key Insight

> **Search against the child. Return the parent.**

Searching against small child chunks provides **better retrieval precision**, while returning the larger parent document provides **better reasoning context** for the LLM.



