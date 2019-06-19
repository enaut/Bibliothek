#!/bin/env python3

def extend(code):
    v = code.split(' ')
    res = []
    for m in v:
        if len(res) > 0:
            if '.' in m:
                res += [res[-1] + ' ' + m.split('.')[0]]
                res += [res[-2] + ' ' + m]
                if len(m.split('.')) > 2:
                    res += [res[-3] + ' ' + '.'.join(m.split('.')[:2])]
            else:
                res += [res[-1] + ' ' + m]
        else:
            res=[m]
    return res

print(extend("DE 3.1.5"))
print(extend("DE 3.1"))
print(extend("J LIT 12"))
