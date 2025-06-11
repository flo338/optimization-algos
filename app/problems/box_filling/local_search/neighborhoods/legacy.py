import numpy as np
from scipy.signal import convolve2d


def place_permutation(permutation: np.ndarray, box_size: int) -> np.ndarray:
    """
    Convolve boxes with rectangle.
    0 results indicicate free space.
    """
    total_width = np.sum(permutation[:, 1])
    needed_boxes = int(np.ceil(total_width/box_size))
    boxes = np.zeros((needed_boxes, box_size, box_size))

    for i in range(permutation.shape[0]):
        rectangle_area = permutation[i,0]*permutation[i,1]
        rectangle = np.ones((int(permutation[i, 0]), int(permutation[i, 1])))
        box_ix = 0

        while box_ix < needed_boxes:
            if np.count_nonzero(boxes[box_ix] == 0) < rectangle_area:
                box_ix+=1
                continue
            convolution = convolve2d(boxes[box_ix], rectangle)
            ys, xs = np.where(convolution==0)
            if len(ys) == 0:
                box_ix+=1
                continue
            boxes[box_ix, int(ys[0]): int(ys[0]) + int(permutation[i, 0]), int(xs[0]): int(xs[0]) + int(permutation[i, 1])] = permutation[i,2]
            break
    
    return boxes