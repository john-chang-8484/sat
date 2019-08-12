from makecnf import makecnf, parse_result, solve
from cnfutil import n, Clauses, deparen
from field_util import at, import_field_macros_to, set_dw


""" find cyclic solutions for the rule 110 CA
cool values for (duration, width):
    (21, 14)
    (12, 14)
    (11, 21)
    (8, 8)
"""


duration = 13
width = 20
set_dw(duration, width) # set the duration and width in field_util


def main():
    c = Clauses()
    
    ######### Macro Definitions ##########
    
    import_field_macros_to(c)
    c.defmacro('r110', ['p', 'q', 'r'], '(| (& q (~ p)) (^ q r))')
    
    ###### End of Macro Definitions ######
    
    ############ Constraints #############
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


