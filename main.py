from makecnf import makecnf, parse_result, solve
from cnfutil import n, Clauses, deparen
from field_util import at, import_field_macros_to, set_dw


width = 14
duration = 21
set_dw(duration, width) # set the duration and width in field_util


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


def num(c, args):
    return c.variables[deparen(args[0])]


def main():
    c = Clauses()
    
    ######### Macro Definitions ##########
    
    c.addmacro('l=', list_eq)
    c.addmacro('defnum', defnum)
    c.addmacro('num', num)
    
    #import_field_macros_to(c)
    c.addmacro('data1', def_rom([[1, 0, 0, 0], [0, 2, 0, 0], [1, 1, 0, 0], [0, 0, 1, 0]]))
    print('!!!')
    c.run('(l= (list x0 x1) (defnum x 2))')
    print('!!!')
    c.run('x0 = 1')
    c.run('x1 = 1')
    c.run('(l= (list a b c d) (data1 (num x))))')
    
    ###### End of Macro Definitions ######
    
    ############ Constraints #############
    

    solution = solve(c.get_clauses())
    if not solution:
        print('UNSAT')
    else:
        print('SAT')
        for k in solution:
            print(k, solution[k])
    

if __name__ == '__main__':
    main()


