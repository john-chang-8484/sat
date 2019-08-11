from makecnf import makecnf, parse_result, solve
from cnfutil import n, Clauses


def indexify(nlist, ind):
    """ put indices on all variables with trailing underscores
        assumes the only mutable elements of nlist are lists
        makes a new copy for indexified nlist
    """
    if isinstance(nlist, list):
        return [indexify(sub, ind) for sub in nlist]
    if isinstance(nlist, str) and nlist[-1] == '_':
        return nlist + '~' + str(ind)
    return nlist


def main():
    c = Clauses()
    
    def forall(args):
        assert len(args) == 1
        return ['&', *[indexify(args[0], i) for i in range(0, 10)]]
    
    c.addmacro('forall', forall)
    #c.defmacro('and', ['a', 'b'], '(& a b)')
    c.run('(forall (& a_ b_))')
    c.print_clauses()

    solution = solve(c.get_clauses())
    if not solution:
        print('UNSAT')
    else:
        print('SAT')
        print(solution)
    

if __name__ == '__main__':
    main()


