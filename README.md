# VoiceFlow AI

VoiceFlow AI is a Windows desktop voice-to-text assistant built with Python, PyQt6, Faster-Whisper, sounddevice, pyautogui, and global hotkeys.

It captures microphone audio, transcribes speech offline with Faster-Whisper, and types the recognized text into the currently active Windows application.

## Features

- Offline speech recognition with Faster-Whisper
- Real-time microphone capture
- Global hotkeys:
  - `Ctrl + Shift + V` starts listening
  - `Ctrl + Shift + C` stops listening
- Types into active apps such as Cursor, Chrome, VS Code, Notepad, Word, ChatGPT, and other Windows software
- Floating microphone indicator while recording
- PyQt6 Windows 11-style dark UI
- System tray support
- Startup-on-Windows option
- Local speech history in SQLite
- Auto punctuation and spoken punctuation commands
- Noise reduction and silence detection
- Multi-language support
- Wake word mode using `Hey VoiceFlow`
- Optional AI processing mode
- Cursor coding mode that focuses Cursor when available and submits dictated prompts there

## Project Structure

```text
VoiceFlow AI/
  main.py
  requirements.txt
  voiceflow_ai.spec
  ui/
  models/
  audio/
  services/
  settings/
```

## Installation

Python 3.10 or 3.11 is recommended on Windows.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Faster-Whisper downloads the selected model on first use. After the model is cached, transcription can run offline.

You can also run:

```powershell
.\scripts\install.ps1
```

## Run

```powershell
python main.py
```

Windows may ask for microphone access. The `keyboard` package can require administrator privileges for global hotkeys on some systems.

## Settings

Open the app and click the settings button to configure:

- Whisper model size
- Language
- Compute type
- Microphone input device
- Wake word mode
- Auto punctuation
- AI mode
- Cursor coding mode
- Startup on Windows

Settings are saved locally at:

```text
%APPDATA%\VoiceFlowAI\settings.json
```

History is saved locally at:

```text
%APPDATA%\VoiceFlowAI\history.db
```

## Optional AI Mode

AI mode is intentionally provider-neutral. To enable cloud AI processing, set:

```powershell
$env:VOICEFLOW_AI_ENDPOINT="https://your-api-endpoint.example.com/v1/chat/completions"
$env:VOICEFLOW_AI_KEY="your-api-key"
$env:VOICEFLOW_AI_MODEL="your-model-name"
```

If no endpoint is configured, AI mode uses a local cleanup pass so the app still works.

## Build Standalone EXE

```powershell
.\.venv\Scripts\Activate.ps1
pyinstaller voiceflow_ai.spec
```

The executable will be created under:

```text
dist\VoiceFlow AI.exe
```

You can also run:

```powershell
.\scripts\build.ps1
```

For best results, build on the same Windows version and architecture you plan to run on.

## Notes

- The app types text into the active foreground window using `pyautogui.write`.
- Faster-Whisper performance depends on CPU/GPU and selected model size.
- For GPU acceleration, install the CUDA/CuDNN stack supported by faster-whisper/CTranslate2.
- Some enterprise security software may restrict global hotkeys, background microphone capture, or automated typing.
