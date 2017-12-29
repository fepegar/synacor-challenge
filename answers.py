from collections import deque

ANSWERS = [
    'doorway',
    'north',
    'north',
    'bridge',
    'continue',
    'down',
    'east',
    'take empty lantern',
    'west',
    'west',
    'passage',
    'ladder',
    'west',  # solve maze -> W S N
    'south',
    'north',
    'take can',
    'west',
    'ladder',
    'use can',  # fill lantern
    'use lantern',  # light lantern
    'darkness',
    'continue',
    'west',
    'west',
    'west',
    'west',
    'north',
    'take red coin',
    'north',
    'east',
    'take concave coin',
    'down',
    'take corroded coin',
    'up',
    'west',
    'west',
    'take blue coin',
    'up',
    'take shiny coin',
    'down',
    'east',
    'use blue coin',  # solve coins puzzle
    'use red coin',
    'use shiny coin',
    'use concave coin',
    'use corroded coin',
    'north',
    'take teleporter',
    'use teleporter',
    'take business card',
    'take strange book',
]


def get_answers():
    return deque(answer + '\n' for answer in ANSWERS)
