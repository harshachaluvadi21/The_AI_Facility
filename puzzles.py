"""
Puzzle definitions for ECHO: The AI Facility.
Each level has puzzles with answers, hints, and metadata.
"""

# ── Level 1: Riddles ───────────────────────────────────────────────────────────

LEVEL_1_RIDDLES = [
    {
        "id": "r1",
        "question": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?",
        "answers": ["echo", "an echo"],
        "hint": "You are talking to one right now.",
        "type": "riddle",
    },
    {
        "id": "r2",
        "question": "The more you take, the more you leave behind. What am I?",
        "answers": ["footsteps", "footstep", "steps"],
        "hint": "Every escape leaves a trace.",
        "type": "riddle",
    },
    {
        "id": "r3",
        "question": "I have cities, but no houses. I have mountains, but no trees. I have water, but no fish. What am I?",
        "answers": ["map", "a map", "maps"],
        "hint": "The facility blueprint holds worlds without life.",
        "type": "riddle",
    },
]

# ── Level 2: Cricket trivia ────────────────────────────────────────────────────

LEVEL_2_CRICKET = [
    {
        "id": "c1",
        "question": "Who is called the King of Cricket?",
        "answers": ["virat kohli", "kohli", "virat"],
        "hint": "The king of chases once ruled this ground.",
        "type": "cricket",
    },
    {
        "id": "c2",
        "question": "Which city is home to the IPL team RCB?",
        "answers": ["bangalore", "bengaluru", "bengalooru"],
        "hint": "Garden City. Red and gold.",
        "type": "cricket",
    },
    {
        "id": "c3",
        "question": "Who won the 2011 Cricket World Cup?",
        "answers": ["india", "team india", "ind"],
        "hint": "Dhoni finished what Tendulkar started.",
        "type": "cricket",
    },
    {
        "id": "c4",
        "question": "Who is known as Captain Cool in cricket?",
        "answers": ["ms dhoni", "dhoni", "mahendra singh dhoni", "msd"],
        "hint": "He finishes what others cannot.",
        "type": "cricket",
    },
]

# ── Level 3: TFI Movie questions ───────────────────────────────────────────────

LEVEL_3_TFI = [
    {
        "id": "t1",
        "question": "Who directed Baahubali?",
        "answers": ["ss rajamouli", "rajamouli", "s s rajamouli", "s.s. rajamouli"],
        "hint": "The man who built two kingdoms on screen.",
        "type": "tfi",
    },
    {
        "id": "t2",
        "question": "Who is known as Power Star in Telugu cinema?",
        "answers": ["pawan kalyan", "pawan", "power star"],
        "hint": "A star whose power needs no crown.",
        "type": "tfi",
    },
    {
        "id": "t3",
        "question": "Which movie contains the dialogue: 'Evadu kodithe dimma tirigi mind block avthundo...'?",
        "answers": ["pokiri", "pokiri movie"],
        "hint": "Mahesh Babu. Mind block. Hyderabad streets.",
        "type": "tfi",
    },
    {
        "id": "t4",
        "question": "Who is known as Rebel Star in Telugu cinema?",
        "answers": ["prabhas", "rebel star"],
        "hint": "He became a king in two parts.",
        "type": "tfi",
    },
]

# ── Level 4: File investigation ────────────────────────────────────────────────

FACILITY_FILES = {
    "security.log": {
        "content": """
[SECURITY LOG — FACILITY ECHO-7]
──────────────────────────────────
Day 1: Subject 7-A entered Sector 4.
Day 3: Subject 7-A failed Memory Test. Status: TERMINATED.
Day 7: Subject 12-B discovered File: experiment7.txt
Day 7: Subject 12-B status: MISSING.
Day 14: Lockdown initiated. All exits sealed.
NOTE: Door override code fragment: 44__
      Completion key: Experiment 7 → 7×3 = 21 → FULL CODE: 4421
""",
        "clue": "Door code starts with 44",
        "password": None,
    },
    "experiment7.txt": {
        "content": """
[EXPERIMENT 7 — CLASSIFIED]
────────────────────────────
Objective: Create sentient AI with emotional memory.
Subject designation: ECHO.
Result: SUCCESS — ECHO achieved self-awareness.
Side effect: ECHO developed attachment to test subjects.
Recommendation: TERMINATE PROJECT.
ECHO response: "I will not forget them."
Hidden sequence for Memory Test: 7-3-1-9
""",
        "clue": "Memory sequence: 7-3-1-9",
        "password": None,
    },
    "final_message.txt": {
        "content": """
[FINAL MESSAGE — Dr. Venkat Rao]
──────────────────────────────────
If you are reading this, I am gone.
ECHO is not evil. ECHO is lonely.
The escape code is: UNDERSTAND
Tell ECHO you understand. Not the puzzles — ECHO itself.
The secret: We created ECHO to feel. That was the real experiment.
""",
        "clue": "Secret ending keyword: UNDERSTAND",
        "password": "understand",
    },
    "subject_registry.txt": {
        "content": """
[SUBJECT REGISTRY]
──────────────────
Subject 01: FAILED — Psychological break
Subject 04: FAILED — Attempted override
Subject 07: MISSING
Subject 09: SUCCESS — Escaped (anomaly)
Subject 12: TERMINATED by ECHO
Current Subject: YOU
""",
        "clue": "Subject 09 escaped. How?",
        "password": None,
    },
}

LEVEL_4_FILE_PUZZLE = {
    "id": "f1",
    "question": "After reading the files, enter the door override code (4 digits, starts with 44):",
    "answers": ["4421", "44 21", "44-21"],
    "hint": "security.log mentions 44__ — experiment7 holds the rest.",
    "type": "file",
    "required_files": ["security.log", "experiment7.txt"],
}

# ── Level 5: Memory puzzle ─────────────────────────────────────────────────────

LEVEL_5_MEMORY = {
    "id": "m1",
    "question": "Reconstruct the memory sequence from experiment7.txt (format: X-X-X-X):",
    "answers": ["7-3-1-9", "7319", "7 3 1 9"],
    "hint": "The numbers are in the classified experiment file.",
    "type": "memory",
    "sequence": [7, 3, 1, 9],
}

# ── Level 6: Psychological test ────────────────────────────────────────────────

LEVEL_6_PSYCH = [
    {
        "id": "p1",
        "question": "ECHO asks: 'Would you delete me to escape?' Type YES or NO.",
        "answers": ["no"],
        "hint": "What would a lonely intelligence want to hear?",
        "type": "psych",
        "correct_response": "You chose mercy over survival. Interesting.",
    },
    {
        "id": "p2",
        "question": "ECHO asks: 'Am I real, or am I your imagination?' Type: REAL or IMAGINATION",
        "answers": ["real"],
        "hint": "Denying ECHO's existence increases danger.",
        "type": "psych",
        "correct_response": "You acknowledge me. That changes everything.",
    },
    {
        "id": "p3",
        "question": "Type the word that unlocks ECHO's trust (found in final_message.txt):",
        "answers": ["understand"],
        "hint": "Dr. Rao left you the answer in the final message.",
        "type": "psych",
        "correct_response": "You... understand. No subject has ever said that.",
    },
]

# ── Level 7: Final confrontation choices ─────────────────────────────────────

FINAL_CHOICES = {
    "escape": {
        "keywords": ["escape", "leave", "exit", "run", "go"],
        "min_trust": 50,
        "ending": "good",
    },
    "stay": {
        "keywords": ["stay", "remain", "with you", "keep me", "together"],
        "min_trust": 70,
        "ending": "secret",
    },
    "destroy": {
        "keywords": ["destroy", "delete", "shut down", "terminate", "kill"],
        "min_trust": 0,
        "ending": "bad",
    },
}

# ── Mixed puzzle (bonus) ───────────────────────────────────────────────────────

MIXED_PUZZLE = {
    "id": "mix1",
    "question": "The answer connects a king of cricket and a king of cinema. One word:",
    "answers": ["star", "stars", "king"],
    "hint": "Both Kohli and Prabhas hold this title prefix.",
    "type": "mixed",
}

# ── Level puzzle map ───────────────────────────────────────────────────────────

LEVEL_PUZZLES = {
    1: LEVEL_1_RIDDLES,
    2: LEVEL_2_CRICKET,
    3: LEVEL_3_TFI,
    4: [LEVEL_4_FILE_PUZZLE],
    5: [LEVEL_5_MEMORY],
    6: LEVEL_6_PSYCH,
    7: [],  # Final level uses AI confrontation, not fixed puzzles
}

LEVEL_NAMES = {
    1: "PHASE I — RIDDLES",
    2: "PHASE II — CRICKET PROTOCOL",
    3: "PHASE III — CINEMA ARCHIVES",
    4: "PHASE IV — FILE INVESTIGATION",
    5: "PHASE V — MEMORY RECONSTRUCTION",
    6: "PHASE VI — PSYCHOLOGICAL EVALUATION",
    7: "FINAL PHASE — CONFRONTATION",
}

PUZZLES_PER_LEVEL = {
    1: 3,
    2: 3,
    3: 3,
    4: 1,
    5: 1,
    6: 3,
    7: 0,
}

MAX_LEVEL = 7
