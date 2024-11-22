class Grammar:
    def __init__(self, N, E, S, P):
        self.N = N
        self.E = E
        self.S = S
        self.P = P

    def from_file(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            N = set(Grammar.parse_line(file.readline()))
            E = set(Grammar.parse_line(file.readline()))
            S = file.readline().split('=')[1].replace(" ", "").strip()
            file.readline()
            P = Grammar.parse_productions([line.strip() for line in file])
            if not Grammar.validate(N, E, S, P):
                raise ValueError(f"Grammar in {filename} is not valid")

            return Grammar(N, E, S, P)

    def parse_line(line):
        return line.split('=', maxsplit=1)[1].strip().split()

    def parse_productions(lines):
        P = {}
        for line in lines:
            if line == '':
                continue
            lhs, rhs = line.split('->')
            lhs = lhs.strip()  # Remove spaces around LHS
            rhs_list = rhs.strip().split('|')  # Split RHS into alternatives

            # Process each alternative in RHS
            processed_rhs = []
            for alternative in rhs_list:
                # Split alternative into individual symbols and remove extra spaces
                symbols = alternative.strip().split()
                processed_rhs.append(symbols)

            if lhs in P:
                P[lhs].extend(processed_rhs)
            else:
                P[lhs] = processed_rhs
        return P

    def validate(N, E, S, P):
        if S not in N:
            print(f"Error: Start symbol '{S}' is not in the set of nonterminals N.")
            return False

        for lhs, rhs_list in P.items():
            if lhs not in N:
                print(f"Error: Production LHS '{lhs}' is not a nonterminal.")
                return False

            for rhs in rhs_list:
                for symbol in rhs:
                    if symbol not in N and symbol not in E and symbol != "epsilon":
                        print(f"Error: Symbol '{symbol}' in production '{lhs} -> {' '.join(rhs)}' is neither a terminal nor a nonterminal.")
                        return False

        return True


    def is_cfg(self):
        for key in self.P.keys():
            if key not in self.N:
                return False
        return True

    def get_nonterminal_productions(self, nonterminal):
        if nonterminal not in self.N:
            raise Exception('Can only show productions for non-terminals')
        return self.P[nonterminal]

    def get_nonterminals(self):
        return self.N

    def get_terminals(self):
        return self.E

    def __str__(self) -> str:
        return f"N = {self.get_nonterminals()}\nE = {self.get_terminals()}\nS = {self.S}\nP = {self.P}"

    def process_grammar(filename):
        """Processes a grammar file and prints details."""
        try:
            print(f"Checking {filename}:")
            g = Grammar.from_file(filename)

            # Print grammar details
            print("Nonterminals (N):", g.get_nonterminals())
            print("Terminals (E):", g.get_terminals())
            print("Start Symbol (S):", g.S)
            print("Productions (P):")
            for lhs, rhs in g.P.items():
                formatted_rhs = " | ".join([" ".join(prod) for prod in rhs])
                print(f"  {lhs} -> {formatted_rhs}")

            # Check if the grammar is a CFG
            print("Is CFG:", g.is_cfg())

            # Get productions for the start symbol
            print(f"Productions for Start Symbol ({g.S}):", g.get_nonterminal_productions(g.S))

        except ValueError as e:
            print(f"Error in {filename}: {e}")
        except Exception as ex:
            print(f"An unexpected error occurred while processing {filename}: {ex}")

        print("\n" + "-" * 30 + "\n")