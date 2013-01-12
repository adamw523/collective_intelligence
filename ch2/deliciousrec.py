from pydelicious import get_popular, get_userposts, get_urlposts
import time

def initalizeUserDict(tag, count = 5):
    user_dict = {}
    # get the top "count" copular posts
    for p1 in get_popular(tag = tag)[0:count]:
        # print p1
        # find all users who posted this
        for p2 in get_urlposts(p1['url']):
            user = p2['user']
            user_dict[user] = {}
    return user_dict

def fillItems(user_dict):
    all_items = {}
    # find links posted by all users
    for user in user_dict:
        print "user: %s" % user
        posts = []
        for i in range(3):
            try:
                posts = get_userposts(user)
                break
            except:
                print "failed user %s, retrying" % user
                time.sleep(4)

        # print "posts: ", posts
        if posts:
            for post in posts:
                url = post['url']
                user_dict[user][url] = 1.0
                all_items[url] = 1

    for ratings in user_dict.values():
        for item in all_items:
            if item not in ratings:
                ratings[item] = 0.0





