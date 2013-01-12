import feedparser
import re
import nmf
import urllib2
from numpy import *

tickers = ['YHOO', 'AVP', 'BIIB', 'BP', 'CL', 'CVX',
        'EXPE', 'GOOG', 'PG', 'XOM', 'AMGN', 'MSFT', 'AAPL']

shortest = 300
prices = {}
dates = None

for t in tickers:
    # open the URL
    url = 'http://ichart.finance.yahoo.com/table.csv?' + \
            's=%s&d=11&e=31&f=2012&g=d&a=0&b=1&c=2006' % t + \
            '&ignore=.csv'
    rows = urllib2.urlopen(url).readlines()

    # extract the volume field from eery line
    prices[t] = [float(r.split(',')[5]) for r in rows[1:] if r.strip() != '']
    if len(prices[t]) < shortest: shortest = len(prices[t])
    if not dates:
        dates = [r.split(',')[0] for r in rows[1:] if r.strip() != '']

l1 = [[prices[tickers[i]][j]
    for i in range(len(tickers))]
    for j in range(shortest)]

w, h = nmf.factorize(matrix(l1), pc=5)

print h
print w

# loop over all the features
for i in range(shape(h)[0]):
    print "Feature %d" % i
    # get the top stocks for this feature
    ol = [(h[i, j], tickers[j]) for j in range(shape(h)[1])]
    ol.sort()
    ol.reverse()
    for j in range(12):
        print ol[j]
    print

    # show the top dates for this feature
    porder = [(w[d, i], d) for d in range(300)]
    porder.sort()
    porder.reverse()
    print [(p[0], dates[p[1]]) for p in porder[0:3]]
    print

