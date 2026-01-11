# Voice-Guided Academic Solver (VGAS) 🎓🎙️

**Voice-Guided Academic Solver** is an AI-powered educational assistant designed to transform the way students solve complex university-level problems. By bridging the gap between visual input and auditory guidance, VGAS allows students to take a photo of a problem and receive real-time, step-by-step voice instructions to solve and write it down manually on paper.

---

## 🌟 Vision

The primary goal of VGAS is to provide a "Personal Tutor" experience. Unlike traditional solvers that just show a static result, VGAS narrates the **methodology**, ensuring the student understands the logic and can physically document the process.

## ✨ Key Features

-   **Multimodal AI Processing:** High-accuracy recognition of handwritten formulas, mathematical notations, and complex text.
-   **"Dictation Mode":** Specifically designed speech patterns that guide the student's hand.
-   **Multiple-Choice Strategy (MCQ):** \* Analyzes all options (A, B, C, D, E).
    -   Explains the **elimination process** (Why A is wrong, why C is a distractor).
    -   Provides the logical path to the correct option.
-   **Adaptive Learning Pace:** Users can control the speed of narration or ask for repetitions via voice commands.
-   **LaTeX to Descriptive Speech:** Converts complex mathematical symbols into natural verbal instructions.

## 🛠️ Technology Stack

-   **Backend:** [Nitro](https://nitro.unjs.io/) (Server Engine)
-   **Language:** TypeScript
-   **AI Engine:** Gemini 1.5 Pro / Vision API
-   **Prompt Engineering:** Structured Markdown-based prompt management
-   **Package Manager:** pnpm

## 🚀 Workflow

1.  **Capture:** Student snaps a photo of a problem (Open-ended or Multiple-choice).
2.  **Analyze:** The AI identifies the problem type.
3.  **Strategic Processing:**
    -   _For Open-ended:_ Generates step-by-step derivation.
    -   _For MCQ:_ Evaluates each option and identifies the correct one through logical elimination.
4.  **Narrate:** The TTS engine reads the instructions aloud, pausing for the student to write.

## 🎯 Target Audience

-   University students in STEM fields (Science, Technology, Engineering, Math).
-   Students with visual impairments or learning disabilities.
-   Auditory learners who retain information better through hearing.

## 🤝 Contributing

This project was written for the purpose of cheating on exams. Please do not use it for any other purpose.
