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
