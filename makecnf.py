import subprocess


def clause2str(clause, varmap):
    """ Convert a given clause to a string. """
    nums = []
    for v in clause:
        if v[0] == '~':
            nums.append(str(-varmap[v[1:]]))
        else:
            nums.append(str(varmap[v]))
    nums.append('0')
    return ' '.join(nums)


# function to make a cnf string from clauses
def makecnf(clauses):
    """ Make a cnf string from clauses """
    varmap = {}
    counter = 1
    for clause in clauses:
        for var in clause:
            varnm = ( var[1:] if var[0] == '~' else var )
            if varnm not in varmap:
                varmap[varnm] = counter
                counter += 1
    lines = ['p cnf %d %d' % (len(varmap), len(clauses))]
    for clause in clauses:
        lines.append(clause2str(clause, varmap))
    return '\n'.join(lines), varmap


def parse_result(result):
    """ Get the result and put it into a dictionary. """
    lines = result.split('\n')
    if [line for line in lines if (len(line) > 0 and line[0] == 's')][0][:3] == 's U':
        return False # unsatisfiable
    big_line = ''.join([line[1:] for line in lines if (len(line) > 0 and line[0] == 'v')])
    numarray = [0] + big_line.split()
    return [int(i) > 0 for i in numarray]


def solve(clauses):
    """ Run delegate sat solving to lingeling, get results. """
    cnf_str, varmap = makecnf(clauses)
    with open('temporary_cnf.cnf', 'w') as f:
        f.write(cnf_str)
    print('file written. running lingeling...')
    result = subprocess.run( # TODO: make this not be hardcoded
        ['../sat/lingeling-bcj-78ebb86-180517/lingeling', 'temporary_cnf.cnf'], stdout=subprocess.PIPE
    ).stdout.decode('utf-8')
    var_values = parse_result(result)
    if not var_values:
        return False
    ans = {}
    for var in varmap:
        ans[var] = var_values[varmap[var]]
    return ans



