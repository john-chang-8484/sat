from cnfutil import n, Clauses, deparen
from itertools import product

""" fields are defined by analogy with fields in physics:
        - they take on a value in every point in space
        - in this case, fields are binary: 0 or 1
    here are some useful functions for working with them
"""

dims = [1, 1] # width, duration


def suffix(pos):
    return ''.join(['_%d' % (pos[i] % dims[i]) for i in range(0, len(dims))])


def at(v, pos):
    """ value of a field at some location in space """
    return v + suffix(pos)

def ps(v):
    """ get the position in space of some field variable """
    return tuple(map(int, v.split('_')[1:]))

def nm(v):
    """ get the field name of some field variable """
    return v.split('_')[0]

def right(v):
    """ returns the field variable just right of v """
    name, (t, x) = nm(v), ps(v)[0:2]
    return at(name, (t, x + 1) + ps(v)[2:])

def left(v):
    """ returns the field variable just left of v """
    name, (t, x) = nm(v), ps(v)[0:2]
    return at(name, (t, x - 1) + ps(v)[2:])

def forward(v):
    """ returns the field variable just futurewards of v """
    name, t = nm(v), ps(v)[0]
    return at(name, (t + 1,) + ps(v)[1:])

def back(v):
    """ returns the field variable just pastwards of v """
    name, t = nm(v), ps(v)[0]
    return at(name, (t - 1,) + ps(v)[1:])

def indexify(nlist, ind):
    """ put indices on all variables with trailing underscores
        assumes the only mutable elements of nlist are lists
        makes a new copy for indexified nlist
    """
    if isinstance(nlist, list):
        return [indexify(sub, ind) for sub in nlist]
    if isinstance(nlist, str) and nlist[-1] == '_':
        return nlist[:-1] + ind
    return nlist

def import_field_macros_to(c):
    """ defines several field macros in the Clauses object c
        note: causes '_' to become a reserved character in variable names
    """
    def mac_at(c, args):
        return at(deparen(args[0]), [deparen(arg) for arg in args[1:]])
    c.addmacro('at', mac_at)
    
    def forall(c, args):
        assert len(args) == 1
        ans = ['&']
        for pos in product(*[range(dim) for dim in dims]):
            ans.append(indexify(args[0], suffix(pos)))
        return ans
    c.addmacro('forall', forall)
    
    c.addmacro('forward', (lambda c, args: forward(args[0][0])))
    c.addmacro('back', (lambda c, args: back(args[0][0])))
    c.addmacro('left', (lambda c, args: left(args[0][0])))
    c.addmacro('right', (lambda c, args: right(args[0][0])))


def set_dims(dimensions):
    """ allows client program to set the desired duration and width """
    global dims
    dims = dimensions



