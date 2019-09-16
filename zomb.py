from makecnf import makecnf, parse_result, solve
from cnfutil import n, Clauses, deparen
from field_util import at, import_field_macros_to, set_dims
from numbers import import_number_macros_to, def_rom
from genutil import import_genutil_to


width = 4
height = 4
duration = 4
set_dims((duration, width, height)) # set the duration and width in field_util




def main():
    c = Clauses()
    
    ######### Macro Definitions ##########

    import_number_macros_to(c)
    import_field_macros_to(c)
    import_genutil_to(c)
    
    c.addmacro('instrs', def_rom([[0,0,0], [1,0,1], [0,1,0], [1,1,1]]))
    
    
    # define a macro to convert 2 bits to a space direction
    c.defmacro('sdir', ['cell', 'd1', 'd2'],
        '(| (& (~ d1) (~ d2) (right cell))'
        '   (& (~ d1)    d2  (up    cell))'
        '   (&    d1  (~ d2) (left  cell))'
        '   (&    d1     d2  (down  cell)))' )
    
    # define a macro to convert 1 bit to a time direction
    c.defmacro('tdir', ['cell', 'd0'],
        '(| (& (~ d0) (back    cell))'
        '   (&    d0  (forward cell)))')
    
    # define a macro to convert 3 bits to a spacetime direction
    c.defmacro('stdir', ['cell', 'd0', 'd1', 'd2'],
        '(| (& (~ d0) (~ d1) (~ d2) (back    (right cell)))'
        '   (& (~ d0) (~ d1)    d2  (back    (up    cell)))'
        '   (& (~ d0)    d1  (~ d2) (back    (left  cell)))'
        '   (& (~ d0)    d1     d2  (back    (down  cell)))'
        '   (&    d1  (~ d1) (~ d2) (forward (right cell)))'
        '   (&    d1  (~ d1)    d2  (forward (up    cell)))'
        '   (&    d1     d1  (~ d2) (forward (left  cell)))'
        '   (&    d1     d1     d2  (forward (down  cell))))' )
    
    ###### End of Macro Definitions ######
    
    # define constants:
    c.run('(cnum one 2 1)')
    
    ############ Constraints #############
    
    c.run('(forall (=> isplasma_ (&'
        '       (sdir (forward isplasma_) d1_ d2_)'
        '       (= d1_ (sdir (forward d1_) d1_ d2_))'
        '       (= d2_ (sdir (forward d2_) d1_ d2_))'
        ')))')
    
    
    c.run('(forall (truth (defnum pc_ 2)))')
    c.run('(forall (=> iszomb (|'
        '   (& (<> (instrs (num pc_)) 0)' # no reverse
        '      (l= (+ (num pc_) (num one)) (stdir pc_ d0_ (<> (instrs (num pc_)) 1) (<> (instrs (num pc_)) 2)) )'
        ')))')
    #c.run('(l= (num pc_0_0_0) (list number0 number1))')
    c.run('isplasma_0_0_0')

    ######### End of Constraints #########

    solution = solve(c.get_clauses())
    if not solution:
        print('UNSAT')
    else:
        print('SAT')
        for k in solution:
            if '~' not in k:
                print(k, solution[k])
        for t in range(duration):
            print('\n')
            for y in range(height):
                line = '| '
                for x in range(width):
                    line += '# ' if solution[at('isplasma', (t, x, y))] else '  '
                print(line + '|')
    

if __name__ == '__main__':
    main()


