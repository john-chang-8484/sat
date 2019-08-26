from makecnf import makecnf, parse_result, solve
from cnfutil import n, Clauses, deparen
from field_util import at, import_field_macros_to, set_dw
from numbers import import_number_macros_to, def_rom


width = 14
duration = 21
set_dw(duration, width) # set the duration and width in field_util


def main():
    c = Clauses()
    
    ######### Macro Definitions ##########

    import_number_macros_to(c)
    #import_field_macros_to(c)
    c.addmacro('data1', def_rom([[1, 0, 0, 0], [0, 2, 0, 0], [1, 1, 0, 0], [0, 0, 1, 0]]))
    
    ###### End of Macro Definitions ######
    
    ############ Constraints #############
    #c.run('(l= (list x0 x1) (defnum x 2))')
    #c.run('x0 = 1')
    #c.run('x1 = 1')
    #c.run('(l= (list a b c d) (data1 (num x))))')
    c.run('(l= (list x0 x1 x2) (cnum x 3 1))')
    #c.run('(l= (list x0 x1 x2) (list 1 0 0))')
    c.run('(l= (list z0 z1 z2) (defnum z 3))')
    c.run('(l= (list z0 z1 z2) (list 1 1 1))')
    c.run('(l= (list a0 a1 a2) (+ (num x) (num z)))')
    

    solution = solve(c.get_clauses())
    if not solution:
        print('UNSAT')
    else:
        print('SAT')
        for k in solution:
            if '~' not in k:
                print(k, solution[k])
    

if __name__ == '__main__':
    main()


