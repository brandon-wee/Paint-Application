from __future__ import annotations
from abc import ABC, abstractmethod
from layer_util import Layer, get_layers
from layers import *
from data_structures.queue_adt import CircularQueue
from data_structures.stack_adt import ArrayStack
from data_structures.bset import BSet
from data_structures.array_sorted_list import ArraySortedList
from data_structures.sorted_list_adt import ListItem


class LayerStore(ABC):

    def __init__(self) -> None:
        pass

    @abstractmethod
    def add(self, layer: Layer) -> bool:
        """
        Add a layer to the store.
        Returns true if the LayerStore was actually changed.
        """
        pass

    @abstractmethod
    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        """
        Returns the colour this square should show, given the current layers.
        """
        pass

    @abstractmethod
    def erase(self, layer: Layer) -> bool:
        """
        Complete the erase action with this layer
        Returns true if the LayerStore was actually changed.
        """
        pass

    @abstractmethod
    def special(self):
        """
        Special mode. Different for each store implementation.
        """
        pass


class SetLayerStore(LayerStore):
    """
    Set layer store. A single layer can be stored at a time (or nothing at all)
    - add: Set the single layer.
    - erase: Remove the single layer. Ignore what is currently selected.
    - special: Invert the colour output.
    """

    def __init__(self):
        """
        Constructor for SetLayerStore. Initializes the instance variables to be used to store the layer used for this grid square
        and for the toggle for special mode.

        Complexity: O(1)
        """
        self.layer = None
        self.on_special = False

    def add(self, layer: Layer) -> bool:
        """
        Replaces old layer with a new layer. Returns True if a change was made and False otherwise.

        Complexity: O(1)
        """
        flag = layer != self.layer  # Compares the new layer and previous layer to see if they are the same
        self.layer = layer  # Replace old layer with new layer
        return flag  # Returns boolean flag representing if the layer changed

    def get_color(self, start: tuple[int, int], timestamp: int, x: int, y: int) -> tuple[int, int, int]:
        """
        Takes in the starting colour of the square and returns the new colour of the square
        depending if there exist a layer to apply and if the special toggle is on.

        Complexity: O(1)
        """
        colour = start  # Initial starting colour

        if self.layer is not None:  # If there exist a layer to be applied
            colour = self.layer.apply(start, timestamp, x, y)  # Apply layer

        if self.on_special:  # If the special toggle is on
            colour = invert.apply(colour, timestamp, x, y)  # Apply special effect (invert colour)

        return colour  # Return final colour

    def erase(self, layer: Layer) -> bool:
        """
        Erases current layer. Returns True if a change was made and False otherwise.

        Complexity: O(1)
        """
        if self.layer is None:
            return False  # Return False since layer is there was no layer to erase

        self.layer = None  # Removes layer
        return True  # Returns True as layer was removed

    def special(self) -> None:
        """
        Toggles between True and False to represent if the special mode is ON or OFF

        Complexity: O(1)
        """
        self.on_special = not self.on_special  # Toggles between True and False


class AdditiveLayerStore(LayerStore):
    """
    Additive layer store. Each added layer applies after all previous ones.
    - add: Add a new layer to be added last.
    - erase: Remove the first layer that was added. Ignore what is currently selected.
    - special: Reverse the order of current layers (first becomes last, etc.)
    """

    def __init__(self):
        """
        Constructor for AdditiveLayerStore class. Used to declare the CircularQueue to be used to store the layers added.

        Complexity: O(n), where n is the number of layers in the get_layers() array
        """
        self.layers = CircularQueue(len(get_layers()) * 100)  # Declare queue of length 'number of layers' * 100

    def add(self, layer: Layer) -> bool:
        """
        Add a new layer to be added last. Returns True if layer was successfully added, False otherwise.

        Complexity: O(1)
        """
        if self.layers.is_full():
            return False  # Returns False if queue is full

        self.layers.append(layer)  # Queue is not full, add layer to queue
        return True  # Returns True to specify that layer was successfully added

    def get_color(self, start: tuple[int, int], timestamp: int, x: int, y: int) -> tuple[int, int, int]:
        """
        Takes in starting colour and applied all the layers added into the queue in the order of the queue and returns
        the final colour.

        Complexity: O(n), where n is the number of layers in the get_layers() array
        """
        colour = start  # Initially the colour is start

        for i in range(len(self.layers)):  # For every layer in the queue
            current_layer = self.layers.serve()  # Remove oldest element in queue
            self.layers.append(current_layer)  # Append it back into the queue so that the order is preserved
            colour = current_layer.apply(colour, timestamp, x, y)  # Apply current layer

        return colour  # Returns final colour

    def erase(self, layer: Layer) -> bool:
        """
        Removes the oldest layer in the queue. Returns True if a layer was removed, False otherwise.

        Complexity: O(1)
        """
        try:
            self.layers.serve()  # Attempt to remove oldest layer in the queue
            return True  # Returns True if removal was successful

        except:
            return False  # If queue was empty, serve() would cause an exception which would be caught here, returns False

    def special(self):
        """
        Reverses queue when this method is invoked.

        Complexity: O(n), where n is the number of layers stored in self.layers
        """
        aux_stack = ArrayStack(len(self.layers))  # Creates a stack to be used as a helper data structure
        while not self.layers.is_empty():
            aux_stack.push(self.layers.serve())  # Push all the elements from queue into the stack
            # All elements would be pushed into the stack following the order of the queue

        while not aux_stack.is_empty():
            self.layers.append(aux_stack.pop())  # Pop all elements from queue and append into stack
            # All elements from the stack would be popped from the opposite order from it was pushed into.
            # Hence, it will append in reverse order.


class SequenceLayerStore(LayerStore):
    """
    Sequential layer store. Each layer type is either applied / not applied, and is applied in order of index.
    - add: Ensure this layer type is applied.
    - erase: Ensure this layer type is not applied.
    - special:
        Of all currently applied layers, remove the one with median `name`.
        In the event of two layers being the median names, pick the lexicographically smaller one.
    """

    def __init__(self):
        """
        Constructor for SequenceLayerStore class. Used to declare the BSet to be used to store the layers added.

        Complexity: O(1)
        """
        self.layers = BSet()  # Declares set to store layers

    def add(self, layer: Layer) -> bool:
        """
        Adds layer into the set. Returns True if layer was successfully added, False if layer already exists.

        Complexity: O(1)
        """
        index = layer.index + 1  # Compute index of the layer
        flag = index not in self.layers  # Checks if layer already exists in set
        self.layers.add(index)  # Adds layer to the set
        return flag  # Returns true or false depending if layer already exists in set

    def get_color(self, start: tuple[int, int], timestamp: int, x: int, y: int) -> tuple[int, int, int]:
        """
        Takes in starting colour and applied all the layers in the order of the index in get_layers() that is added to the set.

        Complexity: O(n), where n is the number of layers in get_layers()
        """
        colour = start  # Initial colour
        for index in range(1, len(get_layers()) + 1):  # For every possible layer index
            try:
                assert index in self.layers  # Check if index exist in the set
                colour = get_layers()[index - 1].apply(colour, timestamp, x, y)  # Applies layer if it does indeed exist

            except:
                continue  # Index does not exist in set

        return colour  # Returns final colour

    def erase(self, layer: Layer) -> bool:
        """
        Removes layer from the set. Returns True if layer was successfully removed, False if layer is already not in set.

        Complexity: O(1)
        """
        try:
            index = layer.index + 1  # Compute layer index
            self.layers.remove(index)  # Attempts to remove index
            return True  # Returns True if removal was successful

        except:
            return False  # Otherwise, return False

    def special(self):
        """
        Removes the lexicographically median layer from the set.

        Complexity analysis:
        Let n be the number of layers in get_layers().

        Creating the sorted_layer_names ArrayStoredList will take O(n) time.
        The loop will loop through n times.
        The .add method worst case takes O(n) to insert an element into the list.
        Other operations takes O(1) time.

        Hence, the time complexity is O(n^2).
        """
        sorted_layer_names = ArraySortedList(len(get_layers()))  # Initialize the ArraySortedList used to store the index and the name of each layer
        for index in range(1, len(get_layers()) + 1):  # For every potential layer
            if index in self.layers:
                sorted_layer_names.add(ListItem(index, get_layers()[index - 1].name))


        if len(sorted_layer_names) > 0:  # If the ArraySortedList is not empty
            self.layers.remove(sorted_layer_names[(len(sorted_layer_names) - 1) // 2].value)  # Then remove the median element from the set
