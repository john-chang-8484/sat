from cnfutil import n, Clauses, deparen


def binrep(x, n):
    """ represent number x as binary list of length n """
    return [x % 2**(i+1) // 2**i  for i in range(0, n)]

def acc(c, data, idx, m):
    """ access the ith row of data, mth bit
        idx is a list of variable names,
        m is an int, data is a 2d array of 0, 1
        c is a clauses object
    """
    assert len(data) <= 2**len(idx)
    ans = c.junkvar()
    for j, dat in enumerate(data):
        jbits = binrep(j, len(idx))
        vnames = [(v if bit else n(v)) for bit, v in zip(jbits, idx)]
        c.run('(& %s) => %s' % (
            ' '.join(vnames),
            (ans if dat[m] else n(ans)) ))
    return ans

def def_rom(data):
    def rom_acc_macro(c, args):
        idx = c.expr_tree(args[0])[1:]
        return ['list', *[acc(c, data, idx, m) for m in range(0, len(data[0]))]]
    return rom_acc_macro


def list_eq(c, args):
    ans = ['&']
    for l1v, l2v in zip(c.expr_tree(args[0])[1:], c.expr_tree(args[1])[1:]):
        ans.append(['=', l1v, l2v])
    return ans


def defnum(c, args):
    """ usage: (defnum, <name>, <number of bits>)
        to access the number: (num <name>)
    """
    name, nbits = deparen(args[0]), deparen(args[1])
    ans = ['list', *[c.junkvar() for i in range(nbits)]]
    c.variables[name] = ans
    return ans


def cnum(c, args):
    """ usage: (cnum, <name>, <number of bits>, <value>)
        defines a constant number
    """
    name, nbits, val = deparen(args[0]), deparen(args[1]), deparen(args[2])
    ans = ['list', *binrep(val, nbits)]
    c.variables[name] = ans
    return ans


def num(c, args):
    return c.variables[deparen(args[0])]


def addnums(c, args):
    num_a = c.expr_tree(args[0])[1:] # assume these are lists
    num_b = c.expr_tree(args[1])[1:] # assume these are lists
    ans = ['list', ['^', num_a[0], num_b[0]]]
    carries = [c.junkvar()]
    c.l_iff(carries[0], c.expr_tree(['&', num_a[0], num_b[0]]))
    for i in range(1, len(num_a)):
        ans.append(['add_o', num_a[i], num_b[i], carries[-1]])
        carries.append(c.junkvar())
        c.l_iff(carries[-1], c.expr_tree(['add_c', num_a[i], num_b[i], carries[-2]]))
    return ans


def index(c, args):
    lst = c.expr_tree(args[0])
    i = deparen(args[1])
    return lst[i + 1]

def slice_macro(c, args):
    lst = c.expr_tree(args[0])
    i = deparen(args[1])
    j = deparen(args[2])
    return lst[i+1:j+1]


def import_number_macros_to(c):
    c.addmacro('l=', list_eq)
    c.addmacro('<>', index)
    c.addmacro('<->', slice_macro)
    c.addmacro('defnum', defnum)
    c.addmacro('cnum', cnum)
    c.addmacro('num', num)
    c.defmacro('add_o', ['a', 'b', 'c'], '(^ c (^ a b))') # full 1 bit adder output
    c.defmacro('add_c', ['a', 'b', 'c'], '(| (& a b) (& c (| a b)))') # full 1 bit adder carry
    c.addmacro('+', addnums)


