"""
voice_input.py — Microphone capture and speech-to-text.

Uses SpeechRecognition with Google's free STT API.
Falls back gracefully if microphone/audio is unavailable.
"""

import sys
import speech_recognition as sr
from colorama import Fore, Style


def listen_once(timeout: int = 5, phrase_limit: int = 8) -> str | None:
    """Listen to the microphone for one voice command.

    Args:
        timeout: Seconds to wait for speech to start.
        phrase_limit: Max seconds for a single phrase.

    Returns:
        Recognised text string, or None if nothing was heard / recognition failed.
    """
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    try:
        with sr.Microphone() as source:
            print(f"{Fore.CYAN}🎙️  Listening...{Style.RESET_ALL}", end=" ", flush=True)
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)

        print(f"{Fore.YELLOW}⚙️  Recognising...{Style.RESET_ALL}", end=" ", flush=True)
        text = recognizer.recognize_google(audio, language="ru-RU,en-US")
        print(f"{Fore.GREEN}✅{Style.RESET_ALL}")
        return text

    except sr.WaitTimeoutError:
        print(f"{Fore.YELLOW}(silence){Style.RESET_ALL}")
        return None
    except sr.UnknownValueError:
        print(f"{Fore.RED}(couldn't understand){Style.RESET_ALL}")
        return None
    except sr.RequestError as e:
        print(f"{Fore.RED}❌ STT API error: {e}{Style.RESET_ALL}")
        return None
    except OSError:
        # No microphone available (e.g. CI/server environment)
        print(f"\n{Fore.RED}❌ No microphone found.{Style.RESET_ALL}")
        print("   Run in text mode with:  python agent.py --text")
        return None


def check_microphone() -> bool:
    """Return True if a microphone is available."""
    try:
        with sr.Microphone():
            return True
    except OSError:
        return False
