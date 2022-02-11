# Generated from Dafna.g4 by ANTLR 4.9
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .DafnaParser import DafnaParser
else:
    from DafnaParser import DafnaParser

# This class defines a complete listener for a parse tree produced by DafnaParser.
class DafnaListener(ParseTreeListener):

    # Enter a parse tree produced by DafnaParser#program.
    def enterProgram(self, ctx:DafnaParser.ProgramContext):
        pass

    # Exit a parse tree produced by DafnaParser#program.
    def exitProgram(self, ctx:DafnaParser.ProgramContext):
        pass


    # Enter a parse tree produced by DafnaParser#statements.
    def enterStatements(self, ctx:DafnaParser.StatementsContext):
        pass

    # Exit a parse tree produced by DafnaParser#statements.
    def exitStatements(self, ctx:DafnaParser.StatementsContext):
        pass


    # Enter a parse tree produced by DafnaParser#statement.
    def enterStatement(self, ctx:DafnaParser.StatementContext):
        pass

    # Exit a parse tree produced by DafnaParser#statement.
    def exitStatement(self, ctx:DafnaParser.StatementContext):
        pass


    # Enter a parse tree produced by DafnaParser#assignmentStatement.
    def enterAssignmentStatement(self, ctx:DafnaParser.AssignmentStatementContext):
        pass

    # Exit a parse tree produced by DafnaParser#assignmentStatement.
    def exitAssignmentStatement(self, ctx:DafnaParser.AssignmentStatementContext):
        pass


    # Enter a parse tree produced by DafnaParser#emptyStatement.
    def enterEmptyStatement(self, ctx:DafnaParser.EmptyStatementContext):
        pass

    # Exit a parse tree produced by DafnaParser#emptyStatement.
    def exitEmptyStatement(self, ctx:DafnaParser.EmptyStatementContext):
        pass


    # Enter a parse tree produced by DafnaParser#identifier.
    def enterIdentifier(self, ctx:DafnaParser.IdentifierContext):
        pass

    # Exit a parse tree produced by DafnaParser#identifier.
    def exitIdentifier(self, ctx:DafnaParser.IdentifierContext):
        pass


    # Enter a parse tree produced by DafnaParser#variable.
    def enterVariable(self, ctx:DafnaParser.VariableContext):
        pass

    # Exit a parse tree produced by DafnaParser#variable.
    def exitVariable(self, ctx:DafnaParser.VariableContext):
        pass


    # Enter a parse tree produced by DafnaParser#expression.
    def enterExpression(self, ctx:DafnaParser.ExpressionContext):
        pass

    # Exit a parse tree produced by DafnaParser#expression.
    def exitExpression(self, ctx:DafnaParser.ExpressionContext):
        pass


    # Enter a parse tree produced by DafnaParser#nuc_expression.
    def enterNuc_expression(self, ctx:DafnaParser.Nuc_expressionContext):
        pass

    # Exit a parse tree produced by DafnaParser#nuc_expression.
    def exitNuc_expression(self, ctx:DafnaParser.Nuc_expressionContext):
        pass


    # Enter a parse tree produced by DafnaParser#term.
    def enterTerm(self, ctx:DafnaParser.TermContext):
        pass

    # Exit a parse tree produced by DafnaParser#term.
    def exitTerm(self, ctx:DafnaParser.TermContext):
        pass


    # Enter a parse tree produced by DafnaParser#scoped_operator.
    def enterScoped_operator(self, ctx:DafnaParser.Scoped_operatorContext):
        pass

    # Exit a parse tree produced by DafnaParser#scoped_operator.
    def exitScoped_operator(self, ctx:DafnaParser.Scoped_operatorContext):
        pass


    # Enter a parse tree produced by DafnaParser#factor.
    def enterFactor(self, ctx:DafnaParser.FactorContext):
        pass

    # Exit a parse tree produced by DafnaParser#factor.
    def exitFactor(self, ctx:DafnaParser.FactorContext):
        pass


    # Enter a parse tree produced by DafnaParser#additiveoperator.
    def enterAdditiveoperator(self, ctx:DafnaParser.AdditiveoperatorContext):
        pass

    # Exit a parse tree produced by DafnaParser#additiveoperator.
    def exitAdditiveoperator(self, ctx:DafnaParser.AdditiveoperatorContext):
        pass


    # Enter a parse tree produced by DafnaParser#multiplicativeoperator.
    def enterMultiplicativeoperator(self, ctx:DafnaParser.MultiplicativeoperatorContext):
        pass

    # Exit a parse tree produced by DafnaParser#multiplicativeoperator.
    def exitMultiplicativeoperator(self, ctx:DafnaParser.MultiplicativeoperatorContext):
        pass


    # Enter a parse tree produced by DafnaParser#nucstring.
    def enterNucstring(self, ctx:DafnaParser.NucstringContext):
        pass

    # Exit a parse tree produced by DafnaParser#nucstring.
    def exitNucstring(self, ctx:DafnaParser.NucstringContext):
        pass



del DafnaParser