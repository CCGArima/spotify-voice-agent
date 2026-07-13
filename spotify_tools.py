"""
spotify_tools.py — Spotify API tools for the Voice DJ Agent.

Supports two modes:
  - DEMO_MODE=true  → mock responses, no Spotify account needed
  - DEMO_MODE=false → real Spotify Web API (requires Premium for playback control)
"""

import os
import random
from dotenv import load_dotenv

load_dotenv()

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# ---------------------------------------------------------------------------
# Mock data for demo mode
# ---------------------------------------------------------------------------
_DEMO_LIBRARY = [
    {"name": "Blinding Lights", "artist": "The Weeknd", "uri": "demo:track:1"},
    {"name": "As It Was", "artist": "Harry Styles", "uri": "demo:track:2"},
    {"name": "Heat Waves", "artist": "Glass Animals", "uri": "demo:track:3"},
    {"name": "Flowers", "artist": "Miley Cyrus", "uri": "demo:track:4"},
    {"name": "Unholy", "artist": "Sam Smith", "uri": "demo:track:5"},
    {"name": "Anti-Hero", "artist": "Taylor Swift", "uri": "demo:track:6"},
    {"name": "Calm Down", "artist": "Rema & Selena Gomez", "uri": "demo:track:7"},
    {"name": "Levitating", "artist": "Dua Lipa", "uri": "demo:track:8"},
]

_demo_state = {
    "playing": False,
    "current_index": 0,
    "volume": 50,
    "liked": set(),
}


def _demo_current_track():
    t = _DEMO_LIBRARY[_demo_state["current_index"]]
    return t


# ---------------------------------------------------------------------------
# Real Spotify client (lazy-loaded)
# ---------------------------------------------------------------------------
_sp = None


def _get_spotify():
    global _sp
    if _sp is None:
        import spotipy
        from spotipy.oauth2 import SpotifyOAuth

        scope = (
            "user-read-playback-state "
            "user-modify-playback-state "
            "user-read-currently-playing "
            "user-library-modify "
            "user-library-read"
        )
        _sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
                redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:8888/callback"),
                scope=scope,
                cache_path=".spotify_cache",
            )
        )
    return _sp


# ---------------------------------------------------------------------------
# Tool functions (called by the AGY agent)
# ---------------------------------------------------------------------------

def play_music() -> str:
    """Resume or start music playback on Spotify.

    Use this when the user says: play, resume, start, включи, воспроизведи.
    """
    if DEMO_MODE:
        _demo_state["playing"] = True
        t = _demo_current_track()
        return f"▶️ [DEMO] Playing: {t['name']} by {t['artist']}"
    try:
        sp = _get_spotify()
        sp.start_playback()
        current = sp.current_playback()
        if current and current.get("item"):
            track = current["item"]["name"]
            artist = current["item"]["artists"][0]["name"]
            return f"▶️ Playing: {track} by {artist}"
        return "▶️ Playback started."
    except Exception as e:
        return f"❌ Could not start playback: {e}"


def pause_music() -> str:
    """Pause music playback on Spotify.

    Use this when the user says: pause, stop, стоп, пауза, останови.
    """
    if DEMO_MODE:
        _demo_state["playing"] = False
        return "⏸️ [DEMO] Music paused."
    try:
        _get_spotify().pause_playback()
        return "⏸️ Music paused."
    except Exception as e:
        return f"❌ Could not pause: {e}"


def next_track() -> str:
    """Skip to the next track on Spotify.

    Use this when the user says: next, skip, следующий, дальше, пропусти.
    """
    if DEMO_MODE:
        _demo_state["current_index"] = (_demo_state["current_index"] + 1) % len(_DEMO_LIBRARY)
        t = _demo_current_track()
        return f"⏭️ [DEMO] Now playing: {t['name']} by {t['artist']}"
    try:
        sp = _get_spotify()
        sp.next_track()
        import time; time.sleep(0.5)
        current = sp.current_playback()
        if current and current.get("item"):
            track = current["item"]["name"]
            artist = current["item"]["artists"][0]["name"]
            return f"⏭️ Skipped! Now: {track} by {artist}"
        return "⏭️ Skipped to next track."
    except Exception as e:
        return f"❌ Could not skip: {e}"


def previous_track() -> str:
    """Go back to the previous track on Spotify.

    Use this when the user says: previous, back, предыдущий, назад, вернись.
    """
    if DEMO_MODE:
        _demo_state["current_index"] = (_demo_state["current_index"] - 1) % len(_DEMO_LIBRARY)
        t = _demo_current_track()
        return f"⏮️ [DEMO] Now playing: {t['name']} by {t['artist']}"
    try:
        sp = _get_spotify()
        sp.previous_track()
        import time; time.sleep(0.5)
        current = sp.current_playback()
        if current and current.get("item"):
            track = current["item"]["name"]
            artist = current["item"]["artists"][0]["name"]
            return f"⏮️ Going back! Now: {track} by {artist}"
        return "⏮️ Went back to previous track."
    except Exception as e:
        return f"❌ Could not go back: {e}"


def search_and_play(query: str) -> str:
    """Search for a song or artist on Spotify and play it.

    Use this when the user says: play [song/artist], включи [название], поставь [исполнитель].

    Args:
        query: The song title, artist name, or both to search for.
    """
    if DEMO_MODE:
        # Find best match in demo library
        query_lower = query.lower()
        for track in _DEMO_LIBRARY:
            if query_lower in track["name"].lower() or query_lower in track["artist"].lower():
                _demo_state["current_index"] = _DEMO_LIBRARY.index(track)
                _demo_state["playing"] = True
                return f"▶️ [DEMO] Found and playing: {track['name']} by {track['artist']}"
        # Random fallback
        pick = random.choice(_DEMO_LIBRARY)
        _demo_state["current_index"] = _DEMO_LIBRARY.index(pick)
        _demo_state["playing"] = True
        return f"▶️ [DEMO] Couldn't find '{query}', playing: {pick['name']} by {pick['artist']}"
    try:
        sp = _get_spotify()
        results = sp.search(q=query, type="track", limit=1)
        tracks = results["tracks"]["items"]
        if not tracks:
            return f"❌ No results found for '{query}'."
        track = tracks[0]
        sp.start_playback(uris=[track["uri"]])
        return f"▶️ Playing: {track['name']} by {track['artists'][0]['name']}"
    except Exception as e:
        return f"❌ Search/play failed: {e}"


def set_volume(level: int) -> str:
    """Set the Spotify playback volume.

    Use this when the user says: volume up, louder, volume down, quieter,
    погромче, потише, громкость, убавь, прибавь.

    Args:
        level: Volume percentage from 0 to 100.
    """
    level = max(0, min(100, level))
    if DEMO_MODE:
        _demo_state["volume"] = level
        bar = "█" * (level // 10) + "░" * (10 - level // 10)
        return f"🔊 [DEMO] Volume set to {level}% [{bar}]"
    try:
        _get_spotify().volume(level)
        bar = "█" * (level // 10) + "░" * (10 - level // 10)
        return f"🔊 Volume: {level}% [{bar}]"
    except Exception as e:
        return f"❌ Could not set volume: {e}"


def get_current_track() -> str:
    """Get the currently playing track info from Spotify.

    Use this when the user asks: what's playing, что играет, какая песня,
    what song is this, кто поёт.
    """
    if DEMO_MODE:
        if not _demo_state["playing"]:
            return "⏹️ [DEMO] Nothing is playing right now."
        t = _demo_current_track()
        vol = _demo_state["volume"]
        return (
            f"🎵 [DEMO] Now playing:\n"
            f"   Track:  {t['name']}\n"
            f"   Artist: {t['artist']}\n"
            f"   Volume: {vol}%"
        )
    try:
        sp = _get_spotify()
        current = sp.current_playback()
        if not current or not current.get("is_playing"):
            return "⏹️ Nothing is playing right now."
        item = current["item"]
        track = item["name"]
        artist = ", ".join(a["name"] for a in item["artists"])
        album = item["album"]["name"]
        progress_ms = current["progress_ms"]
        duration_ms = item["duration_ms"]
        progress = f"{progress_ms // 60000}:{(progress_ms % 60000) // 1000:02d}"
        duration = f"{duration_ms // 60000}:{(duration_ms % 60000) // 1000:02d}"
        return (
            f"🎵 Now playing:\n"
            f"   Track:  {track}\n"
            f"   Artist: {artist}\n"
            f"   Album:  {album}\n"
            f"   Time:   {progress} / {duration}"
        )
    except Exception as e:
        return f"❌ Could not get current track: {e}"


def like_current_track() -> str:
    """Add the currently playing track to the user's Spotify liked songs.

    Use this when the user says: like this, add to favorites, лайк,
    добавь в избранное, нравится.
    """
    if DEMO_MODE:
        t = _demo_current_track()
        _demo_state["liked"].add(t["uri"])
        return f"❤️ [DEMO] Liked: {t['name']} by {t['artist']}"
    try:
        sp = _get_spotify()
        current = sp.current_playback()
        if not current or not current.get("item"):
            return "❌ Nothing is playing to like."
        track_id = current["item"]["id"]
        track_name = current["item"]["name"]
        sp.current_user_saved_tracks_add([track_id])
        return f"❤️ Added to Liked Songs: {track_name}"
    except Exception as e:
        return f"❌ Could not like track: {e}"


def shuffle_toggle() -> str:
    """Toggle shuffle mode on Spotify.

    Use this when the user says: shuffle, random, перемешай, случайный порядок.
    """
    if DEMO_MODE:
        return "🔀 [DEMO] Shuffle mode toggled! Enjoy the randomness 🎲"
    try:
        sp = _get_spotify()
        current = sp.current_playback()
        current_shuffle = current.get("shuffle_state", False) if current else False
        sp.shuffle(not current_shuffle)
        state = "ON 🔀" if not current_shuffle else "OFF"
        return f"Shuffle: {state}"
    except Exception as e:
        return f"❌ Could not toggle shuffle: {e}"
