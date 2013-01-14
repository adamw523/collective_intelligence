import re
import math
from pysqlite2 import dbapi2 as sqlite

def sampletrain(cl):
    cl.train('Nobody owns the water.', 'good')
    cl.train('the quick rabbit jumps fences', 'good')
    cl.train('make quick money at the online casino', 'bad')
    cl.train('the quick brown fox jumps', 'good')

def getwords(doc):
    splitter = re.compile('\\W*')
    # split the words by non-alpha characters
    words = [s.lower() for s in splitter.split(doc)
            if len(s) > 2 and len(s) < 20]

    # return the unique set of words only
    return dict([(w,1) for w in words])

class classifier:
    def __init__(self, getfeatures, filename=None):
        # counts of feature / category combinations
        self.fc = {}
        # counts of documents in each category
        self.cc = {}
        self.getfeatures = getfeatures

    def setdb(self, dbfile):
        self.con = sqlite.connect(dbfile)
        self.con.execute('create table if not exists \
                fc(feature, category, count)')
        self.con.execute('create table if not exists \
                cc(category, count)')

    # increase the count of a feature / category pair
    def incf(self, f, cat):
        """
        self.fc.setdefault(f, {})
        self.fc[f].setdefault(cat, 0)
        self.fc[f][cat] += 1
        """
        count = self.fcount(f, cat)
        if count == 0:
            self.con.execute("insert into fc values('%s', '%s', 1)" %
                    (f, cat))
        else:
            self.con.execute("update fc set count = %d where feature = '%s' and \
                    category = '%s'" % (count + 1, f, cat))

    # increse the count of a category
    def incc(self, cat):
        """
        self.cc.setdefault(cat, 0)
        self.cc[cat] += 1
        """
        count = self.catcount(cat)
        if count == 0:
            self.con.execute("insert into cc values ('%s', 1)" % (cat))
        else:
            self.con.execute("update cc set count = %d where \
                    category = '%s'" % (count + 1, cat))

    # the number of times a feature has appeard in a category
    def fcount(self, f, cat):
        """
        if f in self.fc and cat in self.fc[f]:
            return float(self.fc[f][cat])
        return 0.0
        """
        res = self.con.execute('select count from fc where feature = "%s" and \
                category = "%s"' % (f, cat)).fetchone()
        if res == None: return 0
        else: return float(res[0])

    # the number of items in a category
    def catcount(self, cat):
        """
        if cat in self.cc:
            return float(self.cc[cat])
        return 0
        """
        res = self.con.execute('select count from cc where category = "%s"' %
                (cat)).fetchone()
        if res == None: return 0
        else: return float(res[0])

    # the total number of items
    def totalcount(self):
        """
        return sum(self.cc.values())
        """
        res = self.con.execute('select sum(count) from cc').fetchone()
        if res == None: return 0
        return res[0]

    # the features
    def features(self):
        res = self.con.execute('select feature from fc GROUP BY feature')
        return [f[0] for f in res]

    # the list of all categoreis
    def categories(self):
        """
        return self.cc.keys()
        """
        cur = self.con.execute('select category from cc')
        return [d[0] for d in cur]

    def train(self, item, cat):
        features = self.getfeatures(item)
        # incremet the count for every feature with this category
        for f in features:
            self.incf(f, cat)

        # increment the count for this category
        self.incc(cat)

        self.con.commit()

    def fprob(self, f, cat):
        if self.catcount(cat) == 0: return 0
        # the total number of times this feature appeared in this
        # category divided by the total number of items in this category
        return self.fcount(f, cat) / self.catcount(cat)

    def weightedprob(self, f, cat, prf, weight=1.0, ap=0.5):
        # ap = assumed probability
        # prf = basic probability function

        # calculate current probability
        basicprob = prf(f, cat)

        # count the number of times this feature has appeared
        # in all categories
        totals = sum([self.fcount(f,c) for c in self.categories()])

        # calculate the weighted average
        bp = ((weight * ap) + (totals * basicprob)) / (weight + totals)
        return bp

    def printtable(self):
        # Print a table of the categories, features and their probabilities
        print '             ',
        for category in self.categories():
            print '{0:10}'.format(category),
        print

        for feature in self.features():
            print '{0:14}'.format(feature),
            for category in self.categories():
                print '{0:.1f}       '.format(self.fprob(feature, category)),
            print

class naivebayes(classifier):
    def __init__(self, getfeatures):
        classifier.__init__(self, getfeatures)
        self.thresholds = {}

    def docprob(self, item, cat):
        features = self.getfeatures(item)

        # multiply the probabilities of all the features together
        p = 1
        for f in features:
            p *= self.weightedprob(f, cat, self.fprob)

        return p

    def prob(self, item, cat):
        catprob = self.catcount(cat) / self.totalcount()
        docprob = self.docprob(item, cat)

        return docprob * catprob

    def setthreshold(self, cat, t):
        self.thresholds[cat] = t

    def getthreashold(self, cat):
        if cat not in self.thresholds: return 1.0
        return self.thresholds[cat]

    def classify(self, item, default=None):
        probs = {}

        # find the category with the highest probability
        max = 0.0
        for cat in self.categories():
            probs[cat] = self.prob(item, cat)
            if probs[cat] > max:
                max = probs[cat]
                best = cat

        # make sure the probability exceeds threshold * next best
        for cat in probs:
            if probs[cat] * self.getthreashold(best) > probs[best]: return default

        return best

class fisherclassifier(classifier):
    def __init__(self, getfeatures):
        classifier.__init__(self, getfeatures)
        self.minimums = {}

    def setminimum(self, cat, min):
        self.minimums[cat] = min

    def getminimum(self, cat):
        if cat not in self.minimums: return 0
        return self.minimums[cat]

    def cprob(self, f, cat):
        # the frequency of this feature in this category
        clf = self.fprob(f, cat)
        if clf == 0: return 0

        # the frequency of this feature in all of the categories
        freqsum = sum([self.fprob(f, c) for c in self.categories()])

        # the probability is the frequency in this category divided by
        # the overal frequency
        p = clf / (freqsum)

        return p

    def fisherprob(self, item, cat):
        # multiply all the probabilities together
        p = 1
        features = self.getfeatures(item)
        for f in features:
            p *= (self.weightedprob(f, cat, self.cprob))

        # take the natural log and multiply it by -2
        fscore = -2 * math.log(p)

        # use the inverse chi2 function to get a probability
        return self.invchi2(fscore, len(features) * 2)

    def invchi2(self, chi, df):
        m = chi / 2.0
        sum = term = math.exp(-m)
        for i in range(1, df // 2):
            term *= m / i
            sum += term

        return min(sum, 1.0)

    def classify(self, item, default=None):
        # loop through looking for the best result
        best = default
        max = 0.0
        for c in self.categories():
            p = self.fisherprob(item, c)
            # make sure it exceeds its minimum
            if p > self.getminimum(c) and p > max:
                best = c
                max = p
        return best










