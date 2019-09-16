from makecnf import makecnf, parse_result, solve
from cnfutil import n, Clauses, deparen
from numbers import import_number_macros_to, def_rom
from genutil import import_genutil_to


tile_data = [ #0                   #1                   #2
              "MS","FS","FC","MH", "MS","FH","FC","MS", "MD","FH","FD","MS",
              "MD","FC","FC","MH", "MC","FC","FD","MD", "MD","FS","FH","MS",
              "MH","FS","FH","MC", "MD","FD","FH","MH", "MH","FD","FC","MC"
            ] #6                   #7                   #8


suit2num = {'H':0, 'C':1, 'D':2, 'S':3}
rot2dir = [0, 1, 1, 0]


tiles = []
for i in range(9):
    tile = []
    for j in range(4):
        tile.append(suit2num[tile_data[j + 4*i][1]])
    tiles.append(tile)


def main():
    c = Clauses()
    
    ######### Macro Definitions ##########

    import_number_macros_to(c)
    import_genutil_to(c)
    
    
    ###### End of Macro Definitions ######
    
    ############ Constraints #############
    for x in range(3):
        for y in range(3):
            pieceargs = ['p%d_%d_%d' % (piece, x, y) for piece in range(9)]
            c.run('(e1 %s)' % ' '.join(pieceargs))
    for piece in range(9):
        pieceargs = ['p%d_%d_%d' % (piece, x, y) for x in range(3) for y in range(3)]
        c.run('(e1 %s)' % ' '.join(pieceargs))
    
    for x in range(3):
        for y in range(3):
            rotargs = ['rot%d_%d_%d' % (rot, x, y) for rot in range(4)]
            c.run('(e1 %s)' % ' '.join(rotargs))
    
    for x in range(3):
        for yy in range(2):
            suitargs = ['suit%d_h%d_%d' % (suit, x, yy) for suit in range(4)]
            dirarg = 'dir_h%d_%d' % (x, yy)
            c.run('(e1 %s)' % ' '.join(suitargs))
            for rot in range(4):
                c.run('rot%d_%d_%d => (= %s %s)' %
                    ( rot, x, yy,
                      dirarg, rot2dir[(rot + 2) % 4] ) )
                c.run('rot%d_%d_%d => (^ %s %s)' %
                    ( rot, x, yy+1,
                      dirarg, rot2dir[(rot + 0) % 4] ) )
                for piece in range(9):
                    c.run('(& p%d_%d_%d rot%d_%d_%d) => %s' %
                        ( piece, x, yy,
                          rot, x, yy,
                          suitargs[tiles[piece][(rot + 2) % 4]] ) )
                    c.run('(& p%d_%d_%d rot%d_%d_%d) => %s' %
                        ( piece, x, yy+1,
                          rot, x, yy+1,
                          suitargs[tiles[piece][(rot + 0) % 4]] ) )
    
    for xx in range(2):
        for y in range(3):
            suitargs = ['suit%d_v%d_%d' % (suit, xx, y) for suit in range(4)]
            dirarg = 'dir_v%d_%d' % (xx, y)
            c.run('(e1 %s)' % ' '.join(suitargs))
            for rot in range(4):
                c.run('rot%d_%d_%d => (= %s %s)' %
                    ( rot, xx, y,
                      dirarg, rot2dir[(rot + 1) % 4] ) )
                c.run('rot%d_%d_%d => (^ %s %s)' %
                    ( rot, xx+1, y,
                      dirarg, rot2dir[(rot + 3) % 4] ) )
                for piece in range(9):
                    c.run('(& p%d_%d_%d rot%d_%d_%d) => %s' %
                        ( piece, xx, y,
                          rot, xx, y,
                          suitargs[tiles[piece][(rot + 1) % 4]] ) )
                    c.run('(& p%d_%d_%d rot%d_%d_%d) => %s' %
                        ( piece, xx+1, y,
                          rot, xx+1, y,
                          suitargs[tiles[piece][(rot + 3) % 4]] ) )
    
    
    solution = solve(c.get_clauses())
    if not solution:
        print('UNSAT')
    else:
        print('SAT')
        #for k in solution:
        #    if '~' not in k:
        #        print(k, solution[k])
        for y in range(3):
            line = ''
            for x in range(3):
                for piece in range(9):
                    if solution['p%d_%d_%d' % (piece, x, y)]:
                        line += ' %d' % piece
            print(line)
        print('------------')
        for y in range(3):
            line = ''
            for x in range(3):
                for rot in range(4):
                    if solution['rot%d_%d_%d' % (rot, x, y)]:
                        line += ' %d' % rot
            print(line)

if __name__ == '__main__':
    main()


