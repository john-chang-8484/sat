from makecnf import makecnf, parse_result, solve
from cnfutil import n, Clauses


width = 14
duration = 12


def deparen(l):
    """ strip away all layers of enclosing lists """
    if isinstance(l, list) and len(l) == 1:
        return deparen(l[0])
    return l


def indexify(nlist, ind):
    """ put indices on all variables with trailing underscores
        assumes the only mutable elements of nlist are lists
        makes a new copy for indexified nlist
    """
    if isinstance(nlist, list):
        return [indexify(sub, ind) for sub in nlist]
    if isinstance(nlist, str) and nlist[-1] == '_':
        return nlist + ind
    return nlist

def at(v, t, x):
    """ value of a field at some location in space """
    return v + '_%d_%d' % (t % duration, x % width)

def pos(v):
    """ get the position in space of some field variable """
    return tuple(map(int, v.split('_')[1:]))

def nm(v):
    """ get the field name of some field variable """
    return v.split('_')[0]

def right(v):
    """ returns the field variable just right of v """
    name, (t, x) = nm(v), pos(v)
    return at(name, t, x + 1)

def left(v):
    """ returns the field variable just left of v """
    name, (t, x) = nm(v), pos(v)
    return at(name, t, x - 1)

def forward(v):
    """ returns the field variable just futurewards of v """
    name, (t, x) = nm(v), pos(v)
    return at(name, t + 1, x )

def back(v):
    """ returns the field variable just pastwards of v """
    name, (t, x) = nm(v), pos(v)
    return at(name, t - 1, x )

def main():
    c = Clauses()
    
    ######### Macro Definitions ##########
    def mac_at(args):
        return at(deparen(args[0]), deparen(args[1]), deparen(args[2]))
    c.addmacro('at', mac_at)
    
    def forall(args):
        assert len(args) == 1
        ans = ['&']
        for t in range(0, duration):
            for x in range(0, width):
                ans.append(indexify(args[0], '%d_%d' % (t, x)))
        return ans
    c.addmacro('forall', forall)
    
    c.defmacro('r110', ['p', 'q', 'r'], '(| (& q (~ p)) (^ q r))')
    
    c.addmacro('forward', (lambda args: forward(args[0][0])))
    c.addmacro('back', (lambda args: back(args[0][0])))
    c.addmacro('left', (lambda args: left(args[0][0])))
    c.addmacro('right', (lambda args: right(args[0][0])))
    
    ###### End of Macro Definitions ######
    
    c.run('(forall (= (forward cell_) (r110 (left cell_) cell_ (right cell_))))')
    c.run('(at cell 0 0)')
    # c.print_clauses()

    solution = solve(c.get_clauses())
    if not solution:
        print('UNSAT')
    else:
        print('SAT')
        #print(solution)
        for t in range(0, duration):
            line = '| '
            for x in range(0, width):
                line += '# ' if solution[at('cell', t, x)] else '  '
            print(line + '|')
    

if __name__ == '__main__':
    main()


