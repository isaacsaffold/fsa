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
    def _possibly_parenthesized(regex, op):
        if op < regex._loosest_binding:
            return '(' + regex._string + ')'
        else:
            return regex._string

    def __init__(self, symbol):
        self._string = symbol
        self._loosest_binding = _Operation.NO_OP

    def star(self):
        if self._string == __class__.EMPTY_LANGUAGE:
            self._string = __class__.EMPTY_STRING
        elif self._string != __class__.EMPTY_STRING:
            s = __class__._possibly_parenthesized(self, _Operation.STAR)
            self._string = s + '*'
            self._loosest_binding = _Operation.STAR
        return self

    def concat(self, other):
        if other._string == __class__.EMPTY_LANGUAGE:
            self._string = __class__.EMPTY_LANGUAGE
            self._loosest_binding = _Operation.NO_OP
        elif self._string == __class__.EMPTY_STRING:
            self._string = other._string
            self._loosest_binding = other._loosest_binding
        elif (self._string != __class__.EMPTY_LANGUAGE and
              other._string != __class__.EMPTY_STRING):
            a = __class__._possibly_parenthesized(self, _Operation.CONCAT)
            b = __class__._possibly_parenthesized(other, _Operation.CONCAT)
            self._string = a + b
            self._loosest_binding = _Operation.CONCAT
        return self
        
    def union(self, other):
        if self._string == __class__.EMPTY_LANGUAGE:
            self._string = other._string
            self._loosest_binding = other._loosest_binding
        elif other._string != __class__.EMPTY_LANGUAGE:
            a = __class__._possibly_parenthesized(self, _Operation.UNION)
            b = __class__._possibly_parenthesized(other, _Operation.UNION)
            self._string = a + '|' + b
            self._loosest_binding = _Operation.UNION
        return self

    def __repr__(self):
        return self._string

class DFA:
    """A deterministic finite automaton. Given a string as input,
    determines whether the string belongs to the language corresponding
    to the DFA.

    constructor arguments
    ---------------------
    `states` - a nonempty iterable of states, each of which can be of
    arbitary hashable type.

    `alphabet` - an iterable containing the symbols of the alphabet over
    which the DFA's language is defined. Each symbol must be a single
    character.

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

    @staticmethod
    def _remove_unreachables(auto):
        #simply traverses the state graph
        reachable = set()
        queue = deque([auto._initial])
        while queue:
            orig = queue.pop()
            reachable.add(orig)
            for dest in auto._trans_matrix[orig]:
                if dest not in reachable:
                    queue.append(dest)
        auto._update_states(reachable)

    @staticmethod
    def _to_regex(auto, indices_to_syms):
        start, accept = len(auto._trans_matrix), len(auto._trans_matrix) + 1
        reverse_edges = [set() for i in range(accept)]
        reverse_edges[0].add(start)
        reverse_edges.append(auto._accepting)
        gnfa_func = []
        for i in range(len(auto._trans_matrix)):
            to_dict = {}
            for j in range(len(auto._trans_matrix[i])):
                to = auto._trans_matrix[i][j]
                regex = to_dict.setdefault(to, _BasicRegex.empty_language())
                regex.union(_BasicRegex(auto._indices_to_syms[j]))
            if i in auto._accepting:
                to_dict[accept] = _BasicRegex.empty_string()
            gnfa_func.append(to_dict)
        gnfa_func.extend([{auto._initial: _BasicRegex.empty_string()}, {}])
        for i in range(len(auto._trans_matrix)):
            # TODO
            pass

    def __init__(self, states, alphabet, transitions, initial, accepting,
                 optimize=True):
        """Initialize self. See help(type(self)) for accurate signature."""
        # Iterables may be lazily evaluated, hence unusual idioms for
        # initializing locals below.
        state_indices = dict(zip(states, count()))
        alphabet = tuple(alphabet)
        sym_indices = dict(zip(alphabet, count()))
        trans_matrix = [[0] * len(alphabet) for i in range(len(state_indices))]
        for orig, sym, dest in transitions:
            i, j = state_indices[orig], sym_indices[sym]
            trans_matrix[i][j] = state_indices[dest]

        # only stored as convenience to user
        self._alphabet = frozenset(alphabet)
        self._syms_to_indices = sym_indices
        # Transitions are stored in a matrix, with one row per state and
        # one column per symbol in the alphabet.
        self._trans_matrix = trans_matrix
        self._initial = state_indices[initial]
        self._accepting = set(state_indices[q] for q in accepting)

        if optimize:
            __class__._remove_unreachables(self)
        self._regex = __class__._to_regex(self, alphabet)

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
                state = self._trans_matrix[state][self._syms_to_indices[sym]]
        except KeyError:
            msg = f"'{sym}' is not contained in this DFA's alphabet."
            raise ValueError(msg) from None
        return state in self._accepting

    def __repr__(self):
        """Return repr(self)."""
        return self._regex
