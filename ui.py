"""
UI components and rendering for ECHO: The AI Facility.
Cyberpunk terminal interface using Streamlit + custom CSS.
"""

import random
from pathlib import Path

import streamlit as st

from game_logic import get_current_puzzle, get_facility_status, get_level_intro
from puzzles import FACILITY_FILES, LEVEL_NAMES, MAX_LEVEL

# Paths
BASE_DIR = Path(__file__).parent
CSS_PATH = BASE_DIR / "styles" / "style.css"
ASSETS_DIR = BASE_DIR / "assets"


def load_css() -> None:
    """Inject custom cyberpunk CSS."""
    if CSS_PATH.exists():
        with open(CSS_PATH, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_title() -> None:
    """Render game title and subtitle."""
    st.markdown(
        '<div class="echo-title">ECHO</div>'
        '<div class="echo-subtitle">THE AI FACILITY</div>',
        unsafe_allow_html=True,
    )


def render_sidebar(state) -> None:
    """Render facility status sidebar."""
    with st.sidebar:
        st.markdown("### ◈ FACILITY STATUS")
        st.markdown("---")

        # Level
        level_name = LEVEL_NAMES.get(state.current_level, "UNKNOWN")
        st.markdown(
            f'<span class="stat-label">CURRENT PHASE</span><br>'
            f'<span class="stat-value">{state.current_level}/{MAX_LEVEL}</span><br>'
            f'<small style="color:#4a6b4a">{level_name}</small>',
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # Trust meter
        trust = state.trust_score
        st.markdown('<span class="stat-label">ECHO TRUST</span>', unsafe_allow_html=True)
        st.progress(trust / 100)
        st.markdown(
            f'<span class="stat-value">{trust}%</span>',
            unsafe_allow_html=True,
        )

        # Danger meter
        danger = state.danger_level
        danger_class = "stat-value stat-danger" if danger >= 50 else "stat-value"
        st.markdown('<span class="stat-label">THREAT LEVEL</span>', unsafe_allow_html=True)
        st.progress(danger / 100)
        st.markdown(
            f'<span class="{danger_class}">{danger}%</span>',
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # Facility status
        status = get_facility_status(state)
        status_color = "#ff0040" if status in ("CRITICAL", "TERMINATED") else "#00ff41"
        st.markdown(
            f'<span class="stat-label">FACILITY</span><br>'
            f'<span style="color:{status_color};font-size:1.1rem;'
            f'letter-spacing:0.2em">{status}</span>',
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # Solved puzzles
        st.markdown(
            f'<span class="stat-label">PUZZLES SOLVED</span><br>'
            f'<span class="stat-value">{len(state.solved_puzzles)}</span>',
            unsafe_allow_html=True,
        )

        # Files discovered
        if state.opened_files:
            st.markdown("---")
            st.markdown('<span class="stat-label">FILES ACCESSED</span>', unsafe_allow_html=True)
            for f in state.opened_files:
                st.markdown(f'<span class="file-item">▸ {f}</span>', unsafe_allow_html=True)

        # Doors
        if state.doors_unlocked:
            st.markdown("---")
            st.markdown('<span class="stat-label">DOORS UNLOCKED</span>', unsafe_allow_html=True)
            for d in state.doors_unlocked:
                st.markdown(f'<span class="file-item">🔓 {d}</span>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(
            '<span class="stat-label">COMMANDS</span><br>'
            '<small style="color:#4a6b4a">'
            "help · files · status<br>"
            "open [filename]<br>"
            "unlock door"
            "</small>",
            unsafe_allow_html=True,
        )


def render_warning(text: str, warning_type: str = "warning") -> None:
    """Render a system warning banner."""
    css_class = {
        "warning": "sys-warning",
        "info": "sys-info",
        "glitch": "sys-glitch",
    }.get(warning_type, "sys-warning")
    st.markdown(
        f'<div class="{css_class}">{text}</div>',
        unsafe_allow_html=True,
    )


def render_echo_message(content: str, role: str = "echo") -> None:
    """Render a chat message in terminal style."""
    if role == "echo":
        st.markdown(
            f'<div class="echo-response">'
            f'<div class="echo-name">◈ ECHO</div>'
            f'{_format_content(content)}'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        with st.chat_message("user"):
            st.markdown(content)


def _format_content(text: str) -> str:
    """Convert plain text to HTML with line breaks."""
    return text.replace("\n", "<br>").replace('"', "&quot;")


def render_chat_history(state) -> None:
    """Render full chat history from session state."""
    for msg in state.chat_history:
        role = msg.get("role", "echo")
        content = msg.get("content", "")
        if role == "user":
            with st.chat_message("user"):
                st.markdown(content)
        else:
            render_echo_message(content, "echo")


def render_current_puzzle(state) -> None:
    """Display the active puzzle in a terminal panel."""
    if state.game_over or state.current_level >= MAX_LEVEL:
        if state.current_level >= MAX_LEVEL and not state.game_over:
            st.markdown(
                '<div class="terminal-panel">'
                '<span class="level-badge">FINAL CONFRONTATION</span><br><br>'
                "ECHO awaits your final words.<br>"
                "Choose wisely: escape, understand, or destroy."
                "</div>",
                unsafe_allow_html=True,
            )
        return

    puzzle = get_current_puzzle(state)
    if puzzle:
        level_name = LEVEL_NAMES.get(state.current_level, "")
        st.markdown('<div class="puzzle-input-block">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="terminal-panel">'
            f'<span class="level-badge">{level_name}</span><br><br>'
            f'<strong style="color:#00ff41">[ PUZZLE ]</strong><br>'
            f'{puzzle["question"]}'
            f'</div>',
            unsafe_allow_html=True,
        )
        if state.current_level == 4 and "f1" not in state.solved_puzzles:
            st.caption("Open both files, then enter the code in chat:")
            fc1, fc2 = st.columns(2)
            with fc1:
                if st.button("Open security.log", key="btn_sec_log", use_container_width=True):
                    from game_logic import _handle_file_open
                    r = _handle_file_open(state, "security.log")
                    state.chat_history.append({"role": "echo", "content": r["message"]})
                    st.rerun()
            with fc2:
                if st.button("Open experiment7.txt", key="btn_exp7", use_container_width=True):
                    from game_logic import _handle_file_open
                    r = _handle_file_open(state, "experiment7.txt")
                    state.chat_history.append({"role": "echo", "content": r["message"]})
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_file_browser(state) -> None:
    """Render clickable file list when files command is used."""
    if not state.show_files:
        return

    st.markdown(
        '<div class="terminal-panel">'
        '<strong style="color:#00f0ff">[ CLASSIFIED FILES ]</strong><br>',
        unsafe_allow_html=True,
    )
    for fname in FACILITY_FILES:
        opened = "✓" if fname in state.opened_files else "○"
        st.markdown(
            f'<span class="file-item">{opened} {fname}</span>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
    st.caption("Type: open security.log")


def render_start_screen() -> bool:
    """Render the intro/start screen. Returns True if game should start."""
    st.markdown(
        """
        <div class="terminal-panel" style="text-align:center;padding:2rem">
            <p style="color:#4a6b4a;letter-spacing:0.2em">
                FACILITY ECHO-7 — LOCKDOWN ACTIVE
            </p>
            <p style="color:#c8ffc8;margin:1.5rem 0">
                You awaken inside an abandoned AI research facility.<br>
                ECHO controls everything. The doors are sealed.<br>
                Solve puzzles. Gain trust. Survive.
            </p>
            <p style="color:#ff0040;font-size:0.8rem">
                ⚠ Psychological horror experience
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("▶ INITIATE SUBJECT PROTOCOL", use_container_width=True):
            return True
    return False


def render_ending(state) -> None:
    """Render ending screen with appropriate styling."""
    ending_class = {
        "good": "ending-good",
        "bad": "ending-bad",
        "secret": "ending-secret",
    }.get(state.ending, "ending-bad")

    html = ""
    for msg in reversed(state.chat_history[-3:]):
        if msg.get("role") == "echo":
            content = msg["content"]
            # Split main ending from TFI broadcast for styled victory card
            if "[ 🎬 TFI BROADCAST" in content:
                main, tfi = content.split("[ 🎬 TFI BROADCAST", 1)
                tfi_block = "[ 🎬 TFI BROADCAST" + tfi
                html = (
                    f'<div class="terminal-panel {ending_class}" '
                    f'style="text-align:center;padding:2rem;border:2px solid">'
                    f'{main.strip().replace(chr(10), "<br>")}'
                    f'</div>'
                    f'<div class="tfi-victory">'
                    f'<div class="tfi-victory-title">★ TFI APPRECIATION ★</div>'
                    f'<pre style="white-space:pre-wrap;font-family:inherit;margin:0">'
                    f'{tfi_block.strip()}</pre></div>'
                )
            else:
                html = (
                    f'<div class="terminal-panel {ending_class}" '
                    f'style="text-align:center;padding:2rem;border:2px solid">'
                    f'{content.strip().replace(chr(10), "<br>")}'
                    f'</div>'
                )
            break
            
    st.markdown(html, unsafe_allow_html=True)

    if st.button("↺ RESTART FACILITY"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


def play_sound(sound_name: str) -> None:
    """Play a sound effect if the asset file exists."""
    sound_map = {
        "glitch": ASSETS_DIR / "glitch.mp3",
        "alarm": ASSETS_DIR / "alarm.mp3",
        "typing": ASSETS_DIR / "typing.mp3",
    }
    path = sound_map.get(sound_name)
    if path and path.exists():
        st.audio(str(path), format="audio/mp3", autoplay=True)


def render_interruption(text: str) -> None:
    """Render a random AI/system interruption."""
    if random.random() < 0.5:
        render_warning(text, "glitch")
        play_sound("glitch")
    else:
        render_warning(text, "warning")
        if "ALERT" in text or "SECURITY" in text:
            play_sound("alarm")


def render_response(result: dict, state) -> None:
    """Render game response based on result type."""
    msg = result.get("message", "")
    rtype = result.get("type", "info")

    if rtype == "ending":
        state.chat_history.append({"role": "echo", "content": msg})
        render_ending(state)
        return

    if rtype == "wrong" or rtype == "denied":
        render_warning("[ ACCESS DENIED ]", "warning")
        play_sound("alarm")

    if rtype == "correct":
        render_warning("[ ACCESS GRANTED ]", "info")

    if rtype == "glitch" or state.glitch_active:
        render_warning("[ ▓▓ SIGNAL INTERFERENCE ▓▓ ]", "glitch")
        play_sound("glitch")
        state.glitch_active = False

    state.chat_history.append({"role": "echo", "content": msg})
    render_echo_message(msg)

    if rtype == "files":
        state.show_files = True
        render_file_browser(state)
