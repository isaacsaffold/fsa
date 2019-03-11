import sys

from dfa import DFA

def read_dfa(filename):
    with open(filename) as file:
        states = file.readline().rstrip().split(',')
        alphabet = file.readline().rstrip().split(',')
        transitions = []
        tokens = file.readline().rstrip().split(',')
        while len(tokens) == 3:
            transitions.append(tokens)
            tokens = file.readline().rstrip().split(',')
        initial = tokens[0]
        line = file.readline().rstrip()
        accepting = line.split(',') if line else []
    return DFA(states, alphabet, transitions, initial, accepting)
    
def main():
    auto = read_dfa(sys.argv[1])
    print("Equivalent regex:", auto)
    print("Enter strings to test for acceptance by the DFA, one per line.")
    for line in map(str.rstrip, sys.stdin):
        print("accepted" if auto(line) else "rejected")

if __name__ == "__main__":
    main()
