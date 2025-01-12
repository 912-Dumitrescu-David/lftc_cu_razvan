from Grammar import Grammar
from prettytable import PrettyTable


class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

    def __repr__(self, level=0):
        ret = "\t" * level + repr(self.value) + "\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        return ret


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
                            if terminal not in self.action_table[state]:
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

    def check_conflicts(self):
        conflicts = []
        for state, actions in self.action_table.items():
            for symbol, action in actions.items():
                if isinstance(action, list) and len(action) > 1:
                    conflicts.append((state, symbol, action))
        return conflicts

    def parse(self, input_string):
        input_string += '$'
        stack = [0]
        index = 0
        parse_tree_stack = []

        while True:
            state = self.states[stack[-1]]
            symbol = input_string[index]
            action = self.action_table[state].get(symbol)

            if action is None:
                return False, None

            if action.startswith('shift'):
                next_state = int(action.split()[1])
                stack.append(next_state)
                parse_tree_stack.append(TreeNode(symbol))
                index += 1
            elif action.startswith('reduce'):
                lhs, rhs = action.split('reduce ')[1].split(' -> ')
                rhs_length = len(rhs.split())
                new_node = TreeNode(lhs)

                for _ in range(rhs_length):
                    stack.pop()
                    if parse_tree_stack:
                        new_node.children.insert(0, parse_tree_stack.pop())

                state = self.states[stack[-1]]
                stack.append(self.goto_table[state][lhs])
                parse_tree_stack.append(new_node)
            elif action == 'accept':
                return True, parse_tree_stack[-1]

    def export_parsing_table(self):
        action_table = PrettyTable()
        goto_table = PrettyTable()

        action_table.field_names = ["State"] + list(self.grammar.E) + ['$']
        goto_table.field_names = ["State"] + list(self.grammar.N)

        for i, state in enumerate(self.states):
            action_row = [i]
            goto_row = [i]

            for terminal in self.grammar.E | {'$'}:
                action_row.append(self.action_table[state].get(terminal, ''))
            for nonterminal in self.grammar.N:
                goto_row.append(self.goto_table[state].get(nonterminal, ''))

            action_table.add_row(action_row)
            goto_table.add_row(goto_row)

        return action_table, goto_table

    def export_parsing_tree_table(self, tree_root):
        table = PrettyTable()
        table.field_names = ["Index", "Value", "Parent", "Right Sibling"]

        def traverse(node, parent_index, sibling_index):
            nonlocal index_counter
            current_index = index_counter
            index_counter += 1

            sibling_value = sibling_index if sibling_index is not None else "None"
            table.add_row([current_index, node.value, parent_index, sibling_value])

            for i, child in enumerate(node.children):
                traverse(child, current_index, index_counter if i + 1 < len(node.children) else None)

        index_counter = 0
        traverse(tree_root, "None", "None")
        return table


# Example usage
grammar = Grammar.from_file('g1.txt')

parser = LR0Parser(grammar)

parser.build_automaton()

parser.build_parsing_table()

conflicts = parser.check_conflicts()
if conflicts:
    print("Conflicts found in the parsing table:")
    for conflict in conflicts:
        print(conflict)
else:
    print("No conflicts found in the parsing table.")


with open("seq.txt",'r', encoding='utf-8') as file:
    input_string = file.readline()

with open("out1.txt",'w', encoding ='utf-8') as file:
    accepted, parse_tree = parser.parse(input_string)
    action_table, goto_table = parser.export_parsing_table()

    file.write("Parsing Table - Action:")
    file.write("\n")
    file.write(str(action_table))
    file.write("\n\n")
    file.write("Parsing Table - Goto:")
    file.write("\n")
    file.write(str(goto_table))
    file.write("\n\n")

    if accepted:
        file.write("Input string is accepted.\n")
        file.write("Parsing Tree Table:\n")
        tree_table = parser.export_parsing_tree_table(parse_tree)
        file.write(str(tree_table))
        print("Input string is accepted.")
        print("Parsing Tree Table:")
        print(tree_table)
    else:
        file.write("Input string is rejected.\n")
        print("Input string is rejected.")


# Introduce a manual incorrect action table for testing conflicts
parser.action_table = {
    parser.states[0]: {
        'a': ['shift 1', 'reduce S -> a'],  # Conflict: Shift and Reduce
        '$': 'accept'
    },
    parser.states[1]: {
        'b': 'shift 2'
    },
    parser.states[2]: {
        '$': 'reduce S -> a b'
    }
}

conflicts = parser.check_conflicts()

if conflicts:
    print("Conflicts found in the parsing table:")
    for conflict in conflicts:
        print(conflict)
else:
    print("No conflicts found in the parsing table.")
    
