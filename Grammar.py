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
            lhs = lhs.strip()
            rhs_list = rhs.strip().split('|')
            for alternative in rhs_list:
                symbols = alternative.strip().split()
                if lhs in P:
                    P[lhs].append(symbols)
                else:
                    P[lhs] = [symbols]
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
                        print(
                            f"Error: Symbol '{symbol}' in production '{lhs} -> {' '.join(rhs)}' is neither a terminal nor a nonterminal.")
                        return False

        return True

    def is_cfg(self):        
        if self.S not in self.N:
            return False
        
        print(self.P.keys())

        for lhs in self.P.keys():
            if lhs not in self.N:
                return False
            
            for rhs in self.P[lhs]:
                for symbol in rhs:
                    if symbol not in self.N and symbol not in self.E and symbol != "epsilon":
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

    def process_grammar_with_interface(filename):
        """Processes a grammar file and provides an interactive menu."""
        try:
            print(f"\nLoading grammar from {filename}...\n")
            g = Grammar.from_file(filename)

            # Interactive menu loop
            while True:
                print(f"Grammar: {filename}")
                print("Options:")
                print("1. Show Nonterminals (N)")
                print("2. Show Terminals (E)")
                print("3. Show Productions (P)")
                print("4. Check if CFG")
                print("5. Show Productions for Start Symbol (S)")
                print("6. Show All")
                print("7. Exit")
                choice = input("Choose an option: ")

                if choice == "1":
                    print("Nonterminals (N):", g.get_nonterminals())
                elif choice == "2":
                    print("Terminals (E):", g.get_terminals())
                elif choice == "3":
                    print("Productions (P):")
                    for lhs, rhs in g.P.items():
                        formatted_rhs = " | ".join([" ".join(prod) for prod in rhs])
                        print(f"  {lhs} -> {formatted_rhs}")
                elif choice == "4":
                    print("Is CFG:", g.is_cfg())
                elif choice == "5":
                    print(f"Productions for Start Symbol ({g.S}):", g.get_nonterminal_productions(g.S))
                elif choice == "6":  # Show all
                    print("Nonterminals (N):", g.get_nonterminals())
                    print("Terminals (E):", g.get_terminals())
                    print("Productions (P):")
                    for lhs, rhs in g.P.items():
                        formatted_rhs = " | ".join([" ".join(prod) for prod in rhs])
                        print(f"  {lhs} -> {formatted_rhs}")
                    print("Is CFG:", g.is_cfg())
                    print(f"Productions for Start Symbol ({g.S}):", g.get_nonterminal_productions(g.S))
                elif choice == "7":
                    print("Exiting...")
                    break
                else:
                    print("Invalid choice. Please try again.")

                print("\n" + "-" * 30 + "\n")

        except ValueError as e:
            print(f"Error in {filename}: {e}")
        except Exception as ex:
            print(f"An unexpected error occurred while processing {filename}: {ex}")
            
    
