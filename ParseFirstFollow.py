class ParseFirstFollow(object):
    """docstring for ParseFirstFollow"""
    def __init__(self, grammar, S):
        super(ParseFirstFollow, self).__init__()
        self.grammar     = grammar
        self.S           = S
        self.P           = self.productions()
        self.N           = set(self.P.keys())
        self.T           = {s.strip("'") for s in self.grammar.split() \
                                         if s[0] == s[-1] == "'"} - {'eps'}
        self.FOLLOW      = self.followSet()
        self.parse_table = self.gen_parse_table()

    def productions(self):
        """ returns a dictionary with the left side of a production as keys and
        right side as values """
        P = {}
        for line in self.grammar.split(sep=';'):
            left, right = [s.strip() for s in line.split(sep='=', maxsplit=1)]
            right = [s.strip() for s in right.split(sep='|')]
            P[left] = right
        for N in P:
            if not self.grammar.find('[' + N + ']') == -1:
                P[N].append('eps')
        return P

    @staticmethod
    def _size_of_dict(dictionary):
        """ Helper function which returns sum of all used keys and items in the
        value lists of a dictionary """
        size = len(dictionary.keys())
        for value in dictionary.values():
            size += len(value)
        return size

    def first(self, input):
        """ returns the self.FIRST set for a given input \in (N u T)* """
        FirstA = set([])

        if input.strip("'") in self.T:
            return {input.strip("'")}

        elif input == 'eps':
            return {'eps'}

        elif input in self.N:
            for alpha in self.P[input]:
                FirstA |= self.first(alpha)

        elif input.strip('[]') in self.N:
            FirstA |= {'eps'} | self.first(input.strip('[]'))

        else:
            for alpha in input.split(sep=' '):
                FirstA |= self.first(alpha) - {'eps'}
                if 'eps' not in FirstA:
                    break

        return FirstA

    def followSet(self):
        """ Wrapper function for computing the FOLLOW sets of a given grammar"""
        FOLLOW = {}
        for A in self.N:
            FOLLOW[A] = set()
        FOLLOW[self.S] |= {'$$'}

        old = None
        while old != self._size_of_dict(FOLLOW):
            old = self._size_of_dict(FOLLOW)
            self._calcFollow(FOLLOW)

        return FOLLOW

    def _calcFollow(self, FOLLOW):
        """ Calculates one iteration of the FOLLOW sets for all A \in N at once.
        Several iterations have to be performed to retrieve the Complete FOLLOW sets
        """
        for A in self.N:
            for prod in self.P[A]:
                text = prod.split(sep=' ')
                for i in range(len(text) - 1):
                    B    = text[i].strip('[]')
                    succ = text[i + 1]

                    if B in self.N:
                        FOLLOW[B] |= self.first(succ) - {'eps'}

                    if 'eps' in self.first(succ) and B in self.N:
                        FOLLOW[B] |= FOLLOW[A]

                if text[-1].strip('[]') in self.N:
                    FOLLOW[text[-1].strip('[]')] |= FOLLOW[A]

    def gen_parse_table(self):
        table = {t: {} for t in self.T | {'$$'}}
        for A in self.N:
            for alpha in self.P[A]:
                for t in self.first(alpha) - {'eps'}:
                    table[t][A] = alpha

                if 'eps' in self.first(alpha):
                    for t in self.FOLLOW[A]:
                        table[t][A] = alpha

                if 'eps' in self.first(alpha) and '$$' in self.FOLLOW[A]:
                    table['$$'][A] = alpha
        return table

    def __str__(self):
        from texttable import Texttable
        table = Texttable(max_width=180)
        matrix = [[left + ' -> ' + self.parse_table[t][left]
                    if left in self.parse_table[t] else ' '
                    for t in self.parse_table if not t == 'eps']
                        for left in self.N]
        matrix.insert(0, [t for t in self.parse_table])
        table.add_rows(matrix)
        return table.draw() + '\n'

    def parse_expression(self, expr):
        stack = ['gamma', self.S]
        expr  = expr.split() + ['$$']
        while stack != ['gamma']:
            print('{0:70} | {1}'.format(' '.join(stack), ' '.join(expr)))
            if stack[-1] == expr[0]:
                del stack[-1]
                del expr[0]
            else:
                prod = [s.strip("'[]") for s in self.parse_table[expr[0]][stack[-1]].split()]
                del stack[-1]
                if not 'eps' in prod:
                    stack += prod[::-1]
        print('{0:70} | {1}'.format(' '.join(stack), ' '.join(expr)))
