import numpy as np
from itertools import product
from scipy.interpolate import RegularGridInterpolator


class Chart(object):
    """
    class Chart
        Basic class for creating a 3D chart for mapping local indices into absolute coordinate.
    """

    def __init__(self, small_end: np.array, big_end: np.array, ngrid: np.array = (1, 1, 1)):
        self.small_end = small_end
        self.big_end = big_end
        # Additional "1" is due to the difference between sample points and grid points. (Tree-planting puzzle)
        component = lambda i: np.linspace(small_end[i], big_end[i], num=ngrid[i] + 1)
        self.grid = np.array([[[[x, y, z] for z in component(2)] for y in component(1)] for x in component(0)])

    def __getitem__(self, key):
        return self.grid[key]

    def __setitem__(self, key, value):
        self.grid[key] = value

    def __str__(self):
        return f"Chart(small_end: {self.small_end},big_end: {self.big_end},grid: {self.grid})"

    def __repr__(self):
        return self.__str__()

    def copy(self):
        return Chart(self.small_end, self.big_end, self.grid.shape)

    def refine(self, refine_factor: int):
        return Chart(self.small_end, self.big_end, np.array(self.grid.shape[:3]) * refine_factor)

    def decompose(self):
        nx, ny, nz = self.grid.shape[:3]
        return np.array([
            Chart(self.grid[i - 1][j - 1][k - 1], self.grid[i][j][k])
            for i, j, k in product(range(1, nx), range(1, ny), range(1, nz))
        ])


class Bundle(object):
    """
    class Bundle
        Basic class for creating a fibre bundle with a given base chart.
    """

    def __init__(self, chart: Chart, nComp: int, fibre: np.array = None):
        self.chart = chart
        self.nComp = nComp
        self.fibre = np.array(
            [[[np.zeros(nComp)
               for z in range(chart.grid.shape[2])]
              for y in range(chart.grid.shape[1])]
             for x in range(chart.grid.shape[0])]
        ) if fibre is None else fibre

    def __getitem__(self, key):
        return self.fibre[key]

    def __setitem__(self, key, value):
        self.fibre[key] = value

    def refine(self, refine_factor):
        component = lambda chart, i: np.linspace(chart.small_end[i], chart.big_end[i], num=chart.grid.shape[i])
        interpolators = [
            RegularGridInterpolator(
                (
                    component(self.chart, 0),
                    component(self.chart, 1),
                    component(self.chart, 2)), self.fibre[:, :, :, i]
            )
            for i in range(self.nComp)
        ]  # create an interpolator for each component
        new_chart = self.chart.refine(refine_factor)
        new_fibre = np.array(
            [[[[interp([new_chart[x][y][z]])[0] for interp in interpolators]
               for z in range(new_chart.grid.shape[2])]
              for y in range(new_chart.grid.shape[1])]
             for x in range(new_chart.grid.shape[0])]
        )   # TODO: Necessary to use MPI.
        return Bundle(new_chart, self.nComp, new_fibre)

    def decompose(self):
        return np.array([
            Bundle(
                Chart(self.chart.grid[i - 1][j - 1][k - 1], self.chart.grid[i][j][k]),
                self.nComp,
                self.fibre[i-1:i+1][j-1:j+1][k-1:k+1],
            )
            for i, j, k in product(
                range(1, self.chart.grid.shape[0]),
                range(1, self.chart.grid.shape[1]),
                range(1, self.chart.grid.shape[2])
            )
        ])


class TreeNode(object):
    def __init__(self, bundle: Bundle, level=0, max_level=4):
        if level > max_level:
            raise ValueError(f"TreeNode.level must be less than or equal to TreeNode.max_level. "
                             f"Given: level={level}, max_level={max_level}")
        self.level = level
        self.bundle = bundle
        self.child_nodes = []
        self.max_level = max_level

    def add_child(self, child_node: 'TreeNode'):
        self.child_nodes.append(child_node)

    def __lt__(self, child_node: 'TreeNode'):
        self.add_child(child_node)
        return child_node

    def add_children(self, child_nodes):
        self.child_nodes += child_nodes

    def __le__(self, child_nodes):
        self.add_child(child_nodes)
        return self

    def is_childless(self):
        return self.child_nodes == []

    def refine(self, refine_factor):
        if self.level < self.max_level and (
                not self.child_nodes or not sum([node.is_childless() for node in self.child_nodes])
        ):
            self.child_nodes = [TreeNode(bundle, self.level + 1, self.max_level)
                                for bundle in self.bundle.refine(refine_factor).decompose()]

