# 🎧 Voice DJ — Spotify Voice Agent

> Control Spotify with your voice using Google Antigravity SDK + Gemini AI

![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Demo Mode](https://img.shields.io/badge/demo%20mode-supported-brightgreen)

## What is this?

**Voice DJ** is an AI agent that listens to voice commands (or text) and controls Spotify in real time. It understands natural language in **Russian and English** and uses [Google Antigravity SDK](https://pypi.org/project/google-antigravity/) with Gemini under the hood.

```
You:  "включи что-нибудь от Дрейка"
DJ:   ▶️ Playing: God's Plan by Drake 🔥
```

## Features

| Command | What happens |
|---------|-------------|
| play / включи | Resume playback |
| pause / стоп | Pause |
| next / следующий | Skip track |
| previous / назад | Go back |
| play [artist/song] | Search & play |
| volume 70 / погромче | Set volume |
| what's playing / что играет | Show current track |
| like / добавь в избранное | Like current track |
| shuffle / перемешай | Toggle shuffle |

## Quick Start

### 1. Clone & install dependencies

```bash
git clone https://github.com/CCGArima/spotify-voice-agent
cd spotify-voice-agent

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

> **macOS:** If `PyAudio` fails, run `brew install portaudio` first.  
> *Note for Apple Silicon (M1/M2/M3):* If you get a `symbol not found` or `dlopen` error, install portaudio via native Homebrew and compile PyAudio with explicit paths:
> ```bash
> /opt/homebrew/bin/brew install portaudio
> CFLAGS="-I/opt/homebrew/opt/portaudio/include" LDFLAGS="-L/opt/homebrew/opt/portaudio/lib" python3 -m pip install --force-reinstall --no-cache-dir pyaudio
> ```
> **Linux:** Run `sudo apt install portaudio19-dev python3-pyaudio`.

### 2. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys (see sections below).

### 3. Run in demo mode (no Spotify needed!)

```bash
python agent.py --demo --text
```

This lets you try everything without a Spotify account. Perfect for testing or showing the project.

---

## Full Setup (with real Spotify)

> ⚠️ **Spotify Premium required** for playback control via the Web API.  
> Free accounts can only use `get_current_track` and `like_current_track`.

### Get a Gemini API key

1. Go to [Google AI Studio](https://aistudio.google.com/app/api-keys)
2. Create a new API key
3. Add to `.env`: `GEMINI_API_KEY=your_key`

### Create a Spotify App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click **Create App**
3. Set **Redirect URI** to `http://localhost:8888/callback`
4. Copy **Client ID** and **Client Secret** to `.env`

### Run with voice

```bash
python agent.py          # voice mode (needs microphone)
python agent.py --text   # text mode (type commands)
python agent.py --demo   # demo mode (no Spotify)
```

On first run, Spotify will open a browser for OAuth. After authorisation, a `.spotify_cache` file is created — you won't need to log in again.

---

## Project Structure

```
spotify-voice-agent/
├── agent.py          # Main entry point — AGY agent + voice/text loop
├── spotify_tools.py  # Spotify API tools (play, pause, search, volume...)
├── voice_input.py    # Microphone capture + Google STT
├── requirements.txt
├── .env.example
└── README.md
```

## How it works

```
Microphone → SpeechRecognition (Google STT)
                      ↓
             AGY Agent (Gemini)
                      ↓
         Spotify tools (spotipy)
                      ↓
           Spotify Web API → 🎵
```

1. `voice_input.py` captures audio from the mic and converts it to text
2. The text is sent to the **Antigravity Agent** with Gemini as the brain
3. Gemini picks the right tool and calls it with correct arguments
4. The tool talks to Spotify API and returns a human-readable result
5. The agent speaks the response back to you

## License

MIT © CCGArima
