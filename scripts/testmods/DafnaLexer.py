# Generated from Dafna.g4 by ANTLR 4.9
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\21")
        buf.write("K\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\4\16")
        buf.write("\t\16\4\17\t\17\4\20\t\20\3\2\3\2\3\3\3\3\3\4\3\4\3\5")
        buf.write("\3\5\3\6\3\6\7\6,\n\6\f\6\16\6/\13\6\3\7\3\7\3\b\3\b\3")
        buf.write("\t\3\t\3\t\3\t\3\n\3\n\3\13\3\13\3\f\3\f\3\r\3\r\3\16")
        buf.write("\3\16\3\17\3\17\3\17\3\17\3\20\6\20H\n\20\r\20\16\20I")
        buf.write("\2\2\21\3\3\5\4\7\5\t\6\13\7\r\b\17\t\21\n\23\13\25\f")
        buf.write("\27\r\31\16\33\17\35\20\37\21\3\2\6\6\2cceeiivv\5\2\62")
        buf.write(";C\\aa\4\2\f\f==\5\2\13\13\17\17\"\"\2L\2\3\3\2\2\2\2")
        buf.write("\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2\2\2\2\13\3\2\2\2\2\r\3")
        buf.write("\2\2\2\2\17\3\2\2\2\2\21\3\2\2\2\2\23\3\2\2\2\2\25\3\2")
        buf.write("\2\2\2\27\3\2\2\2\2\31\3\2\2\2\2\33\3\2\2\2\2\35\3\2\2")
        buf.write("\2\2\37\3\2\2\2\3!\3\2\2\2\5#\3\2\2\2\7%\3\2\2\2\t\'\3")
        buf.write("\2\2\2\13)\3\2\2\2\r\60\3\2\2\2\17\62\3\2\2\2\21\64\3")
        buf.write("\2\2\2\238\3\2\2\2\25:\3\2\2\2\27<\3\2\2\2\31>\3\2\2\2")
        buf.write("\33@\3\2\2\2\35B\3\2\2\2\37G\3\2\2\2!\"\7A\2\2\"\4\3\2")
        buf.write("\2\2#$\7,\2\2$\6\3\2\2\2%&\7-\2\2&\b\3\2\2\2\'(\t\2\2")
        buf.write("\2(\n\3\2\2\2)-\4C\\\2*,\t\3\2\2+*\3\2\2\2,/\3\2\2\2-")
        buf.write("+\3\2\2\2-.\3\2\2\2.\f\3\2\2\2/-\3\2\2\2\60\61\7~\2\2")
        buf.write("\61\16\3\2\2\2\62\63\7?\2\2\63\20\3\2\2\2\64\65\7c\2\2")
        buf.write("\65\66\7p\2\2\66\67\7f\2\2\67\22\3\2\2\289\t\4\2\29\24")
        buf.write("\3\2\2\2:;\7}\2\2;\26\3\2\2\2<=\7\177\2\2=\30\3\2\2\2")
        buf.write(">?\7*\2\2?\32\3\2\2\2@A\7+\2\2A\34\3\2\2\2BC\t\5\2\2C")
        buf.write("D\3\2\2\2DE\b\17\2\2E\36\3\2\2\2FH\4\62;\2GF\3\2\2\2H")
        buf.write("I\3\2\2\2IG\3\2\2\2IJ\3\2\2\2J \3\2\2\2\5\2-I\3\b\2\2")
        return buf.getvalue()


class DafnaLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    QUESTION = 1
    STAR = 2
    PLUS = 3
    NUC = 4
    IDENT = 5
    OR = 6
    ASSIGN = 7
    AND = 8
    SEMI = 9
    LBRACE = 10
    RBRACE = 11
    LPAREN = 12
    RPAREN = 13
    WS = 14
    NUM_INT = 15

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'?'", "'*'", "'+'", "'|'", "'='", "'and'", "'{'", "'}'", "'('", 
            "')'" ]

    symbolicNames = [ "<INVALID>",
            "QUESTION", "STAR", "PLUS", "NUC", "IDENT", "OR", "ASSIGN", 
            "AND", "SEMI", "LBRACE", "RBRACE", "LPAREN", "RPAREN", "WS", 
            "NUM_INT" ]

    ruleNames = [ "QUESTION", "STAR", "PLUS", "NUC", "IDENT", "OR", "ASSIGN", 
                  "AND", "SEMI", "LBRACE", "RBRACE", "LPAREN", "RPAREN", 
                  "WS", "NUM_INT" ]

    grammarFileName = "Dafna.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


