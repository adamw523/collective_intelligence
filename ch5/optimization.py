import time
import random
import math

people = [('Saymour', 'BOS'),
        ('Franny', 'DAL'),
        ('Zooey', 'CAK'),
        ('Walt', 'MIA'),
        ('Buddy', 'ORD'),
        ('Les', 'OMA')]

# LaGuardia airport in New York
destination = 'LGA'

flights = {}
for line in file('schedule.txt'):
    origin, dest, depart, arrive, price = line.strip().split(',')
    flights.setdefault((origin, dest), [])

    # add details to the list of possible flights
    flights[(origin, dest)].append((depart, arrive, int(price)))

def getminutes(t):
    x = time.strptime(t, '%H:%M')
    return x[3] * 60 + x[4]

def printschedule(r):
    for d in range(0, len(r) / 2):
        name = people[d][0]
        origin = people[d][1]
        out = flights[(origin, destination)][r[2 * d]]
        ret = flights[(destination, origin)][r[2 * d + 1]]
        print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (name, origin,
                out[0], out[1], out[2], ret[0], ret[1], ret[2])

def schedulecost(sol):
    totalprice = 0
    latestarrival = 0
    earliestdep = 24 * 60
    # print 'sol', sol

    for d in range(len(sol) / 2):
        # get the inboutnd and outbound flights
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[2 * d])]
        returnf = flights[(destination, origin)][int(sol[2 * d + 1])]
        # total price is the price of all outbound and return flights
        totalprice += outbound[2]
        totalprice += returnf[2]

        # track the latest arrival and earliest departure
        if latestarrival < getminutes(outbound[1]):
            latestarrival = getminutes(outbound[1])
        if earliestdep > getminutes(returnf[0]):
            earliestdep = getminutes(returnf[0])

    # every person must wait at the airport until the latest person arrives
    # they also must arrive at the same time and wait for their flighs
    totalwait = 0
    for d in range(len(sol) / 2):
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[2 * d])]
        returnf = flights[(destination, origin)][int(sol[2 * d + 1])]
        totalwait += latestarrival - getminutes(outbound[1])
        totalwait += getminutes(returnf[0]) - earliestdep

    # an extra $50 for an extra day of car rental
    if latestarrival < earliestdep: totalprice += 50

    return totalprice + totalwait

def randomoptimize(domain, costf):
    best = 999999999
    bestr = None
    for i in range(1000):
        # crate a random solution
        r = [random.randint(domain[i][0], domain[i][1])
                for i in range(len(domain))]
        # get the cost
        cost = costf(r)

        # compare it to the best one so far
        if cost < best:
            best = cost
            bestr = r

    return bestr

def hillclimb(domain, costf):
    # create a random solution
    sol = [random.randint(domain[i][0], domain[i][1])
            for i in range(len(domain))]

    # main loop
    while 1:
        # create list of neighboring solutions
        neighbors = []
        for j in range(len(domain)):
            # one way in each direction
            if sol[j] > domain[j][0]:
                neighbors.append(sol[0:j] + [sol[j] - 1] + sol[j + 1:])
            if sol[j] < domain[j][1]:
                neighbors.append(sol[0:j] + [sol[j] + 1] + sol[j + 1:])

        # see what the best solution amongst the neighbors is
        current = costf(sol)
        best = current
        for j in range(len(neighbors)):
            cost = costf(neighbors[j])
            if cost < best:
                best = cost
                sol = neighbors[j]
        # if there's no improvement, then we've reached the top
        if best == current:
            break

    return sol

def annealingoptimize(domain, costf, T=10000.0, cool=0.95, step=1):
    # initialize the values randomly
    vec = [float(random.randint(domain[i][0], domain[i][1]))
        for i in range(len(domain))]

    while T > 0.1:
        # choose one of the indices
        i = random.randint(0, len(domain) - 1)

        # choose a direction to change it
        dir = random.randint(-step,step)

        #create a new list with one of the values changed
        vecb = vec[:]
        vecb[i] += dir
        if vecb[i] < domain[i][0]: vecb[i] = domain[i][0]
        elif vecb[i] > domain[i][1]: vecb[i] = domain[i][1]

        # calculate the current cost and the new cost
        ea = costf(vec)
        eb = costf(vecb)
        p = pow(math.e, (-eb-ea) / T)

        # is it better or does it make the probability cutoff?
        if (eb < ea or random.random() < p):
            vec = vecb

        # decrease the termperature
        T = T * cool
    # return vec
    return [int(v) for v in vec]

def geneticoptimize(domain, costf, popsize=50, step=1,
        mutprob=0.2, elite=0.2, maxiter=100):
    # mutation operation
    def mutate(vec):
        i = random.randint(0, len(domain) - 1)
        if random.random() < 0.5 and vec[i] > domain[i][0]:
            return vec[0:i] + [vec[i] - step] + vec[i+1:]
        elif vec[i] < domain[i][1]:
            return vec[0:i] + [vec[i] + step] + vec[i+1:]

    # crossover operation
    def crossover(r1, r2):
        i = random.randint(1, len(domain) - 2)
        return r1[0:i] + r2[i:]

    # build the initial population
    pop = []
    for i in range(popsize):
        vec = [random.randint(domain[i][0], domain[i][1])
                for i in range(len(domain))]
        pop.append(vec)

    # how many winners from each generation?
    topelite = int(elite * popsize)

    # main loop
    # print 'pop', pop
    for i in range(maxiter):
        scores = [(costf(v), v) for v in pop]
        scores.sort()
        ranked = [v for (s,v) in scores]

        # start with the pure winners
        pop = ranked[0:topelite]

        # add mutated and bred forms of the winners
        while len(pop) < popsize:
            if random.random() < mutprob:
                # mutation
                c = random.randint(0, topelite)
                pop.append(mutate(ranked[c]))
            else:
                # crossover
                c1 = random.randint(0, topelite)
                c2 = random.randint(0, topelite)
                pop.append(crossover(ranked[c1], ranked[c2]))

        # print current best score
        print scores[0][0]

    return scores[0][1]




