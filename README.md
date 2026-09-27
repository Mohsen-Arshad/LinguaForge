# LinguaForge

<p align="center">
  <img src="assets/linguaforge_logo.png" alt="LinguaForge logo" width="110">
</p>

<h1 align="center">LinguaForge</h1>

<p align="center">
  A local desktop studio for generating natural multi-speaker audio with Chatterbox Turbo.
  <br>
  Built for English shadowing, dialogue practice, and scripted conversations.
</p>

<p align="center">
  <strong>Free • Open Source • Local</strong>
</p>

---

## Overview

LinguaForge is a Windows desktop application for generating speech locally with **Chatterbox Turbo**.

The project started as a shadowing-focused TTS tool, but it has grown into a small dialogue studio. You can generate single-speaker practice material, build conversations with multiple voices, control pauses between lines, and export the result as MP3.

Everything runs locally on the user's machine after the environment is installed.

### What you can use it for

- English shadowing practice
- Pronunciation and listening exercises
- Single-speaker TTS
- Multi-speaker conversations
- Movie / TV-style dialogue generation
- Scripted character conversations
- Custom voice references
- Adjustable speech speed and generation settings
- MP3 export with selectable bitrate
- Local CUDA acceleration

> **Note:** LinguaForge is currently focused on English because the current generation pipeline and project design have been tested around English speech.

---

## Screenshots

> **Add your screenshots here.**
>
> Recommended folder:
>
> `docs/screenshots/`
>
> Suggested files:
>
> - `generate.png`
> - `speakers.png`
> - `system.png`
> - `dialogue.png`

### Generate

<!-- Replace the path below with your screenshot -->
![Generate page](docs/screenshots/generate.png)

### Speakers

<!-- Replace the path below with your screenshot -->
![Speakers page](docs/screenshots/speakers.png)

### System

<!-- Replace the path below with your screenshot -->
![System page](docs/screenshots/system.png)

### Dialogue generation

<!-- Replace the path below with your screenshot -->
![Dialogue generation](docs/screenshots/dialogue.png)

---

## Features

### 🎙️ Local TTS generation

Generate speech locally using Chatterbox Turbo instead of relying on a paid cloud API.

### 👥 Multiple speakers

Define several speakers and use them inside a script:

```text
[speaker1] Hey, are you ready? [2]
[speaker2] Almost. Give me a minute. [1.5]
[speaker1] Sure. [2]
```

### 🎬 Dialogue generation

LinguaForge can be used for scripted conversations and movie-style dialogue.

For example:

```text
[speaker1] Did you see what happened?
[speaker2] No. What happened?
[speaker1] They found the car.
[speaker2] Then we should leave.
```

Each line can use a different voice reference.

### ⏱️ Sentence pauses

Add a pause after a line with:

```text
[2]
```

or:

```text
[2.5]
```

If a line does not specify a pause, LinguaForge can use the default pause behavior rather than dropping the line.

### ⚡ CUDA acceleration

The project is configured around a known-good CUDA/PyTorch combination:

- PyTorch `2.6.0+cu124`
- TorchVision `0.21.0+cu124`
- TorchAudio `2.6.0+cu124`

A compatible NVIDIA GPU is recommended for practical generation speed.

### 🔊 MP3 export

Generated audio can be exported to MP3 with selectable bitrate:

- 128 kbps
- 160 kbps
- 192 kbps
- 256 kbps
- 320 kbps

### 🧰 Built-in system diagnostics

The **System** page checks the runtime environment and provides dependency/install/repair functionality.

LinguaForge also caches a successful environment check so it does not waste time repeating the same expensive checks on every startup.

---

# Installation

## Requirements

LinguaForge is currently intended for:

- Windows
- Python 3.11
- NVIDIA GPU with CUDA support recommended
- FFmpeg
- Internet connection for the initial dependency/model setup

The project uses a pinned PyTorch/Chatterbox environment because mixing arbitrary versions can break the TTS stack.

## Easiest setup

If you are using a fresh Windows installation:

1. Clone or download the repository.
2. Make sure Python 3.11 is installed.
3. Run:

```text
setup.bat
```

4. Wait for the setup process to finish.
5. Start the application with:

```text
run.bat
```

The goal of `setup.bat` is to make the first-run experience as simple as possible, even for someone who does not normally work with Python environments.

---

# Manual setup

Create the virtual environment:

```powershell
py -3.11 -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

Install the pinned runtime:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Then run:

```powershell
python run.py
```

---

# Important dependency note

LinguaForge intentionally pins:

```text
setuptools==80.10.2
```

This is not an arbitrary version choice.

The Chatterbox/Perth watermarking stack used by the project relies on `pkg_resources`, and newer setuptools versions can remove or break that compatibility.

For that reason, avoid blindly upgrading every package in the environment.

The known-good core combination is:

```text
torch==2.6.0+cu124
torchvision==0.21.0+cu124
torchaudio==2.6.0+cu124
chatterbox-tts==0.1.7
resemble-perth==1.0.1
setuptools==80.10.2
```

---

# Project structure

```text
LinguaForge/
│
├── app/
│   ├── models/
│   │   ├── events.py
│   │   ├── generation.py
│   │   └── speaker.py
│   │
│   ├── services/
│   │   ├── audio_generator.py
│   │   ├── dialogue_parser.py
│   │   ├── pause_service.py
│   │   ├── speaker_repository.py
│   │   └── system_service.py
│   │
│   ├── ui/
│   │   ├── generate_view.py
│   │   ├── main_window.py
│   │   ├── speakers_view.py
│   │   ├── system_view.py
│   │   ├── theme.py
│   │   └── widgets.py
│   │
│   ├── utils/
│   │   └── threading_utils.py
│   │
│   └── main.py
│
├── assets/
│   ├── linguaforge_logo.png
│   └── linguaforge_logo.ico
│
├── tests/
│   ├── test_dialogue_parser.py
│   └── test_pause_service.py
│
├── run.py
├── run.bat
├── setup.bat
├── requirements.txt
├── speakers.json
├── ARCHITECTURE.md
└── README.md
```

The application is intentionally separated into UI, models, services, and utilities instead of putting the entire program into one large Python file.

---

# Input format

## Single speaker

```text
I wake up early every morning. [3]
I drink coffee before work. [2.5]
Then I go to the gym. [2]
```

## Multiple speakers

```text
[speaker1] Hey, how are you? [2]
[speaker2] I'm doing great. How about you? [2]
[speaker1] I'm good too. [2]
```

The final number represents the pause after that line.

For example:

```text
[speaker1] Hello. [3]
```

means:

> Generate "Hello." → wait 3 seconds → continue.

---

# Voice / Speaker references

Speakers are configured through the application's speaker management interface.

A speaker can have a local reference audio file which is used by the generation pipeline.

The repository keeps speaker configuration separate from the actual generation logic so the UI does not need to know how the audio engine works internally.

---

# Architecture

At a high level, LinguaForge follows a layered structure:

```text
┌──────────────────────────────┐
│          Presentation        │
│  MainWindow / Views / Widgets│
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│          Application          │
│ Controllers / Services / Flow │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│            Models             │
│ Generation / Speaker / Events │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│        Infrastructure         │
│ Chatterbox / PyTorch / Audio  │
│ FFmpeg / Filesystem / System  │
└──────────────────────────────┘
```

The important idea is that the UI should not have to understand the internals of Chatterbox, CUDA, FFmpeg, or speaker-file management.

For a deeper explanation of the architecture, see:

```text
ARCHITECTURE.md
```

---

# Performance and startup

The first environment check can take noticeably longer because LinguaForge has to verify the runtime.

After a successful validation, the result is stored in:

```text
.runtime_cache.json
```

That file is intentionally **not committed to Git**.

On later launches, LinguaForge can use the cached validation result instead of repeatedly performing the full dependency scan.

If the environment changes, the cache can be refreshed from the System page.

---

# Testing

The project currently includes tests for core parsing/pause behavior:

```powershell
python -m pytest
```

If pytest is not installed:

```powershell
python -m pip install pytest
```

The most important parts to test independently are:

- dialogue parsing
- pause handling
- speaker selection
- generation configuration
- export behavior

---

# Development

A useful development workflow is:

```text
Change code
   ↓
Run tests
   ↓
Run application
   ↓
Test the affected workflow
   ↓
Check System page
   ↓
Commit only source/configuration changes
```

Avoid committing:

- virtual environments
- Python bytecode
- generated MP3 files
- local runtime caches
- downloaded model weights
- wheels
- IDE metadata
- temporary files

The repository `.gitignore` is configured for these cases.

---

# Contributing

If you want to improve LinguaForge:

1. Fork the repository.
2. Create a branch for your change.
3. Keep changes focused.
4. Add or update tests when behavior changes.
5. Test the application locally.
6. Open a pull request with a short explanation of the change.

For larger architectural changes, explain the reason for the change before changing multiple layers of the application.

---

# Project status

LinguaForge is an actively developed open-source project.

The current focus is a stable local desktop experience with:

- Chatterbox Turbo
- CUDA acceleration
- multi-speaker generation
- dialogue support
- configurable pauses
- MP3 export
- a Fluent-style desktop UI
- first-run environment setup and repair

---

# License

No license has been added to this repository yet.

If you publish the project publicly, add a `LICENSE` file with the license you actually intend to use.

Also review the licenses of the dependencies used by LinguaForge before redistributing the application.

---

# Screenshots / media folder

For GitHub screenshots, create:

```text
docs/
└── screenshots/
    ├── generate.png
    ├── speakers.png
    ├── system.png
    └── dialogue.png
```

Then the README images above will work automatically.

You can also add a short demo GIF here later:

```text
docs/
└── demo.gif
```

and embed it with:

```markdown
![LinguaForge demo](docs/demo.gif)
```

---

<p align="center">
  Made for local speech generation, language learning, and dialogue creation.
</p>
