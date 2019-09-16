from cnfutil import n, Clauses, deparen


def exactly_one(c, args):
    params = [deparen(arg) for arg in args]
    if len(params) == 0:
        return c.F
    if len(params) == 1:
        return params[0]
    else:
        hlf = len(params) // 2
        return ['|',
            ['&', ['e1', *params[:hlf]], ['~', ['|', *params[hlf:]]]],
            ['&', ['e1', *params[hlf:]], ['~', ['|', *params[:hlf]]]] ]


def truth(c, args):
    for arg in args:
        c.expr_tree(arg)
    return c.T


def import_genutil_to(c):
    c.addmacro('e1', exactly_one)
    c.addmacro('truth', truth)

