import sys
import itertools
import numpy as np
import copy

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
    quantities_labels = ['inflow', 'outflow', 'volume']
    quantities = [inflow, derivative, outflow, derivative, volume, derivative]
    permutations = itertools.product(*quantities)
    return list(permutations), quantities_labels


def create_dependencies(q_labels):
    dependencies = {}
    dependencies[q_labels.index('volume')*2+1] = [q_labels.index('inflow')*2, '+']
    dependencies[q_labels.index('volume')*2+1] = [q_labels.index('outflow')*2, '-']
    dependencies[q_labels.index('outflow')*2+1] = [q_labels.index('volume')*2+1, '+']
    constraints = {}
    constraints[q_labels.index('volume')*2] = ['max', q_labels.index('outflow')*2, 'max']
    constraints[q_labels.index('outflow')*2] = ['max', q_labels.index('volume')*2, 'max']
    constraints[q_labels.index('volume')*2] = ['0', q_labels.index('outflow')*2, '0']
    constraints[q_labels.index('outflow')*2] = ['0', q_labels.index('volume')*2, '0']
    return dependencies, constraints


def determine_transitions(states, labels, dependencies, constraints):
    for state in states:
        possible_outputs = []
        # 1. Check for changes in derivatives
        state_values = state.values
        for influenced, value in enumerate(state_values):
            if influenced % 2 != 0:
                continue
            possible_changes = {'decrease': False, 'increase': False}
            for d in dependencies[influenced]:
                influencer_idx = labels.index(dependencies[d][0])
                if state_values[influencer_idx] == '0':
                    continue
                print(influencer_idx)
                if dependencies[d][0] % 2 == 0:                 # If it is an influence
                    if state_values[influencer_idx] == dependencies[d][1]:
                        new_value = state.next(influenced)
                        possible_changes['increase'] = True
                    else:
                        new_value = state.previous(influenced)
                        possible_changes['decrease'] = True
                else:                                           # If it is a proportion
                    if dependencies[d][1] == '+':
                        new_value = state.next(influenced)
                        possible_changes['increase'] = True
                    elif dependencies[d][1] == '-':
                        new_value = state.previous(influenced)
                        possible_changes['decrease'] = True
                    else:
                        print("You got a dependency wrong, bro!")
                        quit()

            if possible_changes['increase']:
                new_values = copy.copy(state_values)
                new_values[influenced] = new_value
                possible_outputs.append(new_values)
            if possible_changes['decrease']:
                new_values = copy.copy(state_values)
                new_values[influenced] = new_value
                possible_outputs.append(new_values)
            # TODO: Stay same
            if not (possible_changes['increase'] and possible_changes['decrease']):
                continue



        # 2. Check for point value changes
        for influenced, values in enumerate(state_values):
            if influenced % 2 == 0:
                continue


def run(args):
    raw_states, q_labels = init_states()
    remove_illegal_states(raw_states)
    dependencies, constraints = create_dependencies(q_labels)
    states = []
    for p in raw_states:
        states.append(State(p))
    for s in states:
        print(s)
    determine_transitions(states, q_labels, dependencies, constraints)

if __name__ == '__main__':
    run(sys.argv)
