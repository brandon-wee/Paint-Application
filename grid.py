from __future__ import annotations

from data_structures.referential_array import ArrayR
from layer_store import *

class Grid:
    DRAW_STYLE_SET = "SET"
    DRAW_STYLE_ADD = "ADD"
    DRAW_STYLE_SEQUENCE = "SEQUENCE"
    DRAW_STYLE_OPTIONS = (
        DRAW_STYLE_SET,
        DRAW_STYLE_ADD,
        DRAW_STYLE_SEQUENCE
    )

    DEFAULT_BRUSH_SIZE = 2
    MAX_BRUSH = 5
    MIN_BRUSH = 0

    def __init__(self, draw_style, x, y) -> None:
        """
        Initialise the grid object.
        - draw_style:
            The style with which colours will be drawn.
            Should be one of DRAW_STYLE_OPTIONS
            This draw style determines the LayerStore used on each grid square.
        - x, y: The dimensions of the grid.

        Should also intialise the brush size to the DEFAULT provided as a class variable.

        Worst and best case complexity: O(xy), where x, y are dimensions of the grid
        """
        self.draw_style = draw_style  # Draw style used for the grid

        # The dimensions of the grid
        self.x = x
        self.y = y
        self.brush_size = Grid.DEFAULT_BRUSH_SIZE  # Set brush size as default brush size
        self.grid = ArrayR(x)  # 2D array to represent the grid

        # Fill up None values in self.grid with Array of LayerStores
        for i in range(x):
            self.grid[i] = ArrayR(y)  # Set each None value to an Array of length y
            for j in range(y):

                # Set each value of the self.grid[i] array to their specific layer store
                if self.draw_style == Grid.DRAW_STYLE_SET:
                    self.grid[i][j] = SetLayerStore()
                elif self.draw_style == Grid.DRAW_STYLE_ADD:
                    self.grid[i][j] = AdditiveLayerStore()
                else:
                    self.grid[i][j] = SequenceLayerStore()


    def increase_brush_size(self):
        """
        Increases the size of the brush by 1,
        if the brush size is already MAX_BRUSH,
        then do nothing.

        Worst and best case complexity: O(1)
        """
        self.brush_size = min(self.brush_size + 1, Grid.MAX_BRUSH)  # Increment brush size and cap it at Grid.MAX_BRUSH

    def decrease_brush_size(self):
        """
        Decreases the size of the brush by 1,
        if the brush size is already MIN_BRUSH,
        then do nothing.

        Worst and best case complexity: O(1)
        """
        self.brush_size = max(self.brush_size - 1, Grid.MIN_BRUSH)  # Decrement brush size and make sure it is at least Grid.MIN_BRUSH

    def special(self):
        """Called when the special action is requested.

        Complexity analysis:
        Let x and y be the dimensions of the grid. Lets consider three possible cases for the LayerStore.

        SetLayerStore:
        The complexity of the special method in SetLayerStore is O(1) as it just toggles a boolean value between True and False.
        Hence, the worst and best case complexity for special when the draw_style is SetLayerStore is O(xy).

        AdditiveLayerStore:
        Let n be the average number of layers stored in self.layers.
        For each square, activating the special method costs O(n) time.
        Hence, the worst and best case complexity for special when the draw_style is AdditiveLayerStore is O(xyn).

        SequenceLayerStore:
        Let n be the number of layers in get_layers().
        For each square, the worst case complexity for activating the special method is O(n^2).
        Hence, the worst and best case complexity for special when the draw_style is SequenceLayerStore is O(xyn^2).
        """
        for i in range(self.x):
            for j in range(self.y):
                self.grid[i][j].special()  # Activate the special effect on all of the grids in the self.grid array

    def __getitem__(self, index):
        """
        Special method to allow instances of the grid object to be accessed using [] notation.

        Worst and best case complexity: O(1)
        """
        return self.grid[index]  # Returns the row of self.grid at index
