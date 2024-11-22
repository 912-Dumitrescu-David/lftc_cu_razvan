from Grammar import Grammar

if __name__ == "__main__":
    # Specify the grammar files to process
    grammar_files = ["g1.txt", "g2.txt"]

    # Process each grammar file
    for filename in grammar_files:
        Grammar.process_grammar(filename)
