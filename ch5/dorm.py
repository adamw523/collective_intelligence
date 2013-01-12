import random
import math

# the dorms, each of which has two available spaces
dorms = ['Zeus', 'Athena', 'Hercules', 'Bacchus', 'Pluto']

# people along with their first and second choices
prefs = [('Toby', ('Bacchus', 'Hercules')),
        ('Steve', ('Zeus', 'Pluto')),
        ('Andrea', ('Athena', 'Zeus')),
        ('Sarah', ('Zeus', 'Pluto')),
        ('Dave', ('Athena', 'Bacchus')),
        ('Jeff', ('Hercules', 'Pluto')),
        ('Fred', ('Pluto', 'Athena')),
        ('Suzie', ('Bacchus', 'Hercules')),
        ('Laura', ('Bacchus', 'Hercules')),
        ('Neil', ('Hercules', 'Athena'))]

# [(0, 9), (0,8), (0,7), (0,6), ..., (0,0)]
domain = [(0, (len(dorms) * 2) - i - 1) for i in
        range(0, len(dorms) * 2)]

def printsolution(vec):
    slots = []
    # create two slots for each dorm
    for i in range(len(dorms)): slots += [i,i]

    # loop over each students assignment
    for i in range(len(vec)):
        x = int(vec[i])

        # choose the slot from the remaining ones
        dorm = dorms[slots[x]]
        # show the student and assigned dorm
        print prefs[i][0], dorm
        # remove this slot
        del slots[x]

def dormcost(vec):
    # print
    cost = 0
    # create a list of slots
    slots = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]

    # loop over each student
    for i in range(len(vec)):
        x = int(vec[i])
        dorm = dorms[slots[x]]
        pref = prefs[i][1]

        # frist choice costs 0, second choice costs 1
        # not in list costs 3
        if pref[0] == dorm: cost += 0
        elif pref[1] == dorm: cost += 1
        else: cost += 3
        # print pref[0], '\t', pref[1], '\t', dorm, '\t', cost

        # remove selected slot
        del slots[x]

    return cost

