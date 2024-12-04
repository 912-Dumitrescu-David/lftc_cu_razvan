# FILE: Parser.py

from Grammar import Grammar

class LR0Item:
    def __init__(self, lhs : str, rhs : list, dot_position : int) -> None:
        self.lhs = lhs
        self.rhs = rhs
        self.dot_position = dot_position

    def __eq__(self, other : 'LR0Item') -> bool:
        return (self.lhs == other.lhs and
                self.rhs == other.rhs and
                self.dot_position == other.dot_position)

    def __hash__(self) -> int:
        return hash((self.lhs, tuple(self.rhs), self.dot_position))

    def __repr__(self) -> str:
        return f"{self.lhs} -> {' '.join(self.rhs[:self.dot_position] + ['.'] + self.rhs[self.dot_position:])}"

class LR0State:
    def __init__(self, items : set) -> None:
        self.items = set(items)

    def __eq__(self, other : 'LR0State') -> bool:
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

    def first(self, symbols):
        first_set = set()
        if not symbols:
            return first_set
        if symbols[0] in self.grammar.E:
            first_set.add(symbols[0])
            return first_set
        for production in self.grammar.P[symbols[0]]:
            if production == ['']:
                first_set.add('')
            else:
                for symbol in production:
                    symbol_first = self.first([symbol])
                    first_set |= symbol_first - {''}
                    if '' not in symbol_first:
                        break
                else:
                    first_set.add('')
        return first_set

    def get_follow_set(self, nonterminal):
        follow_set = set()
        if nonterminal == self.grammar.S:
            follow_set.add('$')
        for lhs, productions in self.grammar.P.items():
            for production in productions:
                for index, symbol in enumerate(production):
                    if symbol == nonterminal:
                        if index + 1 < len(production):
                            follow_set |= self.first(production[index + 1:])
                        if index + 1 == len(production) or '' in self.first(production[index + 1:]):
                            follow_set |= self.get_follow_set(lhs)
        return follow_set

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

# Assuming Grammar and LR0Parser classes are defined and imported

# Define the grammar
productions = {
    'S': [['a', 'S', 'b', 'S'], ['a', 'S'], ['c']]
}
grammar = Grammar(N={'S', 'A'}, E={'a', 'b', 'c'}, S='S', P=productions)

# Initialize the parser
parser = LR0Parser(grammar)

# Build the automaton
parser.build_automaton()

# Build the parsing table
parser.build_parsing_table()

# Print the parsing table
for state in parser.states:
    print(state)
    print("  ACTION:")
    for terminal, action in parser.action_table[state].items():
        print(f"    {terminal} -> {action}")
    print("  GOTO:")
    for nonterminal, goto in parser.goto_table[state].items():
        print(f"    {nonterminal} -> {goto}")