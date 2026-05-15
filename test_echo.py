from game_logic import call_echo, build_system_context, init_game_state
from prompts import REACTION_PROMPT

class State:
    pass

state = State()
state.__dict__.clear()
init_game_state(state.__dict__)

# Need to copy over the initialized dict to the class properties
for k, v in state.__dict__.items():
    setattr(state, k, v)

# Update state variables
state.current_level = 1
state.trust_score = 50
state.danger_level = 10
state.solved_puzzles = []
state.facility_status = 'LOCKDOWN'

try:
    print(call_echo(
        REACTION_PROMPT.format(action='any hints', result='wrong'),
        build_system_context(state),
        state.chat_history
    ))
except Exception as e:
    print(f"Exception: {e}")
