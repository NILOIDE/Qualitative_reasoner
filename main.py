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


def assign_outputs(outputs):
    pass


def determine_transitions(states, labels, dependencies, constraints):
    for state in states:
        possible_outputs = []
        # TODO: value constraints
        # 1. Check for changes in derivatives
        state_values = state.values
        possible_derivative_changes = {'decrease': False, 'increase': False}

        for influenced_idx, value in enumerate(state_values):
            if influenced_idx % 2 != 0:  # There are no dependencies for magnitudes
                continue
            for d in dependencies[influenced_idx]:
                influencer_idx = labels.index(dependencies[d][0])
                if state_values[influencer_idx] == '0':
                    continue
                print(influencer_idx)
                if dependencies[d][0] % 2 == 0:                 # If it is an influence
                    if dependencies[d][1] == '+':
                        if state.next(influenced_idx) is not None:
                            possible_derivative_changes['increase'] = True
                    elif dependencies[d][1] == '-':
                        if state.previous(influenced_idx) is not None:
                            possible_derivative_changes['decrease'] = True
                    else:
                        print("You got a dependency wrong, bro!")
                        quit()
                else:                                           # If it is a proportion
                    if state_values[influencer_idx] == dependencies[d][1]:
                        if state.next(influenced_idx) is not None:
                            possible_derivative_changes['increase'] = True
                    else:
                        if state.previous(influenced_idx) is not None:
                            possible_derivative_changes['decrease'] = True

            if possible_derivative_changes['increase']:
                new_state_values = copy.copy(state_values)
                new_state_values[influenced_idx] = state.next(influenced_idx)
                possible_outputs.append(new_state_values)
            if possible_derivative_changes['decrease']:
                new_state_values = copy.copy(state_values)
                new_state_values[influenced_idx] = state.previous(influenced_idx)
                possible_outputs.append(new_state_values)
        # If there is the possibility of gradient changes counteracting, magnitude changes
        # transitions should be considered
        if not (possible_derivative_changes['increase'] and possible_derivative_changes['decrease']):
            assign_outputs(possible_outputs, constraints)
            continue

        # 2. Check for point value changes
        possible_point_changes = []
        for influenced_idx, value in enumerate(state_values):
            if influenced_idx % 2 == 0:
                continue
            if value == 'max' and state_values[influenced_idx+1] == '-':
                new_state_values = copy.copy(state_values)
                new_state_values[influenced_idx] = state.previous(influenced_idx)
                possible_outputs.append(new_state_values)
                possible_point_changes = True
            if value == '0' and state_values[influenced_idx+1] == '+':
                new_state_values = copy.copy(state_values)
                new_state_values[influenced_idx] = state.next(influenced_idx)
                possible_outputs.append(new_state_values)
                possible_point_changes = True
        # If there are possible point value magnitude changes, there is no point looking for range value changes.
        if possible_point_changes:
            assign_outputs(possible_outputs, constraints)
            continue

        # 3. Check for range value changes
        for influenced_idx, value in enumerate(state_values):
            if influenced_idx % 2 == 0:
                continue
            if value == 'max' and state_values[influenced_idx+1] == '-':
                new_state_values = copy.copy(state_values)
                new_state_values[influenced_idx] = state.previous(influenced_idx)
                possible_outputs.append(new_state_values)
                possible_point_changes = True
            if value == '0' and state_values[influenced_idx+1] == '+':
                new_state_values = copy.copy(state_values)
                new_state_values[influenced_idx] = state.next(influenced_idx)
                possible_outputs.append(new_state_values)
                possible_point_changes = True



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
