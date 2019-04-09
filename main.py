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
    dependencies[q_labels.index('volume')*2+1] = []
    dependencies[q_labels.index('volume')*2+1].append([q_labels.index('inflow')*2, '+'])
    dependencies[q_labels.index('volume')*2+1].append([q_labels.index('outflow')*2, '-'])
    dependencies[q_labels.index('outflow')*2+1] = []
    dependencies[q_labels.index('outflow')*2+1].append([q_labels.index('volume')*2+1, '+'])
    constraints = {}
    constraints[q_labels.index('volume')*2] = []
    constraints[q_labels.index('outflow')*2] = []
    constraints[q_labels.index('volume')*2].append(['max', q_labels.index('outflow')*2, 'max'])
    constraints[q_labels.index('outflow')*2].append(['max', q_labels.index('outflow')*2, 'max'])
    constraints[q_labels.index('volume')*2].append(['0', q_labels.index('outflow')*2, '0'])
    constraints[q_labels.index('outflow')*2].append(['0', q_labels.index('outflow')*2, '0'])
    return dependencies, constraints


def assign_outputs(states, s, raw_outputs, constraints):
    filtered_outputs = []
    for raw_output in raw_outputs:
        # Apply VC constraints
        for influencer_idx in range(len(raw_output)):
            if raw_output[influencer_idx] == s.values[influencer_idx]:  # If the value was not modified
                continue
            if influencer_idx not in constraints:
                continue
            for c in constraints[influencer_idx]:
                if raw_output[influencer_idx] == c[0]:
                    raw_output[c[1]] = c[2]
        if raw_output not in filtered_outputs:  # Check that constraint edit didn't create a state already in list
            filtered_outputs.append(raw_output)
        # else:
        #     print('ayy', print(filtered_outputs))
        #     quit()

    for output in filtered_outputs:
        # Put corresponding states in this state's outputs
        state_exists = False
        for state in states:
            if state.get_id() == s.get_id():
                continue
            if state.is_equal(output):
                if state in s.outputs:
                    print("????")
                    quit()
                s.add_output(state)
                state_exists = True
                break
        if not state_exists:
            print("This state does not exist!", output)


def determine_transitions(states, dependencies, constraints):
    for state in states:
        state_values = state.values
        print("state ", state.get_id(), ":")
        print(state_values, "\n")
        # 1. Check for point value changes
        new_state_values = list(copy.copy(state_values))
        possible_point_changes = False
        for influenced_idx, value in enumerate(state_values):
            if influenced_idx % 2 != 0:  # Only magnitudes are being checked here
                continue
            if state_values[influenced_idx + 1] == '0':  # If derivative is 0, nothing is going to change
                continue
            if value == 'max' and state_values[influenced_idx + 1] == '-':
                new_state_values[influenced_idx] = state.previous(influenced_idx)
                possible_point_changes = True
            if value == '0' and state_values[influenced_idx + 1] == '+':
                new_state_values[influenced_idx] = state.next(influenced_idx)
                possible_point_changes = True

        # 2. Check for derivative AND range value changes:
        possible_values = {idx: {value} for idx, value in enumerate(new_state_values)}
        for influenced_idx, value in enumerate(state_values):
            # Check for changes in derivatives
            if influenced_idx % 2 == 0:  # There are no dependencies for magnitudes
                continue
            if influenced_idx not in dependencies:
                continue
            for d in dependencies[influenced_idx]:
                influencer_idx = d[0]
                if state_values[influencer_idx] == '0':
                    continue
                if d[0] % 2 == 0:                 # If it is an influence
                    if d[1] == '+':
                        if state.next(influenced_idx) is not None:
                            possible_values[influenced_idx].add(state.next(influenced_idx))
                    elif d[1] == '-':
                        if state.previous(influenced_idx) is not None:
                            possible_values[influenced_idx].add(state.previous(influenced_idx))
                    else:
                        print("You got a dependency wrong, bro!")
                        quit()
                else:                              # If it is a proportion
                    if state_values[influencer_idx] == d[1]:
                        if state.next(influenced_idx) is not None:
                            possible_values[influenced_idx].add(state.next(influenced_idx))
                    else:
                        if state.previous(influenced_idx) is not None:
                            possible_values[influenced_idx].add(state.previous(influenced_idx))

        # If there are possible point value magnitude changes, those changes will happen instantly, so there is
        # no point looking for range value changes.
        if possible_point_changes:
            possible_outputs = [list(i) for i in itertools.product(*[possible_values[key] for key in possible_values])]
            if state_values in possible_outputs:
                print("Original state shouldn't be in here.")
                quit()
            # possible_outputs.remove(state_values)
            print(possible_values)
            assign_outputs(states, state, possible_outputs, constraints)
            continue
        # Check for range value changes
        for influenced_idx, value in enumerate(state_values):
            if influenced_idx % 2 != 0:  # Only magnitudes are being checked here
                continue
            if state_values[influenced_idx+1] == '0':  # If derivative is 0, nothing is going to change
                continue
            if value == 'max' and value == '0':  # Point values were already checked earlier
                print("Why is there a point value check here?", state_values)
                quit()
                continue
            if state_values[influenced_idx+1] == '-':
                if state.previous(influenced_idx) is not None:
                    possible_values[influenced_idx].add(state.previous(influenced_idx))
            elif state_values[influenced_idx+1] == '+':
                if state.next(influenced_idx) is not None:
                    possible_values[influenced_idx].add(state.next(influenced_idx))
            else:
                print("You got a dependency wrong, bro!")
                quit()
        possible_outputs = [list(i) for i in itertools.product(*[possible_values[key] for key in possible_values])]
        possible_outputs.remove(state_values)
        print(possible_values)
        assign_outputs(states, state, possible_outputs, constraints)
        print("______________")


def get_unused_states(states):
    # Returns states that don't have outputs and which are not outputs
    states_set = set(states)
    used_states_set = set()
    for state in states:
        outs = state.get_outputs()
        if outs:
            used_states_set.add(state)
            for out in outs:
                used_states_set.add(out)
    return list(states_set - used_states_set)


def run(args):
    raw_states, q_labels = init_states()
    remove_illegal_states(raw_states)
    dependencies, constraints = create_dependencies(q_labels)
    states = []
    for p in raw_states:

        states.append(State(list(p)))
    for s in states:
        print(s)
    determine_transitions(states, dependencies, constraints)
    for s in states:
        print("___________________________")
        print(s)
    print("***************************************************")
    unused = get_unused_states(states)
    for s in unused:
        print("___________________________")
        print(s)


if __name__ == '__main__':
    run(sys.argv)
