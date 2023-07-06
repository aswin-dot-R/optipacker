from palletier import Solver, Box, Pallet
from pathlib import Path

def main():
    test_case = int(input('Enter test case:'))
    if 0 < test_case < 12:
        print('Solving test case {}'.format(test_case))
        test_p, test_b = initialize_from_file(test_case)
        solver = Solver(test_p, test_b)
        solver.pack()
        solver.print_solution()
    else:
        print('Test case does not exist. Exiting.')




def initialize_from_file(test_case):
    test_filename = "/home/ashie/palletier/examples/inputs/{}.txt".format(test_case)
    with open(test_filename, 'r', encoding='utf-8') as input_file:
        pallets = []
        boxes = []
        pallet_num = int(input_file.readline())
        for i in range(pallet_num):
            pallet_line = input_file.readline()
            pallet_dims = [int(dim.strip())
                           for dim in pallet_line.strip().split(',')]
            pallets.append(Pallet(pallet_dims))
        for line in input_file:
            *dims, num = (int(dim.strip()) for dim in line.strip().split(','))
            for i in range(num):
                boxes.append(Box(dims))
        return pallets, boxes


if __name__ == '__main__':
    main()
