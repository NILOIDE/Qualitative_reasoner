import sys
import itertools
import numpy as np

from state import State


def remove_illegal_states(states):
    rules = np.loadtxt('elimination_rules.txt', comments='#', dtype=str, delimiter=' ')
    to_be_removed = []
    for state in states:
        for rule in rules:
            if len(rule) == 0:
                continue
            decision = True  # State is to be removed unless proved innocent
            for i, item in enumerate(rule):
                if item == '*':
                    continue
                # If an item in the rule is different from item in the state, state is not removed
                elif item != state[i]:
                    decision = False
                    break
            # If a state matches even 1 rule, it is to be removed
            if decision:
                to_be_removed.append(state)
                break
    for s in to_be_removed:
        states.remove(s)


def init_states():
    derivative = ['-', '0', '+']
    inflow = ['0', '+']
    volume = ['0', '+', 'max']
    outflow = ['0', '+', 'max']
    quantities_labels = ['inflow', 'volume', 'outflow']
    quantities = [inflow, derivative, volume, derivative, outflow, derivative]
    permutations = itertools.product(*quantities)
    return list(permutations)


def run(args):
    raw_states = init_states()
    remove_illegal_states(raw_states)
    states = []
    for p in raw_states:
        states.append(State(p))
    for s in states:
        print(s)


if __name__ == '__main__':
    run(sys.argv)
