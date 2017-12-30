import sys
from random import choice
from operator import add, mul, sub

GRID = {
    (0, 0): 22,
    (0, 1): add,
    (0, 2): 4,
    (0, 3): mul,
    (1, 0): sub,
    (1, 1): 4,
    (1, 2): mul,
    (1, 3): 8,
    (2, 0): 9,
    (2, 1): sub,
    (2, 2): 11,
    (2, 3): sub,
    (3, 0): mul,
    (3, 1): 18,
    (3, 2): mul,
    (3, 3): 1,
}

NORTH = (0, 1)
SOUTH = (0, -1)
EAST = (1, 0)
WEST = (-1, 0)

tried = []
while True:
    n = 22
    steps = 0
    x, y = 0, 0
    path = []
    operator_found = None
    while steps < 12:
        choices = [NORTH, SOUTH, EAST, WEST]

        if x == 0:
            choices.remove(WEST)
        elif x == 3:
            choices.remove(EAST)

        if y == 0:
            choices.remove(SOUTH)
        elif y == 3:
            choices.remove(NORTH)

        dx, dy = choice(choices)

        new_x, new_y = x + dx, y + dy

        if (new_x, new_y) == (0, 0):
            break

        if operator_found is None:
            operator_found = GRID[(new_x, new_y)]
        else:
            number_found = GRID[(new_x, new_y)]
            n = operator_found(n, number_found)
            operator_found = None

        path.append((new_x, new_y))
        if (new_x, new_y) == (3, 3):
            if n == 30:
                # Eureka! [(0, 1), (1, 1), (2, 1), (2, 2), (1, 2), (1, 1),
                #          (2, 1), (3, 1), (2, 1), (2, 2), (2, 3), (3, 3)]
                print('Eureka!', path)
                sys.exit(0)
            else:
                print('Not there:', n)
                break
        x, y = new_x, new_y
        steps += 1
