"""
agent.py — Voice DJ: a voice-controlled Spotify agent powered by Google Antigravity SDK.

Usage:
    python agent.py               # voice mode (requires microphone)
    python agent.py --text        # text mode (type commands in terminal)
    python agent.py --demo        # force demo mode (no Spotify account needed)
"""

import asyncio
import argparse
import os
import sys

from dotenv import load_dotenv
from colorama import Fore, Style, init as colorama_init

load_dotenv()
colorama_init()

# ── Antigravity SDK ────────────────────────────────────────────────────────
from google.antigravity import Agent, LocalAgentConfig

# ── Project modules ────────────────────────────────────────────────────────
import spotify_tools
from voice_input import listen_once, check_microphone

# ── Banner ─────────────────────────────────────────────────────────────────
BANNER = f"""
{Fore.GREEN}╔══════════════════════════════════════════╗
║  🎧  Voice DJ — Spotify Voice Agent      ║
║      powered by Google Antigravity SDK   ║
╚══════════════════════════════════════════╝{Style.RESET_ALL}
"""

SYSTEM_PROMPT = """You are Voice DJ — a friendly, enthusiastic AI DJ that controls Spotify
through voice commands. You speak naturally and keep responses short (1-2 sentences max).

You have access to these Spotify tools:
- play_music        → resume playback
- pause_music       → pause
- next_track        → skip to next
- previous_track    → go back
- search_and_play   → find and play a song/artist
- set_volume        → change volume (0-100)
- get_current_track → show what's playing
- like_current_track → add to liked songs
- shuffle_toggle    → toggle shuffle

RULES:
1. Always call a tool — never just describe what you would do.
2. After the tool returns its result, briefly confirm what happened.
3. If the user says something unrelated to music, politely redirect.
4. Support both Russian and English commands.
5. Be enthusiastic! Add emojis 🎵🔥✨ to keep the vibe going.

Example responses:
- User: "следующий" → call next_track(), say "Skipping! 🎵 Let's see what's next..."
- User: "включи Дрейка" → call search_and_play("Drake"), confirm result
- User: "что играет?" → call get_current_track(), share the info
"""


async def run_agent(text_mode: bool = False, demo_mode: bool = False):
    """Main agent loop."""

    # Override demo mode if flag passed
    if demo_mode:
        os.environ["DEMO_MODE"] = "true"
        spotify_tools.DEMO_MODE = True

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print(f"{Fore.RED}❌ GEMINI_API_KEY not set.{Style.RESET_ALL}")
        print(f"   Copy .env.example → .env and add your key.")
        print(f"   Get one free at: https://aistudio.google.com/app/api-keys")
        sys.exit(1)

    # Build agent config with all Spotify tools
    config = LocalAgentConfig(
        api_key=api_key,
        system_instructions=SYSTEM_PROMPT,
        tools=[
            spotify_tools.play_music,
            spotify_tools.pause_music,
            spotify_tools.next_track,
            spotify_tools.previous_track,
            spotify_tools.search_and_play,
            spotify_tools.set_volume,
            spotify_tools.get_current_track,
            spotify_tools.like_current_track,
            spotify_tools.shuffle_toggle,
        ],
    )

    print(BANNER)

    mode_label = "DEMO" if spotify_tools.DEMO_MODE else "LIVE"
    mode_color = Fore.YELLOW if spotify_tools.DEMO_MODE else Fore.GREEN
    print(f"{mode_color}  Mode: {mode_label}{Style.RESET_ALL}")

    if text_mode:
        print(f"{Fore.CYAN}  Input: TEXT (type your commands below){Style.RESET_ALL}")
    else:
        if not check_microphone():
            print(f"{Fore.YELLOW}  ⚠️  No microphone detected → switching to text mode.{Style.RESET_ALL}")
            text_mode = True
        else:
            print(f"{Fore.CYAN}  Input: VOICE (speak your commands){Style.RESET_ALL}")

    print(f"\n{Fore.WHITE}  Say or type commands like:{Style.RESET_ALL}")
    print(f"    • play / pause / next / previous")
    print(f"    • play Drake / включи Хабиби")
    print(f"    • what's playing / что играет")
    print(f"    • volume 70 / погромче / потише")
    print(f"    • like / добавь в избранное")
    print(f"    • quit / exit / выход{Style.RESET_ALL}")
    print(f"\n{Fore.WHITE}{'─' * 44}{Style.RESET_ALL}\n")

    async with Agent(config) as agent:
        while True:
            try:
                # ── Get user input ───────────────────────────────────────
                if text_mode:
                    try:
                        user_input = input(f"{Fore.MAGENTA}You ▶  {Style.RESET_ALL}").strip()
                    except (EOFError, KeyboardInterrupt):
                        break
                else:
                    user_input = listen_once()
                    if user_input:
                        print(f"{Fore.MAGENTA}You ▶  {Style.RESET_ALL}{user_input}")

                if not user_input:
                    continue

                # ── Exit commands ────────────────────────────────────────
                if user_input.lower() in {"quit", "exit", "q", "выход", "стоп агент"}:
                    print(f"\n{Fore.GREEN}🎧 Voice DJ signing off. Keep the music alive! 🎵{Style.RESET_ALL}")
                    break

                # ── Send to agent ────────────────────────────────────────
                print(f"{Fore.GREEN}DJ ▶  {Style.RESET_ALL}", end="", flush=True)
                response = await agent.chat(user_input)
                async for chunk in response:
                    print(chunk, end="", flush=True)
                print("\n")

            except KeyboardInterrupt:
                print(f"\n\n{Fore.GREEN}🎧 Stopped. Peace! ✌️{Style.RESET_ALL}")
                break


def main():
    parser = argparse.ArgumentParser(
        description="🎧 Voice DJ — control Spotify with your voice"
    )
    parser.add_argument(
        "--text",
        action="store_true",
        help="Use text input instead of microphone",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode (no Spotify account needed)",
    )
    args = parser.parse_args()
    asyncio.run(run_agent(text_mode=args.text, demo_mode=args.demo))


if __name__ == "__main__":
    main()
