import collections
from itertools import permutations
from copy import copy, deepcopy

from palletier.box import Box
from palletier.packer import Packer
from palletier.pallet import Pallet
from palletier.packedpallet import PackedPallet
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
Dims = collections.namedtuple('Dims', ['dim1', 'dim2', 'dim3'])


class Solver:
    """The volume optimization solver"""
    def __init__(self, pallets, boxes):
        """Initializes the solver with the pallets available and the boxes
        to be packed.

        Args:
            pallets ([Pallet]): The list of pallets available to the solver
            boxes ([Box]): The boxes to be packed

        Raises:
            TypeError: If an element in pallets is not a Pallet
            TypeError: If an element in boxes is not a Box
        """

        if all(isinstance(pallet, Pallet) for pallet in pallets):
            self.pallets = pallets
        else:
            raise TypeError('All elements of the pallets list '
                            'must be of type Pallet')

        if all(isinstance(pallet, Pallet) for pallet in pallets):
            self.boxes = boxes
        else:
            raise TypeError('All elements of the boxes list '
                            'must be of type Box')
        self.total_num_boxes = len(self.boxes)
        self.total_boxes_vol = sum(box.vol for box in self.boxes)
        self.packed_pallets = []

    def pack(self):
        remaining_boxes = self.boxes
        while len(remaining_boxes) != 0:  # All boxes need to be packed
            single_solutions = []  # A solution for each pallet type
            for pallet in self.pallets:
                packer = Packer(remaining_boxes, pallet)
                pallet_ori, packed, unpacked, util = packer.iterations()
                single_solutions.append((pallet_ori, packed, unpacked, util))
                pallet.weight = 0  # Reset weight for next iteration
            # Get the best solution by utilization percentage
            solution = max(single_solutions, key=lambda x: x[3])
            best_pallet, best_packed, best_unpacked, vol_util = solution
            # Make this a test
            # The boxes we sent to pack do not fit into any pallets
            if len(best_unpacked) == len(remaining_boxes):
                for box in best_unpacked:
                    box.orientation = box.dims
                    self.packed_pallets.append(PackedPallet(
                        Pallet(dims=box.dims, name='BOX', ptype=0,
                               orientation=box.dims),
                        [box],
                    ))
                break
            else:
                self.packed_pallets.append(PackedPallet(copy(best_pallet),
                                                        deepcopy(best_packed)))
                remaining_boxes = best_unpacked

   
    def print_solution(self):
        for packed in self.packed_pallets:
            fig = plt.figure()
            # Set figure title ('Pallet #{0}'.format(packed.idx)) 
             
            ax = fig.add_subplot(111, projection='3d')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')

            # Generate colors for each box
            colors = plt.cm.tab20(np.linspace(0, 1, packed.num_boxes))

            dims = packed.pallet.orientation
            print('Packed Pallet #{0} with utilization of {1}'.format(
                packed.idx, packed.utilization))
            print('Using Pallet #{0} with dims ({1}, {2}, {3})'.format(
                packed.idx, (*dims)))
            print('With {0} boxes:'.format(packed.num_boxes))

            for i, box in enumerate(packed.boxes):
                # Print box details
                print('Box #{0} with dims ({1}, {2}, {3}) located at ({4}, {5}, {6})'.format(
                    box.idx, (*box.orientation), (*box.pos)))

                # Get the position and dimensions of the box
                x, y, z = box.pos
                w, h, d = box.orientation

                # Define the vertices of the box
                vertices = [
                    [x, y, z],
                    [x + w, y, z],
                    [x + w, y + h, z],
                    [x, y + h, z],
                    [x, y, z + d],
                    [x + w, y, z + d],
                    [x + w, y + h, z + d],
                    [x, y + h, z + d]
                ]

                # Define the faces of the box
                faces = [
                    [vertices[0], vertices[1], vertices[2], vertices[3]],  # Bottom face
                    [vertices[4], vertices[5], vertices[6], vertices[7]],  # Top face
                    [vertices[0], vertices[1], vertices[5], vertices[4]],  # Side face 1
                    [vertices[1], vertices[2], vertices[6], vertices[5]],  # Side face 2
                    [vertices[2], vertices[3], vertices[7], vertices[6]],  # Side face 3
                    [vertices[3], vertices[0], vertices[4], vertices[7]]   # Side face 4
                ]

                # Create a Poly3DCollection object and set the color
                box_collection = Poly3DCollection(faces, alpha=0.8)
                box_collection.set_facecolor(colors[i])

                # Add the box to the plot
                ax.add_collection3d(box_collection)

                # Add box edges for better visualization
                edges = [
                    [vertices[0], vertices[1], vertices[2], vertices[3], vertices[0]],  # Bottom edges
                    [vertices[4], vertices[5], vertices[6], vertices[7], vertices[4]],  # Top edges
                    [vertices[0], vertices[4]],  # Side edges
                    [vertices[1], vertices[5]],
                    [vertices[2], vertices[6]],
                    [vertices[3], vertices[7]]
                ]

                for edge in edges:
                    ax.plot3D(*zip(*edge), color='black')

            plt.title('Pallet #{0}'.format(packed.idx))
            plt.savefig('figure_pallet_{0}.png'.format(packed.idx))

            plt.show()
