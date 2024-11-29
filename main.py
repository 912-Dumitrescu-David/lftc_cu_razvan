from Grammar import Grammar
from Parser import LR0Parser

if __name__ == "__main__":
    # Specify the grammar files to process
    grammar_files = ["g1.txt"]

    for filename in grammar_files:
        g = Grammar.from_file(filename)
        parser = LR0Parser(g)
        parser.construct_parsing_table()

        # Example input string to parse
        input_string = "a a c b b"
        parser.parse(input_string)