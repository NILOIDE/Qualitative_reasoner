import sys
import itertools


def init_states():
    # data = read_quantity_input_file()
    inflow = {'magnitude': ['0', '+'], 'derivative': ['0']}
    volume = {'magnitude': ['0', '+', 'max'], 'derivative': ['-', '0', '+']}
    outflow = {'magnitude': ['0', '+'], 'derivative': ['-', '0', '+']}
    quantities_labels = ['inflow', 'volume', 'outflow']
    quantities = [inflow['magnitude'], inflow['derivative'], volume['magnitude'], volume['derivative'], outflow['magnitude'], outflow['derivative']]
    permutations = itertools.product(*quantities)
    return permutations


def run(args):
    state = init_states()


if __name__ == '__main__':
    run(sys.argv)
