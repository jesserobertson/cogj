""" file:    boxes.py (rtree)
    author: Jess Robertson, jess@unearthed.solutions
    date:    Monday, 18 March 2019

    description: Random bounding box generation
"""

import math
from itertools import islice
from random import uniform, lognormvariate

from cogj.utilities import check_bounds

def range_box_stream(bounds=(-10, -10, 10, 10)):
    """
    Generate a stream of random bounding boxes where the corners
    are uniformly distributed

    Parameters:
        bounds - the bounds to generate in
    """
    xmin, ymin, xmax, ymax = check_bounds(bounds)
    while True:
        x_range = sorted(uniform(xmin, xmax) for _ in range(2))
        y_range = sorted(uniform(ymin, ymax) for _ in range(2))
        yield (x_range[0], y_range[0], x_range[1], y_range[1])

def size_box_stream(bounds=(-10, -10, 10, 10)):
    """
    Generate a stream of random bounding boxes where the corners
    are uniformly distributed

    Parameters:
        bounds - the bounds to generate in
    """
    # Check our bounds
    xmin, ymin, xmax, ymax = check_bounds(bounds)

    # Generate random size distribution from priors
    while True:
        xcentre, ycentre = uniform(xmin, xmax), uniform(ymin, ymax)
        width, height = [lognormvariate(-1, 1) for _ in range(2)]
        yield (
            xcentre - width / 2, ycentre - height / 2,
            xcentre + width / 2, ycentre + height / 2
        )

def generate_boxes(bounds=(-1, -1, 1, 1), method='size', size=math.inf):
    """
    Generate a stream of random bounding boxes

    Has two methods for generating random boxes:
        - *size* - generates a random central point (x0, y0)
            within the bounding box, and then draws widths and heights
            from a logN(0, 0.25) distribution.
        - *range* - generates random ranges in x and y by drawing
            points from the bounding box and ordering them.

    Parameters:
        bounds - the bounding box to generate boxes in
        method - the method to use to generate the boxes. One of
            'range' or 'size'
        size - the number of boxes to generate. If `size=math.inf`
            then return a

    Returns:
        a generator
    """
    methods = {
        'size': size_box_stream,
        'range': range_box_stream
    }
    if method not in methods.keys():
        raise ValueError(f'Unknown method {method}, allowed values are {methods.keys()}')

    # Make the thing to return
    _generator = methods[method](bounds)
    return _generator if math.isinf(size) else islice(_generator, size)
