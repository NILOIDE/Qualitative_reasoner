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
    constraints[q_labels.index('outflow')*2].append(['max', q_labels.index('volume')*2, 'max'])
    constraints[q_labels.index('volume')*2].append(['0', q_labels.index('outflow')*2, '0'])
    constraints[q_labels.index('outflow')*2].append(['0', q_labels.index('volume')*2, '0'])
    return dependencies, constraints


def assign_outputs(states, s, raw_outputs, constraints, possible_traces):
    filtered_outputs = []
    filtered_traces = []
    for output_idx, raw_output in enumerate(raw_outputs):
        # Apply VC constraints
        constraints_applied = False
        for influencer_idx in range(len(raw_output)):
            if influencer_idx not in constraints:
                continue
            for c in constraints[influencer_idx]:
                if raw_output[influencer_idx] == c[0] and raw_output[c[1]] != c[2]:
                    raw_output[c[1]] = c[2]
                    constraints_applied = True
        if raw_output not in filtered_outputs:  # Check that constraint edit didn't create a state already in list
            filtered_outputs.append(raw_output)
            if constraints_applied:
                possible_traces[output_idx][1] = "Unstable state"
                possible_traces[output_idx].append(["Constraint applied:", get_corresponding_state(states, raw_output)])
            filtered_traces.append(possible_traces[output_idx])


    print("Possible outputs:")
    for trace, output in zip(filtered_traces, filtered_outputs):
        print("output",output)
        print("trace", trace)
        # Put corresponding states in this state's outputs
        state_exists = False
        for state in states:
            if state.is_equal(output):
                if state in s.outputs:
                    print("????")
                    quit()
                s.add_output(state, trace)
                state_exists = True
                break
        if not state_exists:
            print("^This state does not exist!")
            quit()


def set_unaffected_gradients_to_zero(state_values, dependencies):
    change_has_been_made = False
    for influenced_idx, value in enumerate(state_values):
        if influenced_idx % 2 == 0:  # Dependencies only apply to derivatives
            continue
        if value == '0':
            continue
        all_dependencies_are_zero = True
        if influenced_idx in dependencies:
            for d in dependencies[influenced_idx]:
                influencer_idx = d[0]
                if state_values[influencer_idx] != '0':
                    all_dependencies_are_zero = False
                    break
        if all_dependencies_are_zero:
            state_values[influenced_idx] = '0'
            change_has_been_made = True
    return state_values, change_has_been_made


def fix_derivative_discrepancies(state, dependencies, original_state_values):
    change_has_been_made = False
    for influenced_idx, value in enumerate(state.values):
        if influenced_idx % 2 == 0:  # Dependencies only apply to derivatives
            continue
        if state.current(influenced_idx) != original_state_values[influenced_idx]:
            continue
        discrepancy_directions = set()
        if influenced_idx in dependencies:
            for d in dependencies[influenced_idx]:
                influencer_idx = d[0]
                if state.current(influencer_idx) == '0':
                    continue
                if d[0] % 2 == 0:  # If it is an influence
                    if d[1] == '+':
                        if state.next(influenced_idx) is not None:
                            discrepancy_directions.add(state.next(influenced_idx))
                        else:
                            discrepancy_directions.add(state.current(influenced_idx))
                    elif d[1] == '-':
                        if state.previous(influenced_idx) is not None:
                            discrepancy_directions.add(state.previous(influenced_idx))
                        else:
                            discrepancy_directions.add(state.current(influenced_idx))
                    else:
                        print("You got a dependency wrong, bro!")
                        quit()
                else:  # If it is a proportion
                    if state.current(influencer_idx) == d[1]:
                        if state.next(influenced_idx) is not None:
                            discrepancy_directions.add(state.next(influenced_idx))
                        else:
                            discrepancy_directions.add(state.current(influenced_idx))
                    else:
                        if state.previous(influenced_idx) is not None:
                            discrepancy_directions.add(state.previous(influenced_idx))
                        else:
                            discrepancy_directions.add(state.current(influenced_idx))

        if len(discrepancy_directions) == 0:
            if state.current(influenced_idx) != '0':
                state.values[influenced_idx] = '0'
                change_has_been_made = True
        elif len(discrepancy_directions) == 1 and list(discrepancy_directions)[0] == '+':
            # if state_values[influenced_idx] == '0': # TODO: choice made here
            if state.next(influenced_idx) is not None:
                state.values[influenced_idx] = state.next(influenced_idx)
                change_has_been_made = True
        elif len(discrepancy_directions) == 1 and list(discrepancy_directions)[0] == '-':
            # if state_values[influenced_idx] == '0':
            if state.previous(influenced_idx) is not None:
                state.values[influenced_idx] = state.previous(influenced_idx)
                change_has_been_made = True

    return state.values, change_has_been_made


def make_point_value_changes(state_values, state):
    change_has_been_made = False
    for influenced_idx, value in enumerate(state_values):
        if influenced_idx % 2 != 0:  # Only magnitudes are being checked here
            continue
        if state_values[influenced_idx + 1] == '0':  # If derivative is 0, nothing is going to change
            continue
        if value == 'max' and state_values[influenced_idx + 1] == '-':
            state_values[influenced_idx] = state.previous(influenced_idx)
            change_has_been_made = True
        if value == '0' and state_values[influenced_idx + 1] == '+':
            state_values[influenced_idx] = state.next(influenced_idx)
            change_has_been_made = True

    return state_values, change_has_been_made


def add_possible_derivative_changes(state_values, dependencies, state, possible_values):
    for influenced_idx, value in enumerate(state_values):
        # Check for changes in derivatives
        if influenced_idx % 2 == 0:  # There are no dependencies for magnitudes
            continue
        if influenced_idx not in dependencies:  # If this derivative doesn't have dependencies, skip it
            continue
        for d in dependencies[influenced_idx]:
            influencer_idx = d[0]
            if state_values[influencer_idx] == '0':
                continue
            if d[0] % 2 == 0:  # If it is an influence
                if d[1] == '+':
                    if state.next(influenced_idx) is not None:
                        if state.next(influenced_idx-1) is not None:
                            possible_values[influenced_idx].add(state.next(influenced_idx))
                        else:
                            possible_values[influenced_idx].add(state.current(influenced_idx))
                elif d[1] == '-':
                    if state.previous(influenced_idx) is not None:
                        if state.previous(influenced_idx-1) is not None:
                            possible_values[influenced_idx].add(state.previous(influenced_idx))
                        else:
                            possible_values[influenced_idx].add(state.current(influenced_idx))
                else:
                    print("You got a dependency wrong, bro!")
                    quit()
            else:  # If it is a proportion
                if state_values[influencer_idx] == d[1]:
                    if state.next(influenced_idx) is not None:
                        if state.next(influenced_idx - 1) is not None:
                            possible_values[influenced_idx].add(state.next(influenced_idx))
                        else:
                            possible_values[influenced_idx].add(state.current(influenced_idx))
                else:
                    if state.previous(influenced_idx) is not None:
                        if state.previous(influenced_idx-1) is not None:
                            possible_values[influenced_idx].add(state.previous(influenced_idx))
                        else:
                            possible_values[influenced_idx].add(state.current(influenced_idx))


def add_possible_range_value_changes(state_values, state, possible_values):
    for influenced_idx, value in enumerate(state_values):
        if influenced_idx % 2 != 0:  # Only magnitudes are being checked here
            continue
        if state_values[influenced_idx + 1] == '0':  # If derivative is 0, nothing is going to change
            continue
        if value == 'max' or value == '0':  # Point values were already checked earlier
            continue
        if state_values[influenced_idx + 1] == '-':
            if state.previous(influenced_idx) is not None:
                possible_values[influenced_idx].add(state.previous(influenced_idx))
            else:
                possible_values[influenced_idx].add(state.current(influenced_idx))
        elif state_values[influenced_idx + 1] == '+':
            if state.next(influenced_idx) is not None:
                possible_values[influenced_idx].add(state.next(influenced_idx))
            else:
                possible_values[influenced_idx].add(state.current(influenced_idx))
        else:
            print("You got a dependency wrong, bro!")
            quit()


def determine_transitions(states, dependencies, constraints):
    for state in states:
        trace = []
        state_values = state.values
        print("state ", state.get_id(), ":")
        print(state_values, "\n")

        new_state_values = list(copy.copy(state_values))
        # Step 1: Check for derivative and point values that MUST change (non-stable states)
        new_state_values, derivative_change_has_been_made = fix_derivative_discrepancies(State(new_state_values),
                                                                                         dependencies, state_values)
        if derivative_change_has_been_made:
            while derivative_change_has_been_made :
                # - Set derivative to 0 if their dependencies are 0
                iter_values = copy.copy(new_state_values)
                new_state_values, derivative_change_has_been_made = fix_derivative_discrepancies(State(iter_values),
                                                                                             dependencies, state_values)
            trace.append(["Forced derivative changes: ", get_corresponding_state(states, new_state_values)])
            derivative_change_has_been_made = True
            point_value_change_has_been_made = False
        else:
            # - Check for point value changes
            new_state_values, point_value_change_has_been_made = make_point_value_changes(new_state_values, state)
            if point_value_change_has_been_made:
                trace.append(["Forced point value changes: ", get_corresponding_state(states, new_state_values)])

        # Step 2. Check for ambiguous derivative and range value changes:
        possible_values = {idx: set() for idx, value in enumerate(new_state_values)}
        # If there are possible point value magnitude changes, those changes will happen instantly, so there is
        # no point looking for range value changes.
        if not point_value_change_has_been_made and not derivative_change_has_been_made:
            # - Check for range value changes (if point changes were not made
            add_possible_range_value_changes(state_values, state, possible_values)
            # - Check for derivative changes:
            add_possible_derivative_changes(state_values, dependencies, state, possible_values)
        print(possible_values)

        added_possibility = False
        for p in possible_values:
            if len(possible_values[p]) != 0:
                added_possibility = True
        print("P", possible_values)
        # If derivative possible values contains '+' and '-', then the possibility of '0' should be added
        possible_values = {idx: possible_values[idx] if idx % 2 == 0 or len(possible_values[idx]) < 2 else possible_values[idx].union({'0'})
                           for idx in possible_values}
        print("Ambiguous values:\n", possible_values)
        # Added current values to values that haven't changed
        possible_values = {idx: {value} if possible_values[idx] == set() else possible_values[idx]
                           for idx, value in enumerate(new_state_values)}
        # Create permutations
        possible_outputs = [list(i) for i in itertools.product(*[possible_values[key] for key in possible_values])]

        # Step 3: Check for derivative and point values that MUST change (non-stable states)
        possible_final_outputs = []
        possible_traces = []
        for idx, output in enumerate(possible_outputs):
            # added_possibility = True if output != state_values else False
            possible_traces.append(copy.copy(trace))
            if added_possibility:
                if output != state_values:
                    possible_traces[idx].append(["Possible range value or derivative changes: ",
                                                get_corresponding_state(states, output)])
                else:
                    possible_traces[idx].append(["State remains unchanged: ",
                                                 get_corresponding_state(states, output)])
            output, derivative_change_has_been_made = fix_derivative_discrepancies(State(output), dependencies, state_values)
            if derivative_change_has_been_made:
                while derivative_change_has_been_made:
                    # - Set derivative to 0 if their dependencies are 0
                    output, derivative_change_has_been_made = fix_derivative_discrepancies(State(output), dependencies, state_values)
                if added_possibility:
                    possible_traces[idx][-1][1] = "Unstable state"
                    possible_traces[idx].append(
                        ["Forced derivative changes: ", get_corresponding_state(states, output)])
                else:
                    if possible_traces[-1] != []:
                        possible_traces[-1][-1][1] = "Unstable state"
                    possible_traces[idx].append(
                        ["Forced derivative changes: ", get_corresponding_state(states, output)])
            # - Check for point value changes
            # TODO: Just added this next line
            possible_final_outputs.append(output)

        print("Value possibilities:\n", possible_values)
        assign_outputs(states, state, possible_final_outputs, constraints, possible_traces)
        print("______________")


def get_corresponding_state(states, state_values):
    for state in states:
        if state.is_equal(state_values):
            return str(state.get_id())
    return 'Unstable state'

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
    print("############## GRAPH ENCODING ##############")
    for state in states:
        state.print_connections()


if __name__ == '__main__':
    run(sys.argv)
