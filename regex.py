"""
Regex FSM implementation.
"""

from __future__ import annotations
from abc import ABC, abstractmethod

class State(ABC):
    """
    Base state abstract class.
    """
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """

class StartState(State):
    """
    Starting state.
    """
    def __init__(self):
        self.next_states: list[State] = []

    def check_self(self, _):
        pass

class TerminationState(State):
    """
    State for terminating the FSM.
    """
    def __init__(self):
        pass

    def check_self(self, _):
        return False

class DotState(State):
    """
    state for . character (any character accepted)
    """
    def __init__(self):
        self.next_states: list[State] = []

    def check_self(self, _):
        return True

class AsciiState(State):
    """
    state for alphabet letters or numbers
    """
    def __init__(self, symbol: str) -> None:
        self.next_states: list[State] = []
        self.curr_sym = symbol

    def check_self(self, char: str) -> State | Exception:
        return char == self.curr_sym

class StarState(State):
    """
    State for handling 0 or more instances of the previous state.
    """
    def __init__(self, checking_state: State):
        self.next_states: list[State] = []
        self.checking_state = checking_state
        self.next_states.append(self)

    def check_self(self, char):
        return self.checking_state.check_self(char)

class PlusState(State):
    """
    State for handling 1 or more instances of the previous state.
    """
    def __init__(self, checking_state: State):
        self.next_states: list[State] = []
        self.checking_state = checking_state
        self.next_states.append(self)

    def check_self(self, char):
        return self.checking_state.check_self(char)

class RegexFSM:
    """
    Class for building a finite state machine from a regex and then using it to test a string.
    """

    def __init__(self, regex_expr: str) -> None:
        """
        Initializes the finite state machine based on the passed in regular expression.
        """
        self.curr_state: State = StartState()

        if not regex_expr:
            self.curr_state.next_states.append(TerminationState())
            return

        prev_state = self.curr_state
        tmp_next_state = self.curr_state

        skip = False

        for i, char in enumerate(regex_expr):
            if skip:
                skip = False
                continue

            tmp_next_state = self.__init_next_state(char, prev_state)

            if i + 1 < len(regex_expr):
                match regex_expr[i + 1]:
                    case "*":
                        tmp_next_state = StarState(tmp_next_state)
                        skip = True
                    case "+":
                        tmp_next_state = PlusState(tmp_next_state)
                        skip = True
                    case _:
                        pass


            prev_state.next_states.insert(0, tmp_next_state)
            prev_state = tmp_next_state

        prev_state.next_states.append(TerminationState())

    def __init_next_state(
            self, next_token: str, prev_state: State
        ) -> State:
        """
        Creates and returns the next state based on the given token.
        """
        match next_token:
            case ".":
                return DotState()
            case next_token if next_token in "*+":
                if isinstance(prev_state, (StarState, PlusState)):
                    raise ValueError("Two instances of either '+' or '*' or both may not be placed"
                                     " in a row other in a regex string.")
                if isinstance(prev_state, StartState):
                    raise ValueError("'+' or '*' may not be placed at the start of a regex string.")
            case next_token if next_token.isascii():
                return AsciiState(next_token)
            case _:
                raise AttributeError("Character is not supported")

    def check_string(self, string: str) -> bool:
        """
        Checks the passed in string using bfs to traverse the fsm built in the class init.
        """
        states_queue = [(self.curr_state, 0)]

        length = len(string)

        while states_queue:
            curr_state, start = states_queue.pop(0)

            if start == length:
                if any(isinstance(s,TerminationState) for s in [curr_state]+curr_state.next_states):
                    return True

                continue

            next_state = curr_state.next_states[0]

            if isinstance(next_state, StarState):
                states_queue.append((next_state, start))

            elif next_state.check_self(string[start]):
                states_queue.append((next_state, start + 1))

            if len(curr_state.next_states) == 2:
                states_queue.append((curr_state.next_states[1], start + 1))

        return False

if __name__ == "__main__":
    regex_pattern = "a*4.+hi"

    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))  # True
    print(regex_compiled.check_string("meow"))  # False
