from makecnf import makecnf, parse_result, solve
from cnfutil import n, Clauses


prog = """
a = b
~a = c
c
(| c b)
d = (& c b)

"""


def main():
    c = Clauses()
    
    print(prog)
    c.run(prog)
    c.print_clauses()

    solution = solve(c.get_clauses())
    if not solution:
        print('UNSAT')
    else:
        print('SAT')
        print(solution)
    

if __name__ == '__main__':
    main()


