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

expression: nuc_expression | NUM_INT;
  

nuc_expression
   : term (additiveoperator? nuc_expression)?
   ;


term
   : factor term? scoped_operator?
   ;

scoped_operator : LBRACE (IDENT | NUM_INT)  RBRACE;

factor
   : variable
   | nucstring
   | LPAREN nuc_expression RPAREN
   ;

//quantified_factor : factor quantifier?;

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

LBRACE: '{';
RBRACE: '}';

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
