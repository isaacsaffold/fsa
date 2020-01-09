## Requirements
- Python version 3.6 or above

## DFA File Format
The file containing the components of the DFA should consist of the following, in order:

1. a line containing the comma-separated names of the DFA's states
2. a line containing the comma-separated characters of the DFA's alphabet
3. the DFA's transitions, one per line. Each transition should be of the form *from-state, character, to-state*.
4. a line containing the name of the DFA's start state
5. a line containing the comma-separated names of the DFA's accepting states

In addition, note the following:

- The alphabet must consist entirely of single characters, and cannot contain '|', '{', '}', '(', ')', '\*', or ''' (excluding the surrounding quotes), or a malformed regex may result.
- Trailing whitespace is ignored, but all other whitespace is not.
- A DFA with no final states is permissible. In this case, the line containing final states may be omitted.

## Regex Syntax
(excluding surrounding quotes)
Union: '|'
Kleene star: '\*'
Empty string: ''''
Empty language: '{}'

## How to Run
To run the program, execute a command of this form in the shell:

	<python_exec> <path>/fsa <dfa_file>

`<python_exec>`, by default, is `python` on Windows and `python3` on \*nix.
Both `<path>` and `<dfa_file>` are relative to the working directory.

An equivalent regex will then be displayed. After this, the user may enter any number of strings, one per line. For each string entered, if it is accepted by the DFA, "accepted" is printed. Otherwise, "rejected" is printed. The program can be halted by entering an EOF character (CTRL-Z for Windows, CTRL-D for \*nix).

Note the following:
- Trailing whitespace is ignored, but all other whitespace is not.
- The empty string can be input by simply entering nothing.
