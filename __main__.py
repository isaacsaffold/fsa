#! /usr/bin/env python3

import sys

from dfa import DFA, NotInAlphabetError

def read_dfa(file):
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
    auto = None
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as file:
            auto = read_dfa(file)
    else:
        auto = read_dfa(sys.stdin)
    print("Equivalent regex:", auto)
    print("Enter strings to test for acceptance by the DFA, one per line.")
    for line in map(str.rstrip, sys.stdin):
        try:
            print("accepted" if auto(line) else "rejected", end="\n\n")
        except NotInAlphabetError as exc:
            print(exc.args[0] + '\n')

main()
