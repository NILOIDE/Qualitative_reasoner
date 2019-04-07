import sys
import itertools


def read_quantity_input_file():
    pass
    # with open('test_set/' + args[3], "r") as file:
    #         for i, line in enumerate(file):


def create_quantity_permutations(quantities):
    if not quantities:
        return True
    keys = [*quantities]



def init_states():
    # data = read_quantity_input_file()
    inflow = {'magnitude': ['0', '+'], 'derivative': ['0']}
    volume = {'magnitude': ['0', '+', 'max'], 'derivative': ['-', '0', '+']}
    outflow = {'magnitude': ['0', '+'], 'derivative': ['-', '0', '+']}
    quantities_labels = ['inflow', 'volume', 'outflow']
    quantities = [inflow['magnitude'], inflow['derivative'], volume['magnitude'], volume['derivative'], outflow['magnitude'], outflow['derivative']]
    # permutations = list(zip(quantities))
    permutations = itertools.permutations(quantities)
    for p in permutations:
        print(p)
    return permutations


def run(args):
    state = init_states()


if __name__ == '__main__':
    run(sys.argv)
