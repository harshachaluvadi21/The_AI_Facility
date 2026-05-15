"""
ECHO: The AI Facility
A cinematic AI-powered puzzle horror game.
Run: streamlit run app.py
"""

import random

import streamlit as st

from game_logic import (
    get_current_puzzle,
    get_random_interruption,
    init_game_state,
    process_input,
)
from ui import (
    load_css,
    render_chat_history,
    render_current_puzzle,
    render_file_browser,
    render_interruption,
    render_response,
    render_sidebar,
    render_start_screen,
    render_title,
)

# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="ECHO: The AI Facility",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()
init_game_state(st.session_state)
state = st.session_state

# ── Layout ─────────────────────────────────────────────────────────────────────

render_title()
render_sidebar(state)

# Start screen
if not state.game_started:
    if render_start_screen():
        intro_result = process_input(state, "begin")
        state.chat_history.append({"role": "echo", "content": intro_result["message"]})
        st.rerun()
    st.stop()

# Main game area
col_main, col_pad = st.columns([4, 1])

with col_main:
    # Random system interruption
    interruption = get_random_interruption(state)
    if interruption and random.random() < 0.15:
        render_interruption(interruption)
        state.interruption = interruption

    # Story / dialogue above the active puzzle
    render_chat_history(state)

    if not state.game_over:
        render_current_puzzle(state)
        render_file_browser(state)

    # Input directly below the question panel
    if not state.game_over:
        user_input = st.chat_input("Transmit to ECHO...", key="echo_chat_input")
    else:
        user_input = None

    if user_input:
        state.chat_history.append({"role": "user", "content": user_input})
        result = process_input(state, user_input)
        render_response(result, state)
        if not state.game_over:
            st.rerun()

# Footer status line
if state.game_started and not state.game_over:
    st.markdown(
        '<div style="text-align:center;color:#4a6b4a;font-size:0.7rem;'
        'letter-spacing:0.3em;margin-top:1rem">'
        "FACILITY ECHO-7 — ALL COMMUNICATIONS MONITORED"
        "</div>",
        unsafe_allow_html=True,
    )
