from cnfutil import n, Clauses, deparen

""" fields are defined by analogy with fields in physics:
        - they take on a value in every point in space
        - in this case, fields are binary: 0 or 1
    here are some useful functions for working with them
"""

width = 1
duration = 1



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

def import_field_macros_to(c):
    """ defines several field macros in the Clauses object c
        note: causes '_' to become a reserved character in variable names
    """
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
    
    c.addmacro('forward', (lambda args: forward(args[0][0])))
    c.addmacro('back', (lambda args: back(args[0][0])))
    c.addmacro('left', (lambda args: left(args[0][0])))
    c.addmacro('right', (lambda args: right(args[0][0])))


def set_dw(d, w):
    """ allows client program to set the desired duration and width """
    global duration
    global width
    duration, width = d, w



