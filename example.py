from ParseFirstFollow import *

S = 'program'
grammar = """
    program     = [stmtList];
    stmtList    = stmt [stmtList];
    stmt        = 'id' ':=' expr ;
    expr        = term [termTail] ;
    termTail    = addOp term [termTail];
    term        = factor [factorTail] ;
    factorTail  = multOp factor [factorTail];
    factor      = '(' expr ')' | 'id' ;
    addOp       = '+' | '-' ;
    multOp      = '*' | '/'
""".strip()

# S = "E"
# grammar = """
#     E   = T [E#] ;
#     E#  = '+' T [E#] ;
#     T   = F [T#] ;
#     T#  = '∗' F [T#] ;
#     F   = '(' E ')' | 'id'
# """.strip()

expr = 'id := id * ( id + id )'
LL = ParseFirstFollow(grammar, S)

print(LL)

LL.parse_expression(expr)