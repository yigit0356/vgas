# 🎓 Voice-Guided Academic Solver (VGAS)

VGAS is a cloud-based academic assistant that transforms complex university-level problems from visual input into auditory guidance. The system, which synchronizes a hardware controller (Raspberry Pi) with a powerful cloud backend (Nitro + Gemini), enables students to break down problems step by step onto paper.

---

## ✨ Key Features

-   **Dictation Mode:** Speaks mathematical expressions ($ax^2 + bx + c$) not only as results but also as instructions tailored to your typing speed.
-   **Smart Elimination (MCQ):** Logically explains why incorrect options are eliminated in multiple-choice questions.
-   **LaTeX to Natural Language:** Verbally describes complex formulas (e.g., “Write x squared inside the integral symbol”).
-   **Hybrid Architecture:** Performs heavy processing in the cloud, ensuring minimal resource consumption on the Raspberry Pi.

---

## 🏗️ System Architecture

The project is divided into two main layers for low-latency data processing and high performance:

### 🌐 1. Cloud Server (Cloud/Web) - `/web`

It functions as the central processing unit. It can be hosted on any VPS or Cloud platform.

-   **API Endpoint (`/api/analyze`):** Receives images from the Raspberry Pi.
-   **Intelligence:** Analyzes the problem and establishes the solution logic using the Gemini 1.5 Pro Vision API.
-   **Speech Synthesis:** Converts the solution steps into a natural human voice via the ElevenLabs API.
-   **Technology:** Nitro (UnJS), TypeScript, ElevenLabs SDK, Google Generative AI.

### 🤖 2. Edge Device (Controller) - `/controller`

Manages the physical hardware on the student's desk.

-   **Image Capture:** High-resolution problem capture via Pi Camera.
-   **Communication:** Asynchronously transmits captured data to the Cloud API.
-   **Playback:** Transmits voice commands returned from the server to the student via the speaker.
-   **Technology:** Python/Node.js, Raspberry Pi OS.

---

## 🛠️ Installation

### Cloud Server Installation (`/web`)

```bash
cd web
pnpm install
# Create the .env file:
# GEMINI_API_KEY=...
# ELEVENLABS_API_KEY=...
pnpm dev
```

### Raspberry Pi Setup (`/controller`)

Open the terminal on the Raspberry Pi and run the setup script to prepare the device:

```bash
curl -sSL https://raw.githubusercontent.com/yigit0356/vgas/refs/heads/main/controller_setup.sh | bash
```

Script; automatically configures camera drivers, necessary libraries, and audio output settings.

---

## 🚀 Workflow

1. **Capture**: The student presses the button, and the Raspberry Pi takes a photo.
2. **Upload**: The photo is POSTed to the /api/analyze endpoint in the cloud.
3. **Process**: The cloud server solves the question with Gemini and narrates it with ElevenLabs.
4. **Execute**: The Raspberry Pi plays the received audio file to guide the student.

---

## ⚖️ Purpose of Use and Ethical Note

This tool was developed as a “personal tutor” concept, especially for students who adopt an **auditory learning model** and individuals with disabilities such as **visual impairment/dyslexia**. It is recommended to be used within the framework of academic integrity to support the learning process.

---

## 🤝 Katkıda Bulunma

1. Fork the project.
2. Create a new Feature Branch (git checkout -b feature/NewFeature).
3. Commit your changes.
4. Create a Pull Request.
