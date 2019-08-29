from makecnf import makecnf, parse_result, solve
from cnfutil import n, Clauses, deparen
from field_util import at, import_field_macros_to, set_dims
from numbers import import_number_macros_to, def_rom


width = 14
duration = 21
set_dims((duration, width)) # set the duration and width in field_util


def main():
    c = Clauses()
    
    ######### Macro Definitions ##########

    import_number_macros_to(c)
    #import_field_macros_to(c)
    c.addmacro('data1', def_rom([[1, 0, 0, 0], [0, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 0], [1, 1, 1, 1], [0, 0, 0, 0], [1, 1, 1, 0], [0, 1, 1, 1]]))
    
    ###### End of Macro Definitions ######
    
    ############ Constraints #############
    #c.run('(l= (list x0 x1) (defnum x 2))')
    #c.run('x0 = 1')
    #c.run('x1 = 1')
    #c.run('(l= (list a b c d) (data1 (num x))))')
    c.run('(l= (list x0 x1 x2) (cnum x 3 1))')
    c.run('(l= (list y0 y1 y2) (cnum y 3 3))')
    c.run('(l= (list a0 a1 a2 a3) (data1 (+ (num x) (num y))))')
    

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


