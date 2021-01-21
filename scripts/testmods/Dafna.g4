grammar Dafna;

// PARSER RULES
program:
   statements EOF
   ;


statements
   : statement (SEMI statement)*
   ;

statement
   : assignmentStatement
   | emptyStatement
   ;

assignmentStatement
   : identifier ASSIGN expression
   ;

emptyStatement
   :
   ;


identifier
   : IDENT
   ;

variable
   : identifier
   ;

expression
   : term (additiveoperator expression)?
   ;


term
   : factor term? ('{' (IDENT | NUM_INT)  '}')?
   ;

factor
   : variable
   | nucstring
   | LPAREN expression RPAREN
   | expression quantifier
   ;

quantified_factor : factor quantifier?;

QUESTION : '?';
STAR : '*';
PLUS : '+';

additiveoperator
   : OR
   ;

multiplicativeoperator
   : AND
   ;

NUC
   : 'a' | 'g' | 'c' | 't'
   ;

nucstring
   : NUC nucstring?
   ;

// LEXER RULES


IDENT 
   : ('A' .. 'Z') ('A' .. 'Z' | '0' .. '9' | '_')*
   ;


   
OR
   : '|'
   ;


ASSIGN
   : '='
   ;

AND
   : 'and'
   ;

SEMI
   : ';' | '\n'
   ;

LPAREN
   : '('
   ;

RPAREN
   : ')'
   ;

WS
   : [ \t\r] -> skip
   ;

NUM_INT
   : ('0' .. '9') +
   ;
