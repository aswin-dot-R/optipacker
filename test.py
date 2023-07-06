from itertools import permutations
import collections
import copy

from palletier.topology import Topology

Layer = collections.namedtuple('Layer', ['width', 'value'])
Coords = collections.namedtuple('Coords', ['x', 'y', 'z'])
Dims = collections.namedtuple('Dims', ['dim1', 'dim2', 'dim3'])
class Box:
    def __init__(self, width, height, depth):
        self.width = width
        self.height = height
        self.depth = depth
        self.is_packed = False

    def __repr__(self):
        return f"Box({self.width}, {self.height}, {self.depth})"

class Pallet:
    def __init__(self, width, height, depth):
        self.width = width
        self.height = height
        self.depth = depth

    @property
    def dims(self):
        return [self.width, self.height, self.depth]

    def __repr__(self):
        return f"Pallet({self.width}, {self.height}, {self.depth})"

class Layer:
    def __init__(self, width):
        self.width = width
        self.height = 0
        self.depth = 0

    def __repr__(self):
        return f"Layer({self.width}, {self.height}, {self.depth})"

class Coords:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Coords({self.x}, {self.y}, {self.z})"

class Packer:
    def __init__(self, boxes, pallet):
        self.boxes = boxes
        self.pallet = pallet
        self.used_coords = []
        self.packed_boxes = []
        self.best_num_packed = 0
        self.best_vol = 0
        self.best_boxes = []
        self.best_pallet = None

    # Rest of the code...

    def reset_boxes(self):
        for box in self.boxes:
            box.is_packed = False
        self.packed_boxes = []
        self.used_coords = []
        self.packed_vol = 0

    @staticmethod
    def get_candidate_layers(boxes, pallet_orientation):
        candidate_layers = []
        for box in boxes:
            # We only want (dim1, dim2, dim3), (dim2, dim1, dim3) and (dim3, dim1, dim2)
            for orientation in list(permutations(box.dims))[::2]:
                ex_dim, dim2, dim3 = orientation
                if (ex_dim > pallet_orientation[1] or
                        ((dim2 > pallet_orientation[0] or
                          dim3 > pallet_orientation[2]) and
                         (dim2 > pallet_orientation[2] or
                          dim3 > pallet_orientation[0]))):
                    continue
                if ex_dim in [layer.width for layer in candidate_layers]:
                    continue
                layer_value = sum(min(abs(ex_dim - dim)
                                      for dim in box2.dims)
                                  for box2 in boxes if box2 is not box)
                layer = Layer(width=ex_dim, value=layer_value)
                candidate_layers.append(layer)
        return candidate_layers

    def get_box(self, max_len_x, gap_len_y, max_len_y, gap_len_z, max_len_z):
        all_dims = {dim for box in self.boxes for dim in box.dims
                    if not box.is_packed}
        max_dims = (max_len_x, max_len_y, max_len_z)
        # 3 booleans that represent if any of the max_dims are too small for any box to fit
        too_little_dims = [all(max_dim < dim for dim in all_dims) for max_dim in max_dims]
        # If any dim is too small, no boxes can fit at all.
        if any(too_little_dims):
            return (None, None), (None, None)
        min_y_diff = min_x_diff = min_z_diff = 99999
        other_y_diff = other_x_diff = other_z_diff = 99999
        # Best box in the best orientation
        best_match = (None, None)
        other_best_match = (None, None)
        checked = []
        for idx, box in enumerate(self.boxes):
            if box.is_packed:
                continue
            for orientation in list(permutations(box.dims)):
                dim1, dim2, dim3 = orientation
                # We skip the box if it is too big for the layer
                if ((dim1 > max_len_x or dim2 > max_len_y or
                     dim3 > max_len_z) or
                        (dim1 < max_len_x and dim2 < max_len_y and
                         dim3 < max_len_z and
                         self.layer_in_layer)):
                    continue
                if dim1 == max_len_x:
                    diff = abs(max_len_y - dim2)
                    if diff < min_y_diff:
                        min_y_diff = diff
                        best_match = idx, orientation
                if dim1 == max_len_y:
                    diff = abs(max_len_x - dim2)
                    if diff < min_x_diff:
                        min_x_diff = diff
                        best_match = idx, orientation
                if dim3 == max_len_z:
                    diff = abs(max_len_y - dim2)
                    if diff < min_y_diff:
                        min_y_diff = diff
                        best_match = idx, orientation
                if dim3 == max_len_y:
                    diff = abs(max_len_x - dim2)
                    if diff < min_x_diff:
                        min_x_diff = diff
                        best_match = idx, orientation
                if dim2 == max_len_x:
                    diff = abs(max_len_y - dim1)
                    if diff < min_y_diff:
                        min_y_diff = diff
                        best_match = idx, orientation
                if dim2 == max_len_y:
                    diff = abs(max_len_x - dim1)
                    if diff < min_x_diff:
                        min_x_diff = diff
                        best_match = idx, orientation
                if dim3 == max_len_x:
                    diff = abs(max_len_y - dim1)
                    if diff < min_y_diff:
                        min_y_diff = diff
                        best_match = idx, orientation
                if dim3 == max_len_y:
                    diff = abs(max_len_x - dim1)
                    if diff < min_x_diff:
                        min_x_diff = diff
                        best_match = idx, orientation
                if dim1 == max_len_z:
                    diff = abs(max_len_y - dim2)
                    if diff < min_y_diff:
                        min_y_diff = diff
                        best_match = idx, orientation
                if dim2 == max_len_z:
                    diff = abs(max_len_x - dim1)
                    if diff < min_x_diff:
                        min_x_diff = diff
                        best_match = idx, orientation
                if dim1 == max_len_z:
                    diff = abs(max_len_y - dim2)
                    if diff < min_y_diff:
                        min_y_diff = diff
                        best_match = idx, orientation
                if dim2 == max_len_z:
                    diff = abs(max_len_x - dim1)
                    if diff < min_x_diff:
                        min_x_diff = diff
                        best_match = idx, orientation

                if (dim1 == max_len_x or dim2 == max_len_x or
                        dim3 == max_len_x or dim1 == max_len_z or
                        dim2 == max_len_z or dim3 == max_len_z):
                    continue
                if (dim1 >= max_len_y or dim2 >= max_len_y or
                        dim3 >= max_len_y):
                    continue
                if (dim1 > gap_len_y or dim2 > gap_len_x or
                        dim3 > gap_len_z):
                    continue
                if (dim1 > gap_len_x or dim2 > gap_len_y or
                        dim3 > gap_len_z):
                    continue
                if (dim1 > gap_len_z or dim2 > gap_len_y or
                        dim3 > gap_len_x):
                    continue
                if (dim1 > gap_len_y or dim2 > gap_len_z or
                        dim3 > gap_len_x):
                    continue
                if (dim1 > gap_len_z or dim2 > gap_len_x or
                        dim3 > gap_len_y):
                    continue
                diff = abs(max_len_x - dim1)
                if diff < min_x_diff:
                    min_x_diff = diff
                    best_match = idx, orientation
                diff = abs(max_len_y - dim1)
                if diff < min_y_diff:
                    min_y_diff = diff
                    best_match = idx, orientation
                diff = abs(max_len_x - dim2)
                if diff < min_x_diff:
                    min_x_diff = diff
                    best_match = idx, orientation
                diff = abs(max_len_y - dim2)
                if diff < min_y_diff:
                    min_y_diff = diff
                    best_match = idx, orientation
                diff = abs(max_len_x - dim3)
                if diff < min_x_diff:
                    min_x_diff = diff
                    best_match = idx, orientation
                diff = abs(max_len_y - dim3)
                if diff < min_y_diff:
                    min_y_diff = diff
                    best_match = idx, orientation
                checked.append((idx, orientation))
        if best_match == (None, None):
            for idx, box in checked:
                orientation = box
                dim1, dim2, dim3 = orientation
                if (dim1 >= max_len_y or dim2 >= max_len_y or
                        dim3 >= max_len_y):
                    continue
                if (dim1 > gap_len_y or dim2 > gap_len_x or
                        dim3 > gap_len_z):
                    continue
                if (dim1 > gap_len_x or dim2 > gap_len_y or
                        dim3 > gap_len_z):
                    continue
                if (dim1 > gap_len_z or dim2 > gap_len_y or
                        dim3 > gap_len_x):
                    continue
                if (dim1 > gap_len_y or dim2 > gap_len_z or
                        dim3 > gap_len_x):
                    continue
                if (dim1 > gap_len_z or dim2 > gap_len_x or
                        dim3 > gap_len_y):
                    continue
                if dim1 == max_len_x:
                    diff = abs(max_len_y - dim2)
                    if diff < other_y_diff:
                        other_y_diff = diff
                        other_best_match = idx, orientation
                if dim1 == max_len_y:
                    diff = abs(max_len_x - dim2)
                    if diff < other_x_diff:
                        other_x_diff = diff
                        other_best_match = idx, orientation
                if dim3 == max_len_z:
                    diff = abs(max_len_y - dim2)
                    if diff < other_y_diff:
                        other_y_diff = diff
                        other_best_match = idx, orientation
                if dim3 == max_len_y:
                    diff = abs(max_len_x - dim2)
                    if diff < other_x_diff:
                        other_x_diff = diff
                        other_best_match = idx, orientation
                if dim2 == max_len_x:
                    diff = abs(max_len_y - dim1)
                    if diff < other_y_diff:
                        other_y_diff = diff
                        other_best_match = idx, orientation
                if dim2 == max_len_y:
                    diff = abs(max_len_x - dim1)
                    if diff < other_x_diff:
                        other_x_diff = diff
                        other_best_match = idx, orientation
                if dim3 == max_len_x:
                    diff = abs(max_len_y - dim1)
                    if diff < other_y_diff:
                        other_y_diff = diff
                        other_best_match = idx, orientation
                if dim3 == max_len_y:
                    diff = abs(max_len_x - dim1)
                    if diff < other_x_diff:
                        other_x_diff = diff
                        other_best_match = idx, orientation
                if dim1 == max_len_z:
                    diff = abs(max_len_y - dim2)
                    if diff < other_y_diff:
                        other_y_diff = diff
                        other_best_match = idx, orientation
                if dim2 == max_len_z:
                    diff = abs(max_len_x - dim1)
                    if diff < other_x_diff:
                        other_x_diff = diff
                        other_best_match = idx, orientation
                if dim1 == max_len_z:
                    diff = abs(max_len_y - dim2)
                    if diff < other_y_diff:
                        other_y_diff = diff
                        other_best_match = idx, orientation
                if dim2 == max_len_z:
                    diff = abs(max_len_x - dim1)
                    if diff < other_x_diff:
                        other_x_diff = diff
                        other_best_match = idx, orientation

                if (dim1 == max_len_x or dim2 == max_len_x or
                        dim3 == max_len_x or dim1 == max_len_z or
                        dim2 == max_len_z or dim3 == max_len_z):
                    continue
                if (dim1 >= max_len_y or dim2 >= max_len_y or
                        dim3 >= max_len_y):
                    continue
                if (dim1 > gap_len_y or dim2 > gap_len_x or
                        dim3 > gap_len_z):
                    continue
                if (dim1 > gap_len_x or dim2 > gap_len_y or
                        dim3 > gap_len_z):
                    continue
                if (dim1 > gap_len_z or dim2 > gap_len_y or
                        dim3 > gap_len_x):
                    continue
                if (dim1 > gap_len_y or dim2 > gap_len_z or
                        dim3 > gap_len_x):
                    continue
                if (dim1 > gap_len_z or dim2 > gap_len_x or
                        dim3 > gap_len_y):
                    continue
                diff = abs(max_len_x - dim1)
                if diff < other_x_diff:
                    other_x_diff = diff
                    other_best_match = idx, orientation
                diff = abs(max_len_y - dim1)
                if diff < other_y_diff:
                    other_y_diff = diff
                    other_best_match = idx, orientation
                diff = abs(max_len_x - dim2)
                if diff < other_x_diff:
                    other_x_diff = diff
                    other_best_match = idx, orientation
                diff = abs(max_len_y - dim2)
                if diff < other_y_diff:
                    other_y_diff = diff
                    other_best_match = idx, orientation
                diff = abs(max_len_x - dim3)
                if diff < other_x_diff:
                    other_x_diff = diff
                    other_best_match = idx, orientation
                diff = abs(max_len_y - dim3)
                if diff < other_y_diff:
                    other_y_diff = diff
                    other_best_match = idx, orientation
        return best_match, other_best_match

    def find_layer(self, boxes, pallet, prev_layer):
        self.layer_in_layer = False
        self.layer_finished = False
        self.packed_y = prev_layer.y
        layer_thickness = prev_layer.z - prev_layer.y
        while not self.layer_finished:
            for box in boxes:
                box.is_packed = False
            layer_thickness += pallet.min_height
            if layer_thickness > pallet.max_height:
                return prev_layer
            self.packed_y = prev_layer.y
            boxes = sorted(boxes, key=lambda b: b.dims[2],
                           reverse=True)
            layer = self.get_layer(boxes, pallet.dims[0])
            if layer.width == 0:
                continue
            layer.x, layer.y = self.get_smallest_y(layer.width, boxes)
            self.used_coords = []
            if layer.y == -1:
                return prev_layer
            self.packed_y = max(layer.y, self.packed_y)
            while self.packing:
                self.packing = False
                self.find_box(layer, boxes, pallet)
            self.packed_vol += layer.width * pallet.dims[0] * (
                    layer.z - prev_layer.y)
            if self.packed_vol >= self.best_vol:
                self.best_num_packed = self.num_packed
                self.best_vol = self.packed_vol
                self.best_boxes = copy.deepcopy(self.packed_boxes)
                self.best_pallet = pallet
            self.packing = True
            self.layer_finished = True
            for box in boxes:
                if not box.is_packed:
                    self.layer_finished = False
                    break
        return Coords(prev_layer.x, prev_layer.y, self.packed_y), \
               Coords(prev_layer.x + pallet.dims[0], prev_layer.y,
                      self.packed_y + layer_thickness)

    def find_box(self, layer, boxes, pallet):
        """Find box to pack."""
        best_volume = 0
        best_box_fit = 0
        best_box = None
        best_orientation = None
        max_len_y = layer.width
        if len(self.used_coords) > 1:
            len_diffs = [self.used_coords[i + 1].x - coord.x
                         for i, coord in enumerate(self.used_coords[:-1])]
            max_len_y = min(len_diffs) if len(len_diffs) > 0 else layer.width
        len_y = max_len_y
        len_x = pallet.dims[0]
        len_z = layer.z - self.packed_y
        if len_y == 0:
            return
        box = self.get_box(len_x, len_y, max_len_y, len_z, pallet.dims[2])
        while box[0] is not None:
            box_id, orientation = box
            if orientation[1] == len_x and orientation[0] == len_y:
                volume = len_x * len_y * len_z
            else:
                volume = len_x * len_y * len_z
            if volume > best_volume:
                best_volume = volume
                best_box_fit = box_id
                best_box = self.boxes[box_id]
                best_orientation = orientation
            box = self.get_box(len_x, len_y, max_len_y, len_z,
                               pallet.dims[2])
        if best_box is not None:
            best_box.is_packed = True
            self.used_coords.append(Coords(layer.x, self.packed_y,
                                           layer.z))
            self.num_packed += 1
            self.packed_boxes.append(best_box)
            self.packed_y += best_orientation[0]
            len_x = best_orientation[1]
            self.packing = True

    def get_box(self, len_x, len_y, max_len_y, len_z, max_len_z):
        """Get box that fits x, y, z dimensions."""
        min_y_diff = max_len_y
        min_z_diff = max_len_z
        best_match = (None, None)
        other_y_diff = max_len_y
        other_z_diff = max_len_z
        other_best_match = (None, None)
        checked = []
        for idx, box in enumerate(self.boxes):
            if box.is_packed:
                continue
            for orientation in list(permutations(box.dims)):
                dim1, dim2, dim3 = orientation
                # We skip the box if it is too big for the layer
                if ((dim1 > max_len_y or dim2 > max_len_y or
                     dim3 > max_len_y) or
                        (dim1 > len_y or dim2 > len_y or
                         dim3 > len_y)):
                    continue
                if dim1 == len_y:
                    diff = abs(max_len_z - dim2)
                    if diff < min_z_diff:
                        min_z_diff = diff
                        best_match = idx, orientation
                if dim1 == max_len_z:
                    diff = abs(len_y - dim2)
                    if diff < other_y_diff:
                        other_y_diff = diff
                        other_best_match = idx, orientation
                if dim3 == max_len_y:
                    diff = abs(len_y - dim2)
                    if diff < other_y_diff:
                        other_y_diff = diff
                        other_best_match = idx, orientation
                if dim2 == len_y:
                    diff = abs(max_len_z - dim1)
                    if diff < min_z_diff:
                        min_z_diff = diff
                        best_match = idx, orientation
                if dim2 == max_len_z:
                    diff = abs(len_y - dim1)
                    if diff < other_y_diff:
                        other_y_diff = diff
                        other_best_match = idx, orientation
                if dim1 == max_len_y:
                    diff = abs(len_y - dim2)
                    if diff < other_y_diff:
                        other_y_diff = diff
                        other_best_match = idx, orientation
                if dim2 == max_len_y:
                    diff = abs(len_y - dim1)
                    if diff < other_y_diff:
                        other_y_diff = diff
                        other_best_match = idx, orientation
                if dim1 == len_y:
                    diff = abs(max_len_z - dim2)
                    if diff < min_z_diff:
                        min_z_diff = diff
                        best_match = idx, orientation
                if dim2 == len_y:
                    diff = abs(max_len_z - dim1)
                    if diff < min_z_diff:
                        min_z_diff = diff
                        best_match = idx, orientation
                if dim3 == len_y:
                    diff = abs(max_len_z - dim1)
                    if diff < min_z_diff:
                        min_z_diff = diff
                        best_match = idx, orientation
                if dim3 == max_len_z:
                    diff = abs(len_y - dim2)
                    if diff < other_y_diff:
                        other_y_diff = diff
                        other_best_match = idx, orientation
                if dim1 == len_y:
                    diff = abs(max_len_z - dim2)
                    if diff < min_z_diff:
                        min_z_diff = diff
                        best_match = idx, orientation
                if dim2 == len_y:
                    diff = abs(max_len_z - dim1)
                    if diff < min_z_diff:
                        min_z_diff = diff
                        best_match = idx, orientation
                if dim3 == len_y:
                    diff = abs(max_len_z - dim1)
                    if diff < min_z_diff:
                        min_z_diff = diff
                        best_match = idx, orientation
                if (dim1 > max_len_y or dim2 > max_len_y or
                        dim3 > max_len_y):
                    continue
                if (dim1 > len_y or dim2 > len_y or
                        dim3 > len_y):
                    continue
                if (dim1 > max_len_z or dim2 > max_len_z or
                        dim3 > max_len_z):
                    continue
                if (dim1 > len_z or dim2 > len_z or
                        dim3 > len_z):
                    continue
                if (dim1 > max_len_z or dim2 > len_z or
                        dim3 > len_y):
                    continue
                if (dim1 > len_y or dim2 > max_len_z or
                        dim3 > len_z):
                    continue
                if (dim1 > len_z or dim2 > len_y or
                        dim3 > max_len_z):
                    continue
                if (dim1 > len_y or dim2 > len_z or
                        dim3 > max_len_z):
                    continue
                if (dim1 > max_len_z or dim2 > len_y or
                        dim3 > len_z):
                    continue
                if (dim1 > len_z or dim2 > max_len_z or
                        dim3 > len_y):
                    continue
                if (dim1 > len_y or dim2 > max_len_z or
                        dim3 > len_z):
                    continue
                if (dim1 > len_z or dim2 > len_y or
                        dim3 > max_len_z):
                    continue
                if (dim1 > len_y or dim2 > len_z or
                        dim3 > len_y):
                    continue
                if (dim1 > max_len_z or dim2 > len_z or
                        dim3 > max_len_y):
                    continue
                if (dim1 > len_y or dim2 > max_len_y or
                        dim3 > len_z):
                    continue
                if (dim1 > len_z or dim2 > len_y or
                        dim3 > max_len_y):
                    continue
                if (dim1 > max_len_y or dim2 > len_z or
                        dim3 > len_y):
                    continue
                diff = abs(max_len_y - dim1)
                if diff < min_y_diff:
                    min_y_diff = diff
                    best_match = idx, orientation
                diff = abs(len_y - dim1)
                if diff < other_y_diff:
                    other_y_diff = diff
                    other_best_match = idx, orientation
                diff = abs(max_len_y - dim2)
                if diff < min_y_diff:
                    min_y_diff = diff
                    best_match = idx, orientation
                diff = abs(len_y - dim2)
                if diff < other_y_diff:
                    other_y_diff = diff
                    other_best_match = idx, orientation
                diff = abs(max_len_y - dim3)
                if diff < min_y_diff:
                    min_y_diff = diff
                    best_match = idx, orientation
                diff = abs(len_y - dim3)
                if diff < other_y_diff:
                    other_y_diff = diff
                    other_best_match = idx, orientation
                checked.append((idx, orientation))
        if best_match == (None, None):
            for idx, box in checked:
                orientation = box
                dim1, dim2, dim3 = orientation
                if (dim1 >= max_len_z or dim2 >= max_len_z or
                        dim3 >= max_len_z):
                    continue
                if (dim1 > len_z or dim2 > len_y or
                        dim3 > max_len_y):
                    continue
                if (dim1 > max_len_z or dim2 > len_y or
                        dim3 > len_z):
                    continue
                if (dim1 > len_y or dim2 > max_len_z or
                        dim3 > len_z):
                    continue
                if (dim1 > max_len_z or dim2 > len_z or
                        dim3 > len_y):
                    continue
                diff = abs(max_len_z - dim1)
                if diff < min_z_diff:
                    min_z_diff = diff
                    best_match = idx, orientation
                diff = abs(len_z - dim1)
                if diff < other_z_diff:
                    other_z_diff = diff
                    other_best_match = idx, orientation
                diff = abs(max_len_z - dim2)
                if diff < min_z_diff:
                    min_z_diff = diff
                    best_match = idx, orientation
                diff = abs(len_z - dim2)
                if diff < other_z_diff:
                    other_z_diff = diff
                    other_best_match = idx, orientation
                diff = abs(max_len_z - dim3)
                if diff < min_z_diff:
                    min_z_diff = diff
                    best_match = idx, orientation
                diff = abs(len_z - dim3)
                if diff < other_z_diff:
                    other_z_diff = diff
                    other_best_match = idx, orientation
        if best_match == (None, None):
            print("Skipped")
        else:
            print(best_match, other_best_match)

    def find_layer(self, boxes, pallet, prev_layer):
        self.layer_in_layer = False
        self.layer_finished = False
        self.packed_y = prev_layer.y
        layer_thickness = prev_layer.z - prev_layer.y
        while not self.layer_finished:
            for box in boxes:
                box.is_packed = False
            layer_thickness += pallet.min_height
            if layer_thickness > pallet.max_height:
                return prev_layer
            self.packed_y = prev_layer.y
            boxes = sorted(boxes, key=lambda b: b.dims[2],
                           reverse=True)
            layer = self.get_layer(boxes, pallet.dims[0])
            if layer.width == 0:
                continue
            layer.x, layer.y = self.get_smallest_y(layer.width, boxes)
            self.used_coords = []
            if layer.y == -1:
                return prev_layer
            self.packed_y = max(layer.y, self.packed_y)
            while self.packing:
                self.packing = False
                self.find_box(layer, boxes, pallet)
            self.packed_vol += layer.width * pallet.dims[0] * (
                    layer.z - prev_layer.y)
            if self.packed_vol >= self.best_vol:
                self.best_num_packed = self.num_packed
                self.best_vol = self.packed_vol
                self.best_boxes = copy.deepcopy(self.packed_boxes)
                self.best_pallet = pallet
            self.packing = True
            self.layer_finished = True
            for box in boxes:
                if not box.is_packed:
                    self.layer_finished = False
                    break
        return Coords(prev_layer.x, prev_layer.y, self.packed_y), \
               Coords(prev_layer.x + pallet.dims[0], prev_layer.y,
                      self.packed_y + layer_thickness)

    def find_box(self, layer, boxes, pallet):
        """Find box to pack."""
        best_volume = 0
        best_box_fit = 0
        best_box = None
        best_orientation = None
        max_len_y = layer.width
        if len(self.used_coords) > 1:
            len_diffs = [self.used_coords[i + 1].x - coord.x
                         for i, coord in enumerate(self.used_coords[:-1])]
            max_len_y = min(len_diffs) if len(len_diffs) > 0 else layer.width
        len_y = max_len_y
        len_x = pallet.dims[0]
        len_z = layer.z - self.packed_y
        if len_y == 0:
            return
        box = self.get_box(len_x, len_y, max_len_y, len_z, pallet.dims[2])
        while box[0] is not None:
            box_id, orientation = box
            if orientation[1] == len_x and orientation[0] == len_y:
                volume = len_x * len_y * len_z
            else:
                volume = len_x * len_y * len_z
            if volume > best_volume:
                best_volume = volume
                best_box_fit = box_id
                best_box = self.boxes[box_id]
                best_orientation = orientation
            box = self.get_box(len_x, len_y, max_len_y, len_z,
                               pallet.dims[2])
        if best_box is not None:
            best_box.is_packed = True
            self.used_coords.append(Coords(layer.x, self.packed_y,
                                           layer.z))
            self.num_packed += 1
            self.packed_boxes.append(best_box)
            self.packed_y += best_orientation[0]
            len_x = best_orientation[1]
            self.packing = True

    def get_box(self, len_x, len_y, max_len_y, len_z, max_len_z):
        """Get box that fits x, y, z dimensions."""
        min_y_diff = max_len_y
        min_z_diff = max_len_z
        best_match = (None, None)
        other_y_diff = max_len_y
        other_z_diff = max_len_z
        other_best_match = (None, None)
        checked = []
        for idx, box in enumerate(self.boxes):
            if box.is_packed:
                continue
            for orientation in list(permutations(box.dims)):
                dim1, dim2, dim3 = orientation
                if (dim1 >= max_len_y or dim2 >= max_len_y or
                        dim3 >= max_len_y):
                    continue
                if (dim1 > len_y or dim2 > len_y or
                        dim3 > len_y):
                    continue
                if (dim1 > max_len_z or dim2 > max_len_z or
                        dim3 > max_len_z):
                    continue
                if (dim1 > len_z or dim2 > len_z or
                        dim3 > len_z):
                    continue
                if (dim1 > max_len_z or dim2 > len_z or
                        dim3 > len_y):
                    continue
                if (dim1 > len_y or dim2 > max_len_z or
                        dim3 > len_z):
                    continue
                if (dim1 > len_z or dim2 > len_y or
                        dim3 > max_len_z):
                    continue
                if (dim1 > len_y or dim2 > len_z or
                        dim3 > max_len_z):
                    continue
                if (dim1 > max_len_z or dim2 > len_y or
                        dim3 > len_z):
                    continue
                if (dim1 > len_z or dim2 > max_len_z or
                        dim3 > len_y):
                    continue
                if (dim1 > len_y or dim2 > max_len_z or
                        dim3 > len_z):
                    continue
                if (dim1 > len_z or dim2 > len_y or
                        dim3 > max_len_z):
                    continue
                if (dim1 > len_y or dim2 > len_z or
                        dim3 > len_y):
                    continue
                if (dim1 > max_len_z or dim2 > len_z or
                        dim3 > max_len_y):
                    continue
                if (dim1 > len_y or dim2 > max_len_y or
                        dim3 > len_z):
                    continue
                if (dim1 > len_z or dim2 > len_y or
                        dim3 > max_len_y):
                    continue
                if (dim1 > max_len_y or dim2 > len_z or
                        dim3 > len_y):
                    continue
                diff = abs(max_len_y - dim1)
                if diff < min_y_diff:
                    min_y_diff = diff
                    best_match = idx, orientation
                diff = abs(len_y - dim1)
                if diff < other_y_diff:
                    other_y_diff = diff
                    other_best_match = idx, orientation
                diff = abs(max_len_y - dim2)
                if diff < min_y_diff:
                    min_y_diff = diff
                    best_match = idx, orientation
                diff = abs(len_y - dim2)
                if diff < other_y_diff:
                    other_y_diff = diff
                    other_best_match = idx, orientation
                diff = abs(max_len_y - dim3)
                if diff < min_y_diff:
                    min_y_diff = diff
                    best_match = idx, orientation
                diff = abs(len_y - dim3)
                if diff < other_y_diff:
                    other_y_diff = diff
                    other_best_match = idx, orientation
                checked.append((idx, orientation))
        if best_match == (None, None):
            for idx, box in checked:
                orientation = box
                dim1, dim2, dim3 = orientation
                if (dim1 >= max_len_z or dim2 >= max_len_z or
                        dim3 >= max_len_z):
                    continue
                if (dim1 > len_z or dim2 > len_y or
                        dim3 > max_len_y):
                    continue
                if (dim1 > max_len_z or dim2 > len_z or
                        dim3 > len_y):
                    continue
                if (dim1 > len_y or dim2 > max_len_z or
                        dim3 > len_z):
                    continue
                if (dim1 > max_len_z or dim2 > len_z or
                        dim3 > len_y):
                    continue
                diff = abs(max_len_z - dim1)
                if diff < min_z_diff:
                    min_z_diff = diff
                    best_match = idx, orientation
                diff = abs(len_z - dim1)
                if diff < other_z_diff:
                    other_z_diff = diff
                    other_best_match = idx, orientation
                diff = abs(max_len_z - dim2)
                if diff < min_z_diff:
                    min_z_diff = diff
                    best_match = idx, orientation
                diff = abs(len_z - dim2)
                if diff < other_z_diff:
                    other_z_diff = diff
                    other_best_match = idx, orientation
                diff = abs(max_len_z - dim3)
                if diff < min_z_diff:
                    min_z_diff = diff
                    best_match = idx, orientation
                diff = abs(len_z - dim3)
                if diff < other_z_diff:
                    other_z_diff = diff
                    other_best_match = idx, orientation
        if best_match == (None, None):
            print("Skipped")
        else:
            print(best_match, other_best_match)

    def get_smallest_y(self, width, boxes):
        """Get smallest y coordinate."""
        smallest_y = float('inf')
        coords = []
        for box in boxes:
            if box.is_packed:
                continue
            for orientation in list(permutations(box.dims)):
                dim1, dim2, _ = orientation
                if (dim1 <= width and dim2 <= width and
                        box.y < smallest_y):
                    smallest_y = box.y
                    coords = orientation
        return smallest_y, coords

    def get_layer(self, boxes, width):
        """Get layer."""
        layer = Layer(width)
        for box in boxes:
            if box.is_packed:
                continue
            for orientation in list(permutations(box.dims)):
                dim1, dim2, dim3 = orientation
                if (dim1 <= width and dim2 <= width and
                        dim3 <= width):
                    layer.width = width
                    layer.height = max(layer.height, box.y + dim1)
                    layer.depth = max(layer.depth, dim2)
                    break
        return layer

    def pack(self):
        """Pack algorithm."""
        self.used_coords = []
        self.packed_boxes = []
        for pallet in self.pallets:
            prev_layer = Coords(0, 0, 0)
            while True:
                prev_layer, coords = self.find_layer(self.boxes, pallet,
                                                     prev_layer)
                if coords.x == prev_layer.x and coords.y == prev_layer.y:
                    break
        return self.best_num_packed, self.best_vol, self.best_boxes,
        self.best_pallet

# Example usage
boxes = [
    Box(1, 1, 2),  # Box 0
    Box(2, 2, 2),  # Box 1
    Box(3, 3, 1),  # Box 2
]
pallets = [
    Pallet(4, 4, 4),  # Pallet 0
]

packer = Packer(boxes, pallets)
num_packed, volume, packed_boxes, pallet = packer.pack()
print("Number of packed boxes:", num_packed)
print("Volume occupied:", volume)
print("Packed boxes:", packed_boxes)
print("Pallet used:", pallet)
