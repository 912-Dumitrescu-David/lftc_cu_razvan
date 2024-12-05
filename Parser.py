# FILE: Parser.py

from Grammar import Grammar
from prettytable import PrettyTable


class LR0Item:
    def __init__(self, lhs: str, rhs: list, dot_position: int) -> None:
        self.lhs = lhs
        self.rhs = rhs
        self.dot_position = dot_position

    def __eq__(self, other: 'LR0Item') -> bool:
        return (self.lhs == other.lhs and
                self.rhs == other.rhs and
                self.dot_position == other.dot_position)

    def __hash__(self) -> int:
        return hash((self.lhs, tuple(self.rhs), self.dot_position))

    def __repr__(self) -> str:
        return f"{self.lhs} -> {' '.join(self.rhs[:self.dot_position] + ['.'] + self.rhs[self.dot_position:])}"


class LR0State:
    def __init__(self, items: set) -> None:
        self.items = set(items)

    def __eq__(self, other: 'LR0State') -> bool:
        if not isinstance(other, LR0State):
            return False
        return self.items == other.items

    def __hash__(self) -> int:
        return hash(frozenset(self.items))

    def __repr__(self) -> str:
        return f"State({self.items})"


class LR0Parser:
    def __init__(self, grammar):
        self.grammar = grammar
        self.states = []
        self.transitions = {}
        self.build_automaton()
        self.build_parsing_table()

    def goto(self, items, symbol):
        new_items = set()
        for item in items:
            if item.dot_position < len(item.rhs) and item.rhs[item.dot_position] == symbol:
                new_items.add(LR0Item(item.lhs, item.rhs, item.dot_position + 1))
        return self.closure(new_items)

    def closure(self, items):
        closure_set = set(items)
        added = True

        while added:
            added = False
            new_items = set(closure_set)
            for item in closure_set:
                if item.dot_position < len(item.rhs):
                    next_symbol = item.rhs[item.dot_position]
                    if next_symbol in self.grammar.N:
                        for production in self.grammar.P[next_symbol]:
                            new_item = LR0Item(next_symbol, production, 0)
                            if new_item not in closure_set:
                                new_items.add(new_item)
                                added = True
            closure_set = new_items

        return closure_set

    def canonical_collection(self):
        start_item = LR0Item("S'", [self.grammar.S], 0)
        start_state = LR0State(self.closure({start_item}))
        self.states = [start_state]
        self.transitions = {}
        queue = [start_state]
        while queue:
            current_state = queue.pop(0)
            for symbol in self.grammar.N | self.grammar.E:
                next_items = self.goto(current_state.items, symbol)
                if next_items:
                    next_state = LR0State(self.closure(next_items))
                    if next_state not in self.states:
                        self.states.append(next_state)
                        queue.append(next_state)
                    self.transitions[(current_state, symbol)] = next_state

    def build_automaton(self):
        self.canonical_collection()

    def build_parsing_table(self):
        self.action_table = {}
        self.goto_table = {}

        for state in self.states:
            self.action_table[state] = {}
            self.goto_table[state] = {}

            for item in state.items:
                if item.dot_position == len(item.rhs):
                    if item.lhs == "S'" and item.rhs == [self.grammar.S]:
                        self.action_table[state]['$'] = 'accept'
                    else:
                        for terminal in self.grammar.E | {'$'}:
                            self.action_table[state][terminal] = f'reduce {item.lhs} -> {" ".join(item.rhs)}'
                else:
                    next_symbol = item.rhs[item.dot_position]
                    if next_symbol in self.grammar.E:
                        next_state = self.transitions.get((state, next_symbol))
                        if next_state:
                            self.action_table[state][next_symbol] = f'shift {self.states.index(next_state)}'
                    elif next_symbol in self.grammar.N:
                        next_state = self.transitions.get((state, next_symbol))
                        if next_state:
                            self.goto_table[state][next_symbol] = self.states.index(next_state)
    
    def parse(self, input_string):
        input_string += '$'
        stack = [0]
        index = 0

        while True:
            state = self.states[stack[-1]]
            symbol = input_string[index]
            action = self.action_table[state].get(symbol)

            print(state)
            print(action)
            print(stack)
            print()
            if action is None:
                return False

            if action.startswith('shift'):
                next_state = int(action.split()[1])
                stack.append(next_state)
                index += 1
            elif action.startswith('reduce'):
                lhs, rhs = action.split('reduce ')[1].split(' -> ')
                rhs_length = len(rhs.split())
                for _ in range(rhs_length):
                    stack.pop()
                state = self.states[stack[-1]]
                stack.append(self.goto_table[state][lhs])
            elif action == 'accept':
                return True

    def parse(self, input_string):
        input_string += '$'
        stack = [0]
        index = 0

        while True:
            state = self.states[stack[-1]]
            symbol = input_string[index]
            action = self.action_table[state].get(symbol)

            print(state)
            print(action)
            print(stack)
            print()
            if action is None:
                return False

            if action.startswith('shift'):
                next_state = int(action.split()[1])
                stack.append(next_state)
                index += 1
            elif action.startswith('reduce'):
                lhs, rhs = action.split('reduce ')[1].split(' -> ')
                rhs_length = len(rhs.split())
                for _ in range(rhs_length):
                    stack.pop()
                state = self.states[stack[-1]]
                stack.append(self.goto_table[state][lhs])
            elif action == 'accept':
                return True


# Assuming Grammar and LR0Parser classes are defined and imported

# Define the grammar
grammar = Grammar.from_file('g1.txt')
# Initialize the parser
parser = LR0Parser(grammar)

# Build the automaton
parser.build_automaton()

# Print the automaton
for i, state in enumerate(parser.states):
    print(f"State {i}:")
    for item in state.items:
        print(f"  {item}")
    print()

# Build the parsing table
parser.build_parsing_table()


# Print the parsing table
# Print the parsing table
action_table = PrettyTable()
goto_table = PrettyTable()

# Define the headers for the tables
action_table.field_names = ["State"] + list(parser.grammar.E) + ['$']
goto_table.field_names = ["State"] + list(parser.grammar.N)

# Populate the action table
for i, state in enumerate(parser.states):
    row = [i]
    for terminal in parser.grammar.E | {'$'}:
        row.append(parser.action_table[state].get(terminal, ''))
    action_table.add_row(row)

# Populate the goto table
for i, state in enumerate(parser.states):
    row = [i]
    for nonterminal in parser.grammar.N:
        row.append(parser.goto_table[state].get(nonterminal, ''))
    goto_table.add_row(row)

print("ACTION TABLE")
print(action_table)
print("\nGOTO TABLE")
print(goto_table)

# Parse an input string
input_string = 'ac'

#expected output: Input string is accepted.
if parser.parse(input_string):
    print("Input string is accepted.")
else:
    print("Input string is rejected.")

# # Print the parsing table
# for state in parser.states:
#     print(state)
#     print("  ACTION:")
#     for terminal, action in parser.action_table[state].items():
#         print(f"    {terminal} -> {action}")
#     print("  GOTO:")
#     for nonterminal, goto in parser.goto_table[state].items():
#         print(f"    {nonterminal} -> {goto}")

# # Parse an input string
# input_string = 'acab'

# #expected output: Input string is accepted.
# if parser.parse(input_string):
#     print("Input string is accepted.")
# else:
#     print("Input string is rejected.")

