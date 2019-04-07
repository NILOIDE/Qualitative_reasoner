class State:

    # All possible values for inflow, outflow/volume, and their derivatives
    i_values = ['0', '+']
    ov_values = ['0', '+', 'max']
    d_values = ['-', '0', '+']

    # Count of all states, so we can have unique IDs
    count = 0

    def __init__(self, i_v, i_d, o_v, o_d, v_v, v_d):
        self.values = [i_v, i_d, o_v, o_d, v_v, v_d]
        self.id = State.count
        State.count += 1

    def __str__(self):
        i = "I(" + ', '.join(self.values[0:2]) + '), '
        o = "O(" + ', '.join(self.values[2:4]) + '), '
        v = "V(" + ', '.join(self.values[4:6]) + ')'
        return str(self.id) + ': ' + i + o + v

    def check_validity(self):
        if self.values[0] not in State.i_values or self.values[1] not in State.d_values\
                or self.values[2] not in State.ov_values or self.values[3] not in State.d_values\
                or self.values[4] not in State.ov_values or self.values[5] not in State.d_values:
            print("WARNING: illegal state")

    def get_id(self):
        return self.id
