from itertools import permutations

COINS = {
    2: 'red',
    9: 'blue',
    5: 'shiny',
    7: 'concave',
    3: 'corroded',
}

def main():
    possible = permutations(COINS.keys())
    for permutation in possible:
        a, b, c, d, e = permutation
        if a + b * c**2 + d**3 - e == 399:
            for n in permutation:
                print(COINS[n], n)
            break


if __name__ == '__main__':
    main()
