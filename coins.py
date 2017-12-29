from itertools import permutations

def main():
    coins = 2, 9, 5, 7, 3
    possible = permutations(coins)
    for a, b, c, d, e in possible:
        if a + b * c**2 + d**3 - e == 399:
            print(a, b, c, d, e)

if __name__ == '__main__':
    main()
