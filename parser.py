r""" a simple script for parsing an EBNF grammar and  computing FIRST and FOLLOW
sets. """

from texttable import Texttable

# The grammar and start of the expression
S = "program"
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

# The empty string for better readability
eps = 'eps'

def productions(grammar):
    """ returns a dictionary with the left side of a production as keys and
    right side as values """
    P = {}
    for line in grammar.split(sep=';'):
        left, right = [s.strip() for s in line.split(sep='=', maxsplit=1)]
        right = [s.strip() for s in right.split(sep='|')]
        P[left] = right
    for N in P:
        if not grammar.find('[' + N + ']') == -1:
            P[N].append(eps)
    return P

def _size_of_dict(dictionary):
    """ Helper function which returns sum of all used keys and items in the
    value lists of a dictionary """
    size = len(dictionary.keys())
    for value in dictionary.values():
        size += len(value)
    return size

# calculates terminal and non-terminal symbol sets
P = productions(grammar)
N = set(P.keys())
T = {s.strip("'") for s in grammar.split() if s[0] == s[-1] == "'"} - {eps}

def first(input):
    """ returns the FIRST set for a given input \in (N u T)* """
    FirstA = set([])

    if input.strip("'") in T:
        return set([input.strip("'")])

    elif input == eps:
        return set([eps])

    elif input in N:
        for alpha in P[input]:
            FirstA |= first(alpha)

    elif input.strip('[]') in N:
        FirstA |= set([eps]) | first(input.strip('[]'))

    else:
        for alpha in input.split(sep=' '):
            FirstA |= (first(alpha) - set([eps]))
            if eps not in FirstA:
                break

    return FirstA

def followSet():
    """ Wrapper function for computing the FOLLOW sets of a given grammer """
    FOLLOW = {}
    for A in N:
        FOLLOW[A] = set([])
    FOLLOW[S].add('$$')

    old = None
    while old != _size_of_dict(FOLLOW):
        old = _size_of_dict(FOLLOW)
        _calcFollow(FOLLOW)

    return FOLLOW

def _calcFollow(FOLLOW):
    """ Calculates one iteration of the FOLLOW sets for all A \in N at once.
    Several iterations have to be performed to retrieve the Complete FOLLOW sets
    """
    for A in N:
        for prod in P[A]:
            text = prod.split(sep=' ')
            for i in range(len(text) - 1):
                B    = text[i].strip('[]')
                succ = text[i + 1]

                if B in N:
                    FOLLOW[B] |= first(succ) - set([eps])

                if eps in first(succ) and B in N:
                    FOLLOW[B] |= FOLLOW[A]

            if text[-1].strip('[]') in N:
                FOLLOW[text[-1].strip('[]')] |= FOLLOW[A]

FOLLOW = followSet()

def parse_table():
    table = {t: {} for t in T | {'$$'}}
    for A in N:
        for alpha in P[A]:
            for t in first(alpha) - {eps}:
                table[t][A] = alpha

            if eps in first(alpha):
                for t in FOLLOW[A]:
                    table[t][A] = alpha

            if eps in first(alpha) and '$$' in FOLLOW[A]:
                table['$$'][A] = alpha
    return table

# Hard work is over! Print the results
for prod in P.values():
    for A in prod:
        print("FIRST({0}) = {1}".format(A, first(A)))

for k, v in FOLLOW.items():
    print("FOLLOW({0}) = {1}".format(k, v))

for k, v in parse_table().items():
    print("Parse Table column ({0}) = {1}".format(k, v))

parse_table = parse_table()

table = Texttable(max_width=180)
matrix = [[left + ' -> ' + parse_table[t][left] if left in parse_table[t] else ' ' for t in parse_table if not t == eps] for left in N]
matrix.insert(0, [t for t in parse_table])
table.add_rows(matrix)
print(table.draw() + '\n')
