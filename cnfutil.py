from pyparsing import *


# define the grammar
identifier = Word(alphas+'&^|~_=<>+-', alphanums+'&^|~_=<>+-')
expr = Forward()
parens = Suppress(Literal('(')) + ZeroOrMore(expr) + Suppress(Literal(')'))
expr <<= Group(parens | identifier | pyparsing_common.integer)
constr_op = Literal('=>') | Literal('=')
constr = Group(expr + constr_op + expr)
grammar = ZeroOrMore(constr | expr)



def n(var):
    """ Logically negates a variable. """
    if var[0] == '~':
        return var[1:]
    else:
        return '~' + var


def replace(nlist, s, x):
    """ recursively replace all occurrences of a string s in
        a nested list of strings with x
    """
    if nlist == s:
        return x
    if isinstance(nlist, list):
        return [replace(sub, s, x) for sub in nlist]
    return nlist


def deparen(l):
    """ strip away all layers of enclosing lists
        this function is very useful when defining custom macros
    """
    if isinstance(l, list) and len(l) == 1:
        return deparen(l[0])
    return l


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
        """ each clause is a list of variable names
            ~ preceding a variable name means negation
            variables can generally be arbitrary strings, except the '~' character is reserved
        """
        self.macros = {}  # dict of macros for this Clauses obj's language
        """ a macro is stored in this dict under its name
            macros take parsed code as input, and yield "parsed" output
        """
        self.variables = {} # variables defined by various macros
    def junkvar(self):
        Clauses.counter += 1
        return 'junk~%d' % Clauses.counter
    def ext(self, *args): # extend the clauses list by each argument clause
        self.clauses.extend(args)
    def join(self, cls): # join with another clauses object
        self.ext(*cls.clauses)
        self.macros.update(cls.macros)
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

    
    def run(self, prog):
        """ parse and run a program """
        tokens = grammar.parseString(prog).asList()
        for stat in tokens:
            if len(stat) == 3 and isinstance(stat[1], str): # check if this is a constr
                if stat[1] == '=':
                    self.l_iff(self.expr_tree(stat[0]), self.expr_tree(stat[2]))
                if stat[1] == '=>':
                    self.l_if(self.expr_tree(stat[0]), self.expr_tree(stat[2]))
            else: # otherwise we assume it is an expression constrained to be true
                self.l_ist(self.expr_tree(stat))
    
    def expr_tree(self, toks):
        """ get the result of an expression """
        if isinstance(toks, str):
            return toks
        elif isinstance(toks, int):
            return self.T if toks else self.F
        elif len(toks) == 1:
            return self.expr_tree(toks[0])
        else:
            whichfn = self.expr_tree(toks[0])
            if whichfn == '~':
                return n(self.expr_tree(toks[1]))
            if whichfn == '&':
                return self.all_cnf(*[self.expr_tree(i) for i in toks[1:]])
            if whichfn == '|':
                return self.any_cnf(*[self.expr_tree(i) for i in toks[1:]])
            if whichfn == '^':
                return self.xor_cnf(self.expr_tree(toks[1]), self.expr_tree(toks[2]))
            if whichfn == '=':
                return self.xor_cnf(n(self.expr_tree(toks[1])), self.expr_tree(toks[2]))
            if whichfn == '=>':
                return self.or_cnf(n(self.expr_tree(toks[1])), self.expr_tree(toks[2]))
            if whichfn == 'list':
                return ['list', *[self.expr_tree(i) for i in toks[1:]]]
            # if builtins fail, attempt macro lookup
            print(toks)
            return self.expr_tree( self.macros[whichfn](self, toks[1:]) )
        assert False # fail if we can't figure out this expression

    def addmacro(self, macroname, macrofn):
        """ macrofn is an arbitrary function that takes in the parsed grammar
            in order to produce the resulting code (parsed) to evaluate
        """
        self.macros[macroname] = macrofn

    def defmacro(self, macroname, macroparams, macro):
        """ Define a macro that essentially just works like a function.
            More customized macros are defined using addmacro.
        """
        def the_macro(c, args):
            assert len(args) == len(macroparams)
            ans = expr.parseString(macro).asList()
            for i, param in enumerate(macroparams):
                ans = replace(ans, param, args[i]) # replace params with the actual arguments
            return ans
        self.addmacro(macroname, the_macro)


