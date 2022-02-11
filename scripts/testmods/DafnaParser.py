# Generated from Dafna.g4 by ANTLR 4.9
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\21")
        buf.write("`\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b")
        buf.write("\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\4\16\t")
        buf.write("\16\4\17\t\17\4\20\t\20\3\2\3\2\3\2\3\3\3\3\3\3\7\3\'")
        buf.write("\n\3\f\3\16\3*\13\3\3\4\3\4\5\4.\n\4\3\5\3\5\3\5\3\5\3")
        buf.write("\6\3\6\3\7\3\7\3\b\3\b\3\t\3\t\5\t<\n\t\3\n\3\n\5\n@\n")
        buf.write("\n\3\n\5\nC\n\n\3\13\3\13\5\13G\n\13\3\13\5\13J\n\13\3")
        buf.write("\f\3\f\3\f\3\f\3\r\3\r\3\r\3\r\3\r\3\r\5\rV\n\r\3\16\3")
        buf.write("\16\3\17\3\17\3\20\3\20\5\20^\n\20\3\20\2\2\21\2\4\6\b")
        buf.write("\n\f\16\20\22\24\26\30\32\34\36\2\3\4\2\7\7\21\21\2Z\2")
        buf.write(" \3\2\2\2\4#\3\2\2\2\6-\3\2\2\2\b/\3\2\2\2\n\63\3\2\2")
        buf.write("\2\f\65\3\2\2\2\16\67\3\2\2\2\20;\3\2\2\2\22=\3\2\2\2")
        buf.write("\24D\3\2\2\2\26K\3\2\2\2\30U\3\2\2\2\32W\3\2\2\2\34Y\3")
        buf.write("\2\2\2\36[\3\2\2\2 !\5\4\3\2!\"\7\2\2\3\"\3\3\2\2\2#(")
        buf.write("\5\6\4\2$%\7\13\2\2%\'\5\6\4\2&$\3\2\2\2\'*\3\2\2\2(&")
        buf.write("\3\2\2\2()\3\2\2\2)\5\3\2\2\2*(\3\2\2\2+.\5\b\5\2,.\5")
        buf.write("\n\6\2-+\3\2\2\2-,\3\2\2\2.\7\3\2\2\2/\60\5\f\7\2\60\61")
        buf.write("\7\t\2\2\61\62\5\20\t\2\62\t\3\2\2\2\63\64\3\2\2\2\64")
        buf.write("\13\3\2\2\2\65\66\7\7\2\2\66\r\3\2\2\2\678\5\f\7\28\17")
        buf.write("\3\2\2\29<\5\22\n\2:<\7\21\2\2;9\3\2\2\2;:\3\2\2\2<\21")
        buf.write("\3\2\2\2=B\5\24\13\2>@\5\32\16\2?>\3\2\2\2?@\3\2\2\2@")
        buf.write("A\3\2\2\2AC\5\22\n\2B?\3\2\2\2BC\3\2\2\2C\23\3\2\2\2D")
        buf.write("F\5\30\r\2EG\5\24\13\2FE\3\2\2\2FG\3\2\2\2GI\3\2\2\2H")
        buf.write("J\5\26\f\2IH\3\2\2\2IJ\3\2\2\2J\25\3\2\2\2KL\7\f\2\2L")
        buf.write("M\t\2\2\2MN\7\r\2\2N\27\3\2\2\2OV\5\16\b\2PV\5\36\20\2")
        buf.write("QR\7\16\2\2RS\5\22\n\2ST\7\17\2\2TV\3\2\2\2UO\3\2\2\2")
        buf.write("UP\3\2\2\2UQ\3\2\2\2V\31\3\2\2\2WX\7\b\2\2X\33\3\2\2\2")
        buf.write("YZ\7\n\2\2Z\35\3\2\2\2[]\7\6\2\2\\^\5\36\20\2]\\\3\2\2")
        buf.write("\2]^\3\2\2\2^\37\3\2\2\2\13(-;?BFIU]")
        return buf.getvalue()


class DafnaParser ( Parser ):

    grammarFileName = "Dafna.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'?'", "'*'", "'+'", "<INVALID>", "<INVALID>", 
                     "'|'", "'='", "'and'", "<INVALID>", "'{'", "'}'", "'('", 
                     "')'" ]

    symbolicNames = [ "<INVALID>", "QUESTION", "STAR", "PLUS", "NUC", "IDENT", 
                      "OR", "ASSIGN", "AND", "SEMI", "LBRACE", "RBRACE", 
                      "LPAREN", "RPAREN", "WS", "NUM_INT" ]

    RULE_program = 0
    RULE_statements = 1
    RULE_statement = 2
    RULE_assignmentStatement = 3
    RULE_emptyStatement = 4
    RULE_identifier = 5
    RULE_variable = 6
    RULE_expression = 7
    RULE_nuc_expression = 8
    RULE_term = 9
    RULE_scoped_operator = 10
    RULE_factor = 11
    RULE_additiveoperator = 12
    RULE_multiplicativeoperator = 13
    RULE_nucstring = 14

    ruleNames =  [ "program", "statements", "statement", "assignmentStatement", 
                   "emptyStatement", "identifier", "variable", "expression", 
                   "nuc_expression", "term", "scoped_operator", "factor", 
                   "additiveoperator", "multiplicativeoperator", "nucstring" ]

    EOF = Token.EOF
    QUESTION=1
    STAR=2
    PLUS=3
    NUC=4
    IDENT=5
    OR=6
    ASSIGN=7
    AND=8
    SEMI=9
    LBRACE=10
    RBRACE=11
    LPAREN=12
    RPAREN=13
    WS=14
    NUM_INT=15

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def statements(self):
            return self.getTypedRuleContext(DafnaParser.StatementsContext,0)


        def EOF(self):
            return self.getToken(DafnaParser.EOF, 0)

        def getRuleIndex(self):
            return DafnaParser.RULE_program

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProgram" ):
                listener.enterProgram(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProgram" ):
                listener.exitProgram(self)




    def program(self):

        localctx = DafnaParser.ProgramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_program)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 30
            self.statements()
            self.state = 31
            self.match(DafnaParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementsContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(DafnaParser.StatementContext)
            else:
                return self.getTypedRuleContext(DafnaParser.StatementContext,i)


        def SEMI(self, i:int=None):
            if i is None:
                return self.getTokens(DafnaParser.SEMI)
            else:
                return self.getToken(DafnaParser.SEMI, i)

        def getRuleIndex(self):
            return DafnaParser.RULE_statements

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatements" ):
                listener.enterStatements(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatements" ):
                listener.exitStatements(self)




    def statements(self):

        localctx = DafnaParser.StatementsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_statements)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 33
            self.statement()
            self.state = 38
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==DafnaParser.SEMI:
                self.state = 34
                self.match(DafnaParser.SEMI)
                self.state = 35
                self.statement()
                self.state = 40
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def assignmentStatement(self):
            return self.getTypedRuleContext(DafnaParser.AssignmentStatementContext,0)


        def emptyStatement(self):
            return self.getTypedRuleContext(DafnaParser.EmptyStatementContext,0)


        def getRuleIndex(self):
            return DafnaParser.RULE_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatement" ):
                listener.enterStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatement" ):
                listener.exitStatement(self)




    def statement(self):

        localctx = DafnaParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_statement)
        try:
            self.state = 43
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [DafnaParser.IDENT]:
                self.enterOuterAlt(localctx, 1)
                self.state = 41
                self.assignmentStatement()
                pass
            elif token in [DafnaParser.EOF, DafnaParser.SEMI]:
                self.enterOuterAlt(localctx, 2)
                self.state = 42
                self.emptyStatement()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AssignmentStatementContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(DafnaParser.IdentifierContext,0)


        def ASSIGN(self):
            return self.getToken(DafnaParser.ASSIGN, 0)

        def expression(self):
            return self.getTypedRuleContext(DafnaParser.ExpressionContext,0)


        def getRuleIndex(self):
            return DafnaParser.RULE_assignmentStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAssignmentStatement" ):
                listener.enterAssignmentStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAssignmentStatement" ):
                listener.exitAssignmentStatement(self)




    def assignmentStatement(self):

        localctx = DafnaParser.AssignmentStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_assignmentStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 45
            self.identifier()
            self.state = 46
            self.match(DafnaParser.ASSIGN)
            self.state = 47
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EmptyStatementContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return DafnaParser.RULE_emptyStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEmptyStatement" ):
                listener.enterEmptyStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEmptyStatement" ):
                listener.exitEmptyStatement(self)




    def emptyStatement(self):

        localctx = DafnaParser.EmptyStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_emptyStatement)
        try:
            self.enterOuterAlt(localctx, 1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IdentifierContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENT(self):
            return self.getToken(DafnaParser.IDENT, 0)

        def getRuleIndex(self):
            return DafnaParser.RULE_identifier

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIdentifier" ):
                listener.enterIdentifier(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIdentifier" ):
                listener.exitIdentifier(self)




    def identifier(self):

        localctx = DafnaParser.IdentifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_identifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 51
            self.match(DafnaParser.IDENT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class VariableContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(DafnaParser.IdentifierContext,0)


        def getRuleIndex(self):
            return DafnaParser.RULE_variable

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVariable" ):
                listener.enterVariable(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVariable" ):
                listener.exitVariable(self)




    def variable(self):

        localctx = DafnaParser.VariableContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_variable)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 53
            self.identifier()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def nuc_expression(self):
            return self.getTypedRuleContext(DafnaParser.Nuc_expressionContext,0)


        def NUM_INT(self):
            return self.getToken(DafnaParser.NUM_INT, 0)

        def getRuleIndex(self):
            return DafnaParser.RULE_expression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpression" ):
                listener.enterExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpression" ):
                listener.exitExpression(self)




    def expression(self):

        localctx = DafnaParser.ExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_expression)
        try:
            self.state = 57
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [DafnaParser.NUC, DafnaParser.IDENT, DafnaParser.LPAREN]:
                self.enterOuterAlt(localctx, 1)
                self.state = 55
                self.nuc_expression()
                pass
            elif token in [DafnaParser.NUM_INT]:
                self.enterOuterAlt(localctx, 2)
                self.state = 56
                self.match(DafnaParser.NUM_INT)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Nuc_expressionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def term(self):
            return self.getTypedRuleContext(DafnaParser.TermContext,0)


        def nuc_expression(self):
            return self.getTypedRuleContext(DafnaParser.Nuc_expressionContext,0)


        def additiveoperator(self):
            return self.getTypedRuleContext(DafnaParser.AdditiveoperatorContext,0)


        def getRuleIndex(self):
            return DafnaParser.RULE_nuc_expression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNuc_expression" ):
                listener.enterNuc_expression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNuc_expression" ):
                listener.exitNuc_expression(self)




    def nuc_expression(self):

        localctx = DafnaParser.Nuc_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_nuc_expression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 59
            self.term()
            self.state = 64
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << DafnaParser.NUC) | (1 << DafnaParser.IDENT) | (1 << DafnaParser.OR) | (1 << DafnaParser.LPAREN))) != 0):
                self.state = 61
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==DafnaParser.OR:
                    self.state = 60
                    self.additiveoperator()


                self.state = 63
                self.nuc_expression()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TermContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def factor(self):
            return self.getTypedRuleContext(DafnaParser.FactorContext,0)


        def term(self):
            return self.getTypedRuleContext(DafnaParser.TermContext,0)


        def scoped_operator(self):
            return self.getTypedRuleContext(DafnaParser.Scoped_operatorContext,0)


        def getRuleIndex(self):
            return DafnaParser.RULE_term

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTerm" ):
                listener.enterTerm(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTerm" ):
                listener.exitTerm(self)




    def term(self):

        localctx = DafnaParser.TermContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_term)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 66
            self.factor()
            self.state = 68
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,5,self._ctx)
            if la_ == 1:
                self.state = 67
                self.term()


            self.state = 71
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,6,self._ctx)
            if la_ == 1:
                self.state = 70
                self.scoped_operator()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Scoped_operatorContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(DafnaParser.LBRACE, 0)

        def RBRACE(self):
            return self.getToken(DafnaParser.RBRACE, 0)

        def IDENT(self):
            return self.getToken(DafnaParser.IDENT, 0)

        def NUM_INT(self):
            return self.getToken(DafnaParser.NUM_INT, 0)

        def getRuleIndex(self):
            return DafnaParser.RULE_scoped_operator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterScoped_operator" ):
                listener.enterScoped_operator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitScoped_operator" ):
                listener.exitScoped_operator(self)




    def scoped_operator(self):

        localctx = DafnaParser.Scoped_operatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_scoped_operator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 73
            self.match(DafnaParser.LBRACE)
            self.state = 74
            _la = self._input.LA(1)
            if not(_la==DafnaParser.IDENT or _la==DafnaParser.NUM_INT):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 75
            self.match(DafnaParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FactorContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def variable(self):
            return self.getTypedRuleContext(DafnaParser.VariableContext,0)


        def nucstring(self):
            return self.getTypedRuleContext(DafnaParser.NucstringContext,0)


        def LPAREN(self):
            return self.getToken(DafnaParser.LPAREN, 0)

        def nuc_expression(self):
            return self.getTypedRuleContext(DafnaParser.Nuc_expressionContext,0)


        def RPAREN(self):
            return self.getToken(DafnaParser.RPAREN, 0)

        def getRuleIndex(self):
            return DafnaParser.RULE_factor

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFactor" ):
                listener.enterFactor(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFactor" ):
                listener.exitFactor(self)




    def factor(self):

        localctx = DafnaParser.FactorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_factor)
        try:
            self.state = 83
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [DafnaParser.IDENT]:
                self.enterOuterAlt(localctx, 1)
                self.state = 77
                self.variable()
                pass
            elif token in [DafnaParser.NUC]:
                self.enterOuterAlt(localctx, 2)
                self.state = 78
                self.nucstring()
                pass
            elif token in [DafnaParser.LPAREN]:
                self.enterOuterAlt(localctx, 3)
                self.state = 79
                self.match(DafnaParser.LPAREN)
                self.state = 80
                self.nuc_expression()
                self.state = 81
                self.match(DafnaParser.RPAREN)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AdditiveoperatorContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def OR(self):
            return self.getToken(DafnaParser.OR, 0)

        def getRuleIndex(self):
            return DafnaParser.RULE_additiveoperator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAdditiveoperator" ):
                listener.enterAdditiveoperator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAdditiveoperator" ):
                listener.exitAdditiveoperator(self)




    def additiveoperator(self):

        localctx = DafnaParser.AdditiveoperatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_additiveoperator)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 85
            self.match(DafnaParser.OR)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MultiplicativeoperatorContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def AND(self):
            return self.getToken(DafnaParser.AND, 0)

        def getRuleIndex(self):
            return DafnaParser.RULE_multiplicativeoperator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMultiplicativeoperator" ):
                listener.enterMultiplicativeoperator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMultiplicativeoperator" ):
                listener.exitMultiplicativeoperator(self)




    def multiplicativeoperator(self):

        localctx = DafnaParser.MultiplicativeoperatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_multiplicativeoperator)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 87
            self.match(DafnaParser.AND)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NucstringContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUC(self):
            return self.getToken(DafnaParser.NUC, 0)

        def nucstring(self):
            return self.getTypedRuleContext(DafnaParser.NucstringContext,0)


        def getRuleIndex(self):
            return DafnaParser.RULE_nucstring

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNucstring" ):
                listener.enterNucstring(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNucstring" ):
                listener.exitNucstring(self)




    def nucstring(self):

        localctx = DafnaParser.NucstringContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_nucstring)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 89
            self.match(DafnaParser.NUC)
            self.state = 91
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,8,self._ctx)
            if la_ == 1:
                self.state = 90
                self.nucstring()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





