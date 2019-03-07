"""Contains a DFA implementation."""

from itertools import count
from collections import deque
from enum import IntEnum

class _Operation(IntEnum):
    """Regex operations ordered by precedence, from highest to lowest."""
    NO_OP = 0
    STAR = 1
    CONCAT = 2
    UNION = 3

class _BasicRegex:

    EMPTY_LANGUAGE = '{}'
    EMPTY_STRING = "''"

    @classmethod
    def empty_language(cls):
        return cls(cls.EMPTY_LANGUAGE)

    @classmethod
    def empty_string(cls):
        return cls(cls.EMPTY_STRING)

    @staticmethod
    def possibly_parenthesized(regex, op):
        if op < regex.loosest_binding:
            return '(' + regex.string + ')'
        else:
            return regex.string

    def __init__(self, symbol):
        self.string = symbol
        self.loosest_binding = _Operation.NO_OP

    def star(self):
        if self.string == __class__.EMPTY_LANGUAGE:
            self.string = __class__.EMPTY_STRING
        elif self.string != __class__.EMPTY_STRING:
            s = __class__.possibly_parenthesized(self, _Operation.STAR)
            self.string = s + '*'
            self.loosest_binding = _Operation.STAR
        return self

    def concat(self, other):
        if other.string == __class__.EMPTY_LANGUAGE:
            self.string = __class__.EMPTY_LANGUAGE
            self.loosest_binding = _Operation.NO_OP
        elif self.string == __class__.EMPTY_STRING:
            self.string = other.string
            self.loosest_binding = other.loosest_binding
        elif (self.string != __class__.EMPTY_LANGUAGE and
              other.string != __class__.EMPTY_STRING):
            a = __class__.possibly_parenthesized(self, _Operation.CONCAT)
            b = __class__.possibly_parenthesized(other, _Operation.CONCAT)
            self.string = a + b
            self.loosest_binding = _Operation.CONCAT
        return self
        
    def union(self, other):
        if self.string == __class__.EMPTY_LANGUAGE:
            self.string = other.string
            self.loosest_binding = other.loosest_binding
        elif other.string != __class__.EMPTY_LANGUAGE:
            a = __class__.possibly_parenthesized(self, _Operation.UNION)
            b = __class__.possibly_parenthesized(other, _Operation.UNION)
            self.string = a + '|' + b
            self.loosest_binding = _Operation.UNION
        return self

    def __repr__(self):
        return self.string

class DFA:
    """A deterministic finite automaton. Given a string as input,
    determines whether the string belongs to the language corresponding
    to the DFA.

    constructor arguments
    ---------------------
    `states` - an iterable of states, each of which can be of arbitrary
    hashable type.

    `alphabet` - an iterable containing the symbols of the alphabet over
    which the DFA's language is defined. Each symbol must be of string
    type.

    In the common case that every symbol in the alphabet can be
    represented by a single character, a string containing each of these
    characters can be passed to `alphabet`.

    `transitions` - an iterable of iterables, each of the form
    (current_state, current_symbol, next_state). current_state and
    next_state must be elements of `states`, and current_symbol must be
    an element of `alphabet`.

    For each state s in `states` and each symbol c in `alphabet`, there
    must be a transition (s, c, t) in `transitions`, where t is also in
    `states`.

    `initial` - starting state (must be in `states`)

    `accepting` - iterable of states (all of which are in `states`) such
    that a string is accepted iff the final state reached by the DFA when
    evaluating said string is in the iterable

    `optimize` - if `True`, removes all unreachable states
    """

    def __init__(self, states, alphabet, transitions, initial, accepting,
                 optimize=True):
        """Initialize self. See help(type(self)) for accurate signature."""
        # Iterables may be lazily evaluated, hence unusual idioms for
        # initializing locals below.
        state_indices = dict(zip(states, count()))
        alphabet = tuple(sorted(alphabet))
        sym_indices = dict(zip(alphabet, count()))
        trans_matrix = [[0] * len(alphabet) for i in range(len(state_indices))]
        for orig, sym, dest in transitions:
            i, j = state_indices[orig], sym_indices[sym]
            trans_matrix[i][j] = state_indices[dest]

        # only stored as convenience to user
        self._alphabet = alphabet
        # maps symbols in alphabet to integers
        self._sym_indices = sym_indices
        # Transitions are stored in a matrix, with one row per state and
        # one column per symbol in the alphabet.
        self._trans_matrix = trans_matrix
        self._initial = state_indices[initial]
        self._accepting = set(state_indices[q] for q in accepting)

        if optimize:
            self._remove_unreachables()

    def _update_states(self, new_states):
        """Reconfigures the DFA when its set of states is altered."""
        new_matrix = []
        new_accepting = set()
        for i in new_states:
            if i == self._initial:
                self._initial = len(new_matrix)
            if i in self._accepting:
                new_accepting.add(len(new_matrix))
            new_matrix.append(self._trans_matrix[i])
        self._trans_matrix = new_matrix
        self._accepting = new_accepting
                
    def _remove_unreachables(self):
        # simply traverses the state graph
        reachable = set()
        queue = deque([self._initial])
        while queue:
            orig = queue.pop()
            reachable.add(orig)
            for dest in self._trans_matrix[orig]:
                if dest not in reachable:
                    queue.append(dest)
        self._update_states(reachable)

    def _to_regex(self):
        pass

    @property
    def alphabet(self):
        return self._alphabet

    def __call__(self, s):
        """Returns `True` if `s` is a member of this DFA's language,
        `False` otherwise. `s` must be an iterable that consists
        entirely of symbols in this DFA's alphabet."""
        state = self._initial
        try:
            for sym in s:
                state = self._trans_matrix[state][self._sym_indices[sym]]
        except KeyError:
            msg = f"'{sym}' is not contained in this DFA's alphabet."
            raise ValueError(msg) from None
        return state in self._accepting

    def __repr__(self):
        """Return repr(self)."""
        self._regex = getattr(self, "_regex", self._to_regex())
        return self._regex
