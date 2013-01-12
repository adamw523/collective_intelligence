from math import sqrt

# A dictionary of movie critics and their ratings of a small # set of movies 

critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,  
            'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
            'The Night Listener': 3.0},
        'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
            'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
            'You, Me and Dupree': 3.5},
        'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
            'Superman Returns': 3.5, 'The Night Listener': 4.0},
        'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
            'The Night Listener': 4.5, 'Superman Returns': 4.0,
            'You, Me and Dupree': 2.5},
        'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
            'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
            'You, Me and Dupree': 2.0},
        'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
            'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
        'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}


def sim_distance(prefs, p1, p2):
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1

    # no ratings in common
    if len(si) == 0: return 0

    # add up the squares of all the differences
    sum_of_squares = sum([pow(prefs[p1][item] - prefs[p2][item], 2)
        for item in si])

    return 1 / (1 + sqrt(sum_of_squares))

def sim_pearson(prefs, p1, p2):
    # list of mutually rated items
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item] = 1

    n = len(si)

    if n == 0: return 0

    # add up all the preferences
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    # sum up the squares
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])

    # sum up the products
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    # Calculate Pearson score
    num = pSum - (sum1 * sum2 /n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if int(den) is 0: return 0

    r = num / den
    return r

def topMatches(prefs, person, n = 5, similarity = sim_pearson):
    # returns best matches for person from the prefs dictionary
    # number of results and similarity function are optional params
    scores = [(similarity(prefs, person, other), other)
                for other in prefs if other != person]

    scores.sort()
    scores.reverse()
    return scores[0:n]


def getRecommendations(prefs, person, similarity = sim_pearson):
    # gets recommendations for a person by using a weighted average
    # of every other users's rankings
    totals = {}
    simSums = {}
    for other in prefs:
        if other == person: continue
        sim = similarity(prefs, person, other)

        # ignore 0 or lower
        if sim <= 0: continue

        for item in prefs[other]:
            # only score movies person hasn't seen
            if item not in prefs[person] or prefs[person][item] == 0:
                # similarity * score
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim
                #sum of similarities
                simSums.setdefault(item, 0)
                simSums[item] += sim

    # create normalized list
    rankings = [(total / simSums[item], item) for 
            item, total in totals.items() ]

    rankings.sort()
    rankings.reverse()
    return rankings


def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})

            # flip item and person
            result[item][person] = prefs[person][item]
    return result


def calculateSimilarItems(prefs, n = 10):
    # create a dictonary of items showing which other items they 
    # are most like
    result = {}

    # invert the preference matrix to be item-centric
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        c += 1
        if c % 100 == 0: print "%d / %d" % (c, len(itemPrefs))
        # find the most similar items to this one
        scores = topMatches(itemPrefs, item, n = n, similarity = sim_distance)
        result[item] = scores
    return result

def getRecommendedItems(prefs, itemMatch, user):
    userRatings = prefs[user]
    scores = {}
    totalSim = {}

    # loop over items rated by this user
    for (item, rating) in userRatings.items():
        # lool pver items similar to this one
        for (similarity, item2) in itemMatch[item]:
            # ignore if this user has already rated this item
            if item2 in userRatings: continue

            # weighted sum of rating iimes similarity
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating

            # sum of all the similarities
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity

    # divide each total score by total weighting to get an average
    rankings = [(score / totalSim[item], item) for item, score in
            scores.items()]

    # return the rankings from hightest to lowest
    rankings.sort()
    rankings.reverse()
    return rankings


def loadMovieLens(path = 'ml-100k'):
    movies = {}

    # get movie titles
    for line in open(path + '/u.item'):
        (id, title) = line.split('|')[0:2]
        movies[id] = title

    # load data
    prefs = {}
    for line in open(path + '/u.data'):
        (user, movieid, rating, ts) = line.split('\t')
        prefs.setdefault(user, {})
        prefs[user][movies[movieid]] = float(rating)

    return prefs



