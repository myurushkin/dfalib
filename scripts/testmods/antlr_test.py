import sys
from antlr4 import *
from DafnaLexer import *
from DafnaParser import *
from DafnaListener import *

class KeyPrinter(DafnaListener):
    def enterR(self, ctx):

        print("Oh, a key!")

# antlr4 -Dlanguage=Python2 MyGrammar.g4
def main(argv):
    input_stream = FileStream("antlr_test_program.txt")
    lexer = DafnaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = DafnaParser(stream)
    tree = parser.program()

    printer = KeyPrinter()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)


if __name__ == '__main__':
    main(sys.argv)