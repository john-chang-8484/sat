from pyparsing import *


# define the grammar
identifier = Word(alphas+'&^|~', alphanums+'&^|~')
expr = Forward()
parens = Suppress(Literal('(')) + ZeroOrMore(expr) + Suppress(Literal(')'))
expr <<= Group(parens | identifier)
constr_op = Literal('=>') | Literal('=')
constr = Group(expr + constr_op + expr)
grammar = ZeroOrMore(constr | expr)



def n(var):
    """ Logically negates a variable. """
    if var[0] == '~':
        return var[1:]
    else:
        return '~' + var


# a useful class for making clause sets
class Clauses:
    """ A set of clauses that must all be fulfilled.
        Starts out empty, provides many methods for
        adding more clauses, including a mini
        language. Allows for adding macros.
    """
    T =  'T~'   # constant logical true
    F = '~T~'   # constant logical false
    counter = 0
    def __init__(self):
        self.clauses = [] # a set of clauses
        self.macros = {}  # list of macros for this Clauses obj's language
    def junkvar(self):
        Clauses.counter += 1
        return 'junk~%d' % Clauses.counter
    def ext(self, *args): # extend the clauses list by each argument clause
        self.clauses.extend(args)
    def join(self, cls): # join with another clauses object
        self.ext(*cls.clauses)
    def get_clauses(self):
        return self.clauses + [[self.T]] # force T to be true
    def print_clauses(self):
        for clause in self.clauses:
            print(' v '.join(clause))
    
    # logical constraints:
    def l_ist(self, a): # a is true
        self.ext([a])
    def l_isf(self, a): # a is false
        self.ext([n(a)])
    def l_if(self, a, b): # if a, then b
        self.ext([n(a), b])
    def l_iff(self, a, b): # a iff b
        self.ext([n(a), b], [a, n(b)])
    def l_any(self, vlist):
        self.ext(vlist)
    
    # logical computations: make new variable, put result there
    def xor_cnf(self, a, b):
        ans = self.junkvar()
        self.ext(
            [n(a), n(b), n(ans)],
            [n(a), b, ans],
            [a, n(b), ans],
            [a, b, n(ans)])
        return ans
    def eq(self, a, b):
        return n(self.xor_cnf(a, b))
    def and_cnf(self, a, b):
        ans = self.junkvar()
        self.ext(
            [n(a), n(b), ans],
            [a, n(ans)],
            [b, n(ans)])
        return ans
    def or_cnf(self, a, b):
        ans = self.junkvar()
        self.ext(
            [a, b, n(ans)],
            [n(a), ans],
            [n(b), ans])
        return ans
    def all_cnf(self, *vlist):
        if len(vlist) == 0:
            return self.T
        elif len(vlist) == 1:
            ans = self.junkvar()
            self.l_iff(ans, vlist[0])
            return ans
        elif len(vlist) == 2:
            return self.and_cnf(vlist[0], vlist[1])
        elif len(vlist) == 3:
            return self.and_cnf(self.and_cnf(vlist[0], vlist[1]), vlist[2])
        else:
            half = len(vlist) // 2
            return self.and_cnf(self.all_cnf(*vlist[0:half]), self.all_cnf(*vlist[half:]))
    def any_cnf(self, *vlist):
        if len(vlist) == 0:
            return self.F
        elif len(vlist) == 1:
            ans = self.junkvar()
            self.l_iff(ans, vlist[0])
            return ans
        elif len(vlist) == 2:
            return self.or_cnf(vlist[0], vlist[1])
        elif len(vlist) == 3:
            return self.or_cnf(self.or_cnf(vlist[0], vlist[1]), vlist[2])
        else:
            half = len(vlist) // 2
            return self.or_cnf(self.any_cnf(*vlist[0:half]), self.any_cnf(*vlist[half:]))

    
    # parse a program written in wombley, update clauses accordingly
    def run(self, prog):
        tokens = grammar.parseString(prog)
        for stat in tokens:
            if len(stat) == 3 and isinstance(stat[1], str): # check if this is a constr
                if stat[1] == '=':
                    self.l_iff(self.expr_tree(stat[0]), self.expr_tree(stat[2]))
                if stat[1] == '=>':
                    self.l_if(self.expr_tree(stat[0]), self.expr_tree(stat[2]))
            else: # otherwise we assume it is an expression constrained to be true
                self.l_ist(self.expr_tree(stat))
    
    # get the result of an expression in wombley
    def expr_tree(self, toks):
        if len(toks) == 1:
            return toks[0]
        else:
            if toks[0][0] == '~':
                return n(self.expr_tree(toks[1]))
            if toks[0][0] == '&':
                return self.all_cnf(*[self.expr_tree(i) for i in toks[1:]])
            if toks[0][0] == '|':
                return self.any_cnf(*[self.expr_tree(i) for i in toks[1:]])
            if toks[0][0] == '^':
                return self.xor_cnf(self.expr_tree(toks[1]), self.expr_tree(toks[2]))
            # if builtins fail, attempt macro lookup
            print(self.macros[toks[0][0]])
        assert False # fail if we can't figure out this expression



