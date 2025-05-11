# Overview
This is a basic regex implementation using a finite state machine for checking a string.

## Supported opperations:
- ascii symbols (`a`, `b`, `c` etc.)
- `.` symbol (any symbol)
- `+` operator (placed after a regular symbol to notate that there should be 1 or more instances of that symbol)
- `*` operator (placed after a regular symbol to notate that there should be 0 or more instances of that symbol)

All other operations are currently not implemented and will not work or will be treated as a regular ascii symbol.

## Examples:
```
regex_pattern = "a*4.+hi"
regex_compiled = RegexFSM(regex_pattern)
print(regex_compiled.check_string("aaaaaa4uhi")) # returns True
print(regex_compiled.check_string("4uhi")) # returns True
print(regex_compiled.check_string("meow")) # returns False
```

```
regex_pattern = "a*aa"
regex_compiled = RegexFSM(regex_pattern)
print(regex_compiled.check_string("a")) # returns False
print(regex_compiled.check_string("aa")) # returns True
print(regex_compiled.check_string("a" * 100000)) # returns True
```

# Implementation explanation
First thing to note is that in all the state classes I changed the `next_states` variable from a class variable to an instance variable. Before that, for example, all instances of the AsciiState class would share the same `next_states` which would be hard to work around. With the current implementation, after parsing the regex, all states will have one member in the `next_states` list at index 0, which is the next state in the order, and the StarState and PlusState class instances will also have a second state being the class itself, which is used for looping a state.

## `State`
Basic state class from which all other classes are inheritted.

## `StartState`
Starting state from which we begin the fsm. Doesn't do anything.

## `TerminationState`
Final state which is used for handling the end of regex. Always returns False in the `check_self` method.

## `DotState`
State that accepts all characters. Always returns True in the `check_self` method.

## `AsciiState`
State the handles individual characters like "a" or "4". Only returns True in the `check_self` method if the passed in symbol is exactly the same as the one the state was initialized with.

## `StarState`
State for handling a "*" symbol in regex, which allows 0 or more occurances of the previous symbol so a regex of `"a*"` would allow both an empty string and `"a" * 10000`. During initialization sets an instance variable `checking_state` to remember what state was before it and appends itself to `next_states` which is used for accumulting the state.

## `PlusState`
State for handling a "+" symbol in regex, which allows 1 or more occurances of the previous symbol so a regex of `"a+"` would not allow an empty string but would allow `"a" * 10000`. The class itself is the exact same as the StarState class, as the different handling of the StarState where `"a*"` allows an empty string is handled in the `check_string` method of `RegexFSM` instead of the class itself.

## `RegexFSM`
### `__init__`
Constructs the actual finite state machine for the regular expression. Firstly checks wether the passed in regular expression is empty in which case it simply adds a `TerminationState()` to the `curr_state` and immediately exits. Otherwise starts enumerating through the regular expression and executes the `__init_next_state` method on each one to create a State. Once the state is created checks wether the next character in the regex is either a star or plus, in which case the appropriate state is created with the result of the `__init_next_state` method and sets the variable `skip` to True which skips the next iteration where the star or plus symbol would be. In any case, after the next state is created, the method adds it to the `next_states` list of the previous state at index 0, to properly handle the star and plus states, and updates the previous state to be the current one.

### `__init_next_state`
Makes a match case on the passed in `next_token`, if the character is a dot, creates a `DotState()` and if the character is an ascii character, creates an `AsciiState()` with that character. Additionally if the `next_token` is a plus or star character checks wether the last state was a `StarState`, `PlusState` or a `StartState`, in which case raises a value error notifying the user they entered an incorrect regex. The match case also has a default case which catches any unexpected characters and raises an error if reached.

### `check_string`
Does the actual checking of the string using the previously built regex state machine. This implementation uses the bfs algorithm to properly traverse the states. First it initializes a state queue with a tuple `(self.curr_state, 0)`, then while the `states_queue` has any elements gets the first element from the queue and unpacks it into `curr_state` and `start` variables. Then checks wether this start variable is equal to the length of the string, in which case checks wether either the curr_state or one of its next states contain a TermintaionState, in which case immediately returns True, otherwise just skips this itteration. If the start variable is less than the length. Sets `next_state` to `curr_next.next_states[0]`, then checks if it's a StarState and if true adds the state to the queue at the current `start` index, otherwise checks if the character at the `start` index of string is accepted by the `next_state`, and if it does adds it to the queue with the `start` variable at the next index of the string. Then checks wether the `curr_state` has two states in the `next_states` list which means it's either a PlusState or a StarState, then appends the second element in it with the next string index to the queue. Once the `states_queue` queue is empty and the method has not already been exited by a TerminationState return False, as none of the paths in the regex state machine correctly handled the passed in string.

My first attempt at writing this `check_string` used a linear approach where it would keep going to the next state, unless the state is a `StarState` or a `PlusState` where it would repeatedly `check_self` until it returned False and only then proceed to the next state. So a regex string of `"a*a"` would have returned False for a string `"aaa"` as going through linearly would iterate through all 3 `a`'s in the `a*` and not satisfy the `a` ascii state after it. So the only way I found was to use some kind of search algorithm (in this case bfs) to traverse multiple paths of the finite state machine. The bfs either continues checking the path by adding the next state with start + 1 to the queue when the `curr_state` is not a `StarState` and stops when its `check_string` is incorrect. For a `StarState` it splits the path to one where `StarState` will keep looping and moving along the string and one where the `StarState` stops its loop iteration and continues with the next states.
