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
    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar
        self.states = []
        self.transitions = {}
        # self.build_automaton()
        # self.build_parsing_table()

    def closure(self, items : set) -> set:
        closure = set(items)
        changed = True
        while changed:
            changed = False
            for item in list(closure):
                if item.dot_position < len(item.rhs):
                    next_symbol = item.rhs[item.dot_position]
                    if next_symbol in self.grammar.N:
                        for production in self.grammar.P[next_symbol]:
                            new_item = LR0Item(next_symbol, production, 0)
                            if new_item not in closure:
                                closure.add(new_item)
                                changed = True
        return closure
    
    def goto(self, items : set, symbol : str) -> set:
        new_items = set()
        for item in items:
            if item.dot_position < len(item.rhs) and item.rhs[item.dot_position] == symbol:
                new_items.add(LR0Item(item.lhs, item.rhs, item.dot_position + 1))
        return self.closure(new_items)
    
    def canonical_collection(self) -> None:
        start_item = LR0Item(self.grammar.S, self.grammar.P[self.grammar.S][0], 0)
        start_state = LR0State(self.closure({start_item}))
        self.states.append(start_state)
        queue = [start_state]
        while queue:
            current_state = queue.pop(0)
            for symbol in self.grammar.N | self.grammar.E:
                next_items = self.goto(current_state.items, symbol)
                if next_items:
                    next_state = LR0State(next_items)
                    if next_state not in self.states:
                        self.states.append(next_state)
                        queue.append(next_state)
                        self.transitions[(current_state, symbol)] = next_state
                    
#test closure and goto
g = Grammar.from_file("g1.txt")
parser = LR0Parser(g)
item = LR0Item("S", ["E"], 0)
closure = parser.closure({item})
print(closure)
print(parser.goto(closure, "E"))
print(parser.goto(closure, "T"))
print(parser.goto(closure, "F"))

#test canonical collection
parser.canonical_collection()
for state in parser.states:
    print(state)
    for symbol in g.N | g.E:
        if (state, symbol) in parser.transitions:
            print(f"  {symbol} -> {parser.transitions[(state, symbol)]}")


