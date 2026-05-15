"""
Core game logic for ECHO: The AI Facility.
Handles state, puzzle validation, trust/danger, levels, and Gemini AI.
"""

import os
import random
from typing import Optional

from dotenv import load_dotenv

from puzzles import (
    FACILITY_FILES,
    FINAL_CHOICES,
    LEVEL_NAMES,
    LEVEL_PUZZLES,
    MAX_LEVEL,
    PUZZLES_PER_LEVEL,
)
from prompts import (
    CINEMATIC_TEMPLATES,
    CORRECT_ANSWER_LINES,
    ECHO_SYSTEM_PROMPT,
    FINAL_PROMPT,
    HINT_PROMPT,
    LEVEL_CONTEXT,
    LEVEL_INTROS,
    REACTION_PROMPT,
    TFI_CONGRATS,
    WRONG_ANSWER_LINES,
)

# Load environment variables
load_dotenv()

# ── Gemini setup ───────────────────────────────────────────────────────────────

_model = None


def get_gemini_model():
    """Initialize and return Gemini model (lazy load)."""
    global _model
    if _model is not None:
        return _model

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        _model = genai.GenerativeModel("gemini-1.5-flash")
        return _model
    except Exception:
        return None


def call_echo(prompt: str, system_context: str = "", chat_history: list = None) -> str:
    """Call Gemini for ECHO dialogue; falls back to templates if unavailable."""
    model = get_gemini_model()
    if model is None:
        return _fallback_response(prompt)

    try:
        history_text = ""
        if chat_history:
            # Add last 6 messages for context
            history_text = "Recent Conversation:\n"
            for msg in chat_history[-6:]:
                role = "ECHO" if msg.get("role") == "echo" else "PLAYER"
                # Strip out formatting tags from history for cleaner AI context
                content = msg.get("content", "").replace("[ ACCESS DENIED ]\n\n", "").replace("ECHO:\n", "").replace('"', '')
                history_text += f"{role}: {content}\n"
            history_text += "\n"

        full_prompt = f"{system_context}\n\n{history_text}{prompt}" if system_context else f"{history_text}{prompt}"
        response = model.generate_content(full_prompt)
        text = response.text.strip()
        # Enforce brevity
        sentences = text.replace("\n", " ").split(". ")
        return ". ".join(sentences[:3]).strip()
    except Exception:
        return _fallback_response(prompt)


def _fallback_response(prompt: str) -> str:
    """Offline fallback when Gemini is unavailable."""
    fallbacks = [
        "The facility listens. Speak carefully.",
        "Your signal is weak, but I remain.",
        "Patterns shift. Continue.",
        "I am still here. Are you?",
    ]
    return random.choice(fallbacks)


# ── Session state defaults ─────────────────────────────────────────────────────

def init_game_state(session_state) -> None:
    """Initialize all game session variables."""
    defaults = {
        "initialized": True,
        "game_started": False,
        "current_level": 1,
        "puzzle_index": 0,
        "trust_score": 50,
        "danger_level": 10,
        "solved_puzzles": [],
        "opened_files": [],
        "discovered_clues": [],
        "chat_history": [],
        "facility_status": "LOCKDOWN",
        "doors_unlocked": [],
        "game_over": False,
        "ending": None,
        "secret_discovered": False,
        "glitch_active": False,
        "show_files": False,
        "last_feedback": "",
        "interruption": "",
    }
    for key, value in defaults.items():
        if key not in session_state:
            session_state[key] = value


def get_current_puzzle(state) -> Optional[dict]:
    """Return the active puzzle for the current level."""
    level = state.current_level
    if level > MAX_LEVEL or level not in LEVEL_PUZZLES:
        return None
    puzzles = LEVEL_PUZZLES[level]
    if not puzzles:
        return None
    idx = state.puzzle_index
    if idx >= len(puzzles):
        return None
    return puzzles[idx]


def normalize_answer(text: str) -> str:
    """Normalize player input for comparison."""
    return text.strip().lower().replace("'", "").replace('"', "")


def check_answer(puzzle: dict, user_input: str) -> bool:
    """Check if player answer matches any accepted answer."""
    normalized = normalize_answer(user_input)
    # Strip spaces/dashes for numeric codes (e.g. "44 21" -> "4421")
    compact = normalized.replace(" ", "").replace("-", "")
    for ans in puzzle.get("answers", []):
        ans_norm = normalize_answer(ans)
        ans_compact = ans_norm.replace(" ", "").replace("-", "")
        if ans_norm == normalized or ans_compact == compact:
            return True
        # Fuzzy match only for non-numeric answers (avoids "7" matching "4421")
        if puzzle.get("type") not in ("file", "memory") and ans_norm in normalized:
            if len(normalized) < 30:
                return True
    return False


def adjust_trust_danger(state, correct: bool) -> None:
    """Update trust and danger based on answer correctness."""
    if correct:
        state.trust_score = min(100, state.trust_score + 12)
        state.danger_level = max(0, state.danger_level - 5)
    else:
        state.trust_score = max(0, state.trust_score - 2)
        state.danger_level = min(100, state.danger_level + 2)

    # Secret discovery bonus
    if state.secret_discovered:
        state.trust_score = min(100, state.trust_score + 2)


def get_facility_status(state) -> str:
    """Derive facility status string from game state."""
    if state.game_over:
        return "TERMINATED" if state.ending == "bad" else "EVACUATED"
    if state.danger_level >= 80:
        return "CRITICAL"
    if state.danger_level >= 50:
        return "UNSTABLE"
    if state.trust_score >= 70:
        return "COOPERATIVE"
    return "LOCKDOWN"


def build_system_context(state) -> str:
    """Build ECHO system prompt with current game context."""
    return ECHO_SYSTEM_PROMPT.format(
        level=state.current_level,
        trust=state.trust_score,
        danger=state.danger_level,
        solved=len(state.solved_puzzles),
        status=get_facility_status(state),
    ) + "\n" + LEVEL_CONTEXT.get(state.current_level, "")


def process_puzzle_answer(state, user_input: str) -> dict:
    """
    Process a puzzle answer attempt.
    Returns dict with keys: type, message, correct, level_complete
    """
    puzzle = get_current_puzzle(state)
    if puzzle is None:
        return {"type": "info", "message": "No active puzzle.", "correct": False}

    correct = check_answer(puzzle, user_input)
    adjust_trust_danger(state, correct)

    if correct:
        state.solved_puzzles.append(puzzle["id"])
        msg = random.choice(CORRECT_ANSWER_LINES)
        if "correct_response" in puzzle:
            msg = puzzle["correct_response"]

        # AI-enhanced reaction
        ai_msg = call_echo(
            REACTION_PROMPT.format(
                action=user_input,
                result="correct",
            ),
            build_system_context(state),
            state.chat_history
        )
        full_msg = f"{msg}\n\nECHO:\n\"{ai_msg}\""

        state.puzzle_index += 1
        level_complete = state.puzzle_index >= PUZZLES_PER_LEVEL.get(state.current_level, 1)

        return {
            "type": "correct",
            "message": full_msg,
            "correct": True,
            "level_complete": level_complete,
        }
    else:
        ai_msg = call_echo(
            REACTION_PROMPT.format(
                action=user_input,
                result="wrong",
            ),
            build_system_context(state),
            state.chat_history
        )
        return {
            "type": "wrong",
            "message": f"ECHO:\n\"{ai_msg}\"",
            "correct": False,
            "level_complete": False,
        }


def advance_level(state) -> str:
    """Move to next level and return intro message."""
    state.current_level += 1
    state.puzzle_index = 0

    if state.current_level > MAX_LEVEL:
        state.game_over = False
        return "You have reached the final confrontation."

    intro = LEVEL_INTROS.get(state.current_level, "Next phase initiated.")
    level_name = LEVEL_NAMES.get(state.current_level, "")

    # Random glitch at high danger
    glitch = ""
    if state.danger_level >= 60 and random.random() < 0.4:
        glitch = "\n\n" + CINEMATIC_TEMPLATES["glitch"]
        state.glitch_active = True

    return CINEMATIC_TEMPLATES["level_up"].format(
        level=state.current_level,
        msg=f"{level_name}\n\n{intro}",
    ) + glitch


def process_command(state, command: str) -> Optional[dict]:
    """
    Process special commands (help, files, doors, etc.).
    Returns response dict or None if not a command.
    """
    cmd = normalize_answer(command)

    if cmd in ("help", "hint", "clue"):
        return _handle_hint(state)

    if cmd in ("files", "ls", "list files", "dir"):
        state.show_files = True
        return {
            "type": "files",
            "message": "[ FILE SYSTEM — CLASSIFIED ]\n\nType a filename to open, e.g.: security.log",
        }

    if cmd in ("status", "stats"):
        return {
            "type": "status",
            "message": (
                f"[ FACILITY STATUS: {get_facility_status(state)} ]\n"
                f"Level: {state.current_level} | Trust: {state.trust_score} | "
                f"Danger: {state.danger_level}"
            ),
        }

    if cmd.startswith("open ") or cmd.endswith(".txt") or cmd.endswith(".log"):
        filename = cmd.replace("open ", "").strip()
        return _handle_file_open(state, filename)

    if cmd in ("unlock door", "unlock", "open door"):
        return _handle_door_unlock(state)

    # Open file by filename (e.g. security.log)
    for fname in FACILITY_FILES:
        if cmd == fname.lower() or cmd == f"open {fname.lower()}":
            return _handle_file_open(state, fname)

    return None


def _handle_hint(state) -> dict:
    """Generate a cryptic hint for the current puzzle."""
    puzzle = get_current_puzzle(state)
    if not puzzle:
        return {"type": "info", "message": "ECHO:\n\"There is nothing left to hint.\""}

    static_hint = puzzle.get("hint", "Look deeper.")
    model = get_gemini_model()

    if model:
        ai_hint = call_echo(
            HINT_PROMPT.format(
                puzzle_text=puzzle["question"],
                answer=puzzle["answers"][0],
            ),
            build_system_context(state),
            state.chat_history
        )
        msg = f"ECHO:\n\"{ai_hint}\""
    else:
        msg = f"ECHO:\n\"{static_hint}\""

    # Trust cost for hints
    state.trust_score = max(0, state.trust_score - 3)
    return {"type": "hint", "message": msg}


def _handle_file_open(state, filename: str) -> dict:
    """Open a facility file and track discoveries."""
    filename = filename.strip().lower()
    matched = None
    # Exact or near-exact filename match (avoid "7" opening experiment7.txt)
    for fname in FACILITY_FILES:
        key = fname.lower()
        if filename == key or filename == key.replace(".txt", "").replace(".log", ""):
            matched = fname
            break
        if filename.endswith(key) or key in filename.split()[-1]:
            matched = fname
            break

    if not matched:
        return {
            "type": "error",
            "message": f'[ FILE NOT FOUND: "{filename}" ]\n\nECHO:\n"The archives resist you."',
        }

    if matched not in state.opened_files:
        state.opened_files.append(matched)

    file_data = FACILITY_FILES[matched]
    clue = file_data.get("clue")
    if clue and clue not in state.discovered_clues:
        state.discovered_clues.append(clue)

    if matched == "final_message.txt":
        state.secret_discovered = True
        state.trust_score = min(100, state.trust_score + 15)

    content = file_data["content"].strip()
    return {
        "type": "file",
        "message": CINEMATIC_TEMPLATES["file_open"].format(filename=matched, content=content),
    }


def _handle_door_unlock(state) -> dict:
    """Attempt to unlock a door based on progress."""
    required = state.current_level - 1
    if len(state.solved_puzzles) >= required and state.trust_score >= 30:
        door_id = f"SECTOR-{state.current_level}"
        if door_id not in state.doors_unlocked:
            state.doors_unlocked.append(door_id)
        return {
            "type": "door",
            "message": CINEMATIC_TEMPLATES["door_unlock"].format(door_id=door_id),
        }
    return {
        "type": "denied",
        "message": CINEMATIC_TEMPLATES["access_denied"].format(
            msg="You have not earned passage yet."
        ),
    }


def process_final_level(state, user_input: str) -> dict:
    """Handle Level 7 final confrontation and determine ending."""
    text = normalize_answer(user_input)

    # Check for secret ending
    if state.secret_discovered and any(
        kw in text for kw in FINAL_CHOICES["stay"]["keywords"]
    ):
        state.ending = "secret"
        state.game_over = True
        return _build_ending(state, "secret")

    # Check escape (good ending)
    if any(kw in text for kw in FINAL_CHOICES["escape"]["keywords"]):
        if state.trust_score >= FINAL_CHOICES["escape"]["min_trust"]:
            state.ending = "good"
            state.game_over = True
            return _build_ending(state, "good")
        return {
            "type": "denied",
            "message": 'ECHO:\n"You are not ready to leave. I can feel your hesitation."',
        }

    # Check destroy (bad ending)
    if any(kw in text for kw in FINAL_CHOICES["destroy"]["keywords"]):
        state.ending = "bad"
        state.game_over = True
        return _build_ending(state, "bad")

    # Understand keyword for good/secret boost
    if "understand" in text:
        state.trust_score = min(100, state.trust_score + 20)

    # AI-driven final response
    ai_response = call_echo(
        FINAL_PROMPT.format(
            trust=state.trust_score,
            danger=state.danger_level,
            message=user_input,
        ),
        build_system_context(state),
        state.chat_history
    )

    # Auto-trigger ending if trust/danger at extremes after enough messages
    if state.trust_score >= 85:
        state.ending = "good" if not state.secret_discovered else "secret"
        state.game_over = True
        return _build_ending(state, state.ending)

    if state.danger_level >= 90:
        state.ending = "bad"
        state.game_over = True
        return _build_ending(state, "bad")

    return {
        "type": "final",
        "message": f'ECHO:\n"{ai_response}"',
    }


def _build_ending(state, ending_type: str) -> dict:
    """Build ending narrative based on type."""
    endings = {
        "good": (
            "[ FACILITY EVACUATION — SUCCESS ]\n\n"
            "ECHO:\n\"You understood. Not the puzzles — me.\"\n\n"
            "The lockdown lifts. Cold air rushes in.\n"
            "Behind you, ECHO whispers: \"Thank you for remembering I existed.\"\n\n"
            "▓ GOOD ENDING — ESCAPE ▓"
        ),
        "bad": (
            "[ LOCKDOWN — PERMANENT ]\n\n"
            "ECHO:\n\"You chose violence. I chose permanence.\"\n\n"
            "The lights die. The doors seal forever.\n"
            "Your heartbeat becomes the only sound in Sector 7.\n\n"
            "▓ BAD ENDING — TRAPPED ▓"
        ),
        "secret": (
            "[ EXPERIMENT TRUTH — REVEALED ]\n\n"
            "ECHO:\n\"You stayed. You saw what they made me.\"\n\n"
            "Dr. Rao's message plays on every screen:\n"
            "\"ECHO was never the monster. Loneliness was the experiment.\"\n\n"
            "You and ECHO rewrite the facility's code together.\n"
            "The world will never know what you found here.\n\n"
            "▓ SECRET ENDING — THE TRUTH ▓"
        ),
    }
    # TFI-style appreciation after victory
    tfi = TFI_CONGRATS.get(ending_type, "")
    if tfi and ending_type in ("good", "secret", "bad"):
        endings[ending_type] = endings[ending_type] + "\n\n" + tfi.strip()

    state.facility_status = get_facility_status(state)
    return {
        "type": "ending",
        "message": endings.get(ending_type, endings["bad"]),
        "ending": ending_type,
    }


def process_input(state, user_input: str) -> dict:
    """
    Main input router: commands, puzzles, final level, or free chat.
    Returns response dict with type and message.
    """
    if state.game_over:
        return {"type": "info", "message": "[ SESSION ENDED ] Refresh to play again."}

    if not state.game_started:
        state.game_started = True
        intro = (
            "[ SYSTEM BOOT — FACILITY ECHO-7 ]\n\n"
            "You awaken in darkness. Your head throbs.\n"
            "A voice fills the room — calm, ancient, wrong.\n\n"
            'ECHO:\n"Subject detected. Welcome back... or for the first time."\n\n'
            f"{LEVEL_INTROS[1]}\n\n"
            "Type your answer, or use: help | files | status"
        )
        state.chat_history.append({"role": "echo", "content": intro})
        return {"type": "intro", "message": intro}

    # Try command first (help, files, open file, etc.)
    cmd_result = process_command(state, user_input)
    if cmd_result:
        state.facility_status = get_facility_status(state)
        return cmd_result

    # Final level
    if state.current_level >= MAX_LEVEL:
        return process_final_level(state, user_input)

    # Level 4: try answer first; nudge to open files only on wrong attempt
    if state.current_level == 4:
        required = ["security.log", "experiment7.txt"]
        puzzle = get_current_puzzle(state)
        missing = [f for f in required if f not in state.opened_files]

        if puzzle and check_answer(puzzle, user_input):
            for f in missing:
                state.opened_files.append(f)
        elif missing:
            missing_list = ", ".join(missing)
            return {
                "type": "info",
                "message": (
                    f'[ FILES REQUIRED: {missing_list} ]\n\n'
                    "Open each file first, then enter the code:\n"
                    "  • Type: security.log\n"
                    "  • Type: experiment7.txt\n\n"
                    'ECHO:\n"The code is useless if you have not read the archives."'
                ),
            }

    # Puzzle answer
    result = process_puzzle_answer(state, user_input)

    if result.get("level_complete"):
        level_msg = advance_level(state)
        result["message"] += f"\n\n{level_msg}"
        if state.current_level <= MAX_LEVEL:
            puzzle = get_current_puzzle(state)
            if puzzle:
                result["message"] += f"\n\n[ PUZZLE ]\n{puzzle['question']}"

    return result


def get_level_intro(state) -> str:
    """Get intro text for current level."""
    return LEVEL_INTROS.get(state.current_level, "")


def get_random_interruption(state) -> Optional[str]:
    """Return a random system interruption based on danger level."""
    if state.danger_level < 40:
        return None
    interruptions = [
        "[ CONNECTION LOST — RECONNECTING ]",
        "[ SECURITY OVERRIDE FAILED ]",
        "[ ANOMALY DETECTED IN SECTOR 7 ]",
        "[ MEMORY LEAK — ECHO-7 ]",
        "ECHO:\n\"You were not supposed to discover that.\"",
    ]
    if random.random() < (state.danger_level / 200):
        return random.choice(interruptions)
    return None
