import random
import os

# Generate random input boxes
num_boxes = 15  # Number of boxes
max_dim = 56  # Maximum dimension of a box

boxes = []
for i in range(num_boxes):
    dims = [random.randint(1, max_dim) for _ in range(3)]
    boxes.append(dims)
    boxes[-1].insert(0, i + 1)  # Insert box index at the beginning

# Get pallet size from user input
pallet_dims = input("Enter the pallet size (format: dim1, dim2, dim3): ").strip().split(',')
pallet_dims = [int(dim.strip()) for dim in pallet_dims]

# Save random input to a text file
filename = os.path.join(os.getcwd(), '8.txt')
with open(filename, 'w') as file:
    file.write("1\n")
    file.write(', '.join(str(dim) for dim in pallet_dims) + '\n')
    for box in boxes:
        file.write(', '.join(str(dim) for dim in box) + '\n')

print(f"Random input saved to {filename}.")
