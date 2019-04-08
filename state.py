class State:

    # All possible values for inflow, outflow/volume, and their derivatives
    i_values = ['0', '+']
    ov_values = ['0', '+', 'max']
    d_values = ['-', '0', '+']

    # Count of all states, so we can have unique IDs
    count = 0

    def __init__(self, values):
        self.values = values
        self.id = State.count
        State.count += 1
        self.inputs = []
        self.outputs = []
        self.check_validity()

    def __str__(self):
        i = "I(" + ', '.join(self.values[0:2]) + '), '
        o = "O(" + ', '.join(self.values[2:4]) + '), '
        v = "V(" + ', '.join(self.values[4:6]) + ')'
        id_str = str(self.id) if self.id > 9 else '0' + str(self.id)
        state_string = id_str + ': ' + i + o + v + '\n'
        out_string = ''
        for out in self.outputs:
            out_values = out.get_values()
            out_id = out.get_id()
            i = "I(" + ', '.join(out_values[0:2]) + '), '
            o = "O(" + ', '.join(out_values[2:4]) + '), '
            v = "V(" + ', '.join(out_values[4:6]) + ')'
            id_str = str(out_id) if self.id > 9 else '0' + str(self.id)
            out_string = out_string + '\t' + id_str + ': ' + i + o + v + '\n'
        return state_string + out_string

    def get_values(self):
        return self.values

    def check_validity(self):
        if self.values[0] not in State.i_values or self.values[1] not in State.d_values\
                or self.values[2] not in State.ov_values or self.values[3] not in State.d_values\
                or self.values[4] not in State.ov_values or self.values[5] not in State.d_values:
            print("\nWARNING: illegal state")
            print(self, "\n")

    def get_id(self):
        return self.id

    def add_input(self, input_state):
        self.inputs.append(input_state)

    def get_inputs(self):
        return self.inputs

    def add_output(self, output_state):
        self.outputs.append(output_state)

    def get_outputs(self):
        return self.outputs

    def is_equal(self, values):
        return self.values == values

    def next(self, v_idx):
        v_new = None
        current = self.values[v_idx]
        if v_idx in [1, 3, 5]:
            d_idx = State.d_values.index(current)
            new_idx = max(0, min(d_idx + 1, 2))
            v_new = State.d_values[new_idx]
        elif v_idx == 0:
            i_idx = State.i_values.index(current)
            new_idx = max(0, min(i_idx + 1, 1))
            v_new = State.i_values[new_idx]
        elif v_idx in [2, 4]:
            ov_idx = State.ov_values.index(current)
            new_idx = max(0, min(ov_idx + 1, 2))
            v_new = State.ov_values[new_idx]
        return v_new if v_new != current else None

    def previous(self, v_idx):
        v_new = None
        current = self.values[v_idx]
        if v_idx in [1, 3, 5]:
            d_idx = State.d_values.index(current)
            new_idx = max(0, min(d_idx - 1, 2))
            v_new = State.d_values[new_idx]
        elif v_idx == 0:
            i_idx = State.i_values.index(current)
            new_idx = max(0, min(i_idx - 1, 1))
            v_new = State.i_values[new_idx]
        elif v_idx in [2, 4]:
            ov_idx = State.ov_values.index(current)
            new_idx = max(0, min(ov_idx - 1, 2))
            v_new = State.ov_values[new_idx]
        return v_new if v_new != current else None
