from __future__ import annotations
from action import PaintAction
from grid import Grid
from data_structures.queue_adt import CircularQueue

class ReplayTracker:
    def __init__(self):
        self.action_queue = CircularQueue(11000)  # Class variable to store actions to be replayed, O(1) operation as it is a fixed capacity
    def start_replay(self) -> None:
        """
        Called whenever we should stop taking actions, and start playing them back.

        Useful if you have any setup to do before `play_next_action` should be called.

        No setup is required for this implementation.

        Complexity: O(1)
        """
        pass


    def add_action(self, action: PaintAction, is_undo: bool=False) -> None:
        """
        Adds an action to the replay.

        `is_undo` specifies whether the action was an undo action or not.
        Special, Redo, and Draw all have this is False.

        Worst and best case complexity: O(1)
        """
        if not self.action_queue.is_full():
            self.action_queue.append((action, is_undo))  # Adds the action and is undo as a tuple into the queue

    def play_next_action(self, grid: Grid) -> bool:
        """
        Plays the next replay action on the grid.
        Returns a boolean.
            - If there were no more actions to play, and so nothing happened, return True.
            - Otherwise, return False.

        Worst and best case complexity: O(n), where n is the number of steps needed to be processed in this action
        """
        try:
            action, is_undo = self.action_queue.serve()  # Obtain next action to be processed

            # Check if the current action to be played is an undo action
            if is_undo:
                action.undo_apply(grid)  # Undo action
            else:
                action.redo_apply(grid)  # Otherwise, perform the action using redo_apply

            return False

        except:
            # Exception is caused when queue is empty, i.e. when no more actions are to be played
            return True

    def clear(self) -> None:
        """
        Helper method used to clear the action_queue.

        Worst and best case complexity: O(1)
        """
        self.action_queue.clear()  # Clears queue using CircularQueue method


if __name__ == "__main__":
    action1 = PaintAction([], is_special=True)
    action2 = PaintAction([])

    g = Grid(Grid.DRAW_STYLE_SET, 5, 5)

    r = ReplayTracker()
    # add all actions
    r.add_action(action1)
    r.add_action(action2)
    r.add_action(action2, is_undo=True)
    # Start the replay.
    r.start_replay()
    f1 = r.play_next_action(g) # action 1, special
    f2 = r.play_next_action(g) # action 2, draw
    f3 = r.play_next_action(g) # action 2, undo
    t = r.play_next_action(g)  # True, nothing to do.
    assert (f1, f2, f3, t) == (False, False, False, True)

