import sys
import itertools


def init_states():
    # data = read_quantity_input_file()
    derivative = ['-', '0', '+']
    inflow = ['0', '+']
    volume = ['0', '+', 'max']
    outflow = ['0', '+', 'max']
    quantities_labels = ['inflow', 'volume', 'outflow']
    quantities = [inflow, derivative, volume, derivative, outflow, derivative]
    permutations = itertools.product(*quantities)
    return permutations


def run(args):
    states = init_states()
    for p in states:
        print(p)


if __name__ == '__main__':
    run(sys.argv)
