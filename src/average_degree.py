__author__ = 'tushar'
import os
import json
import Graph
import re
from email.utils import parsedate_tz,mktime_tz,formatdate
import pytz
import datetime
import time
import sys

dir = os.path.dirname(__file__)

infile=os.path.abspath(os.path.join(dir,'..',sys.argv[1]))
outfile=os.path.abspath(os.path.join(dir,'..',sys.argv[2]))

rolling_degree=[]
g={}
graph=Graph.Graph(g)
older_tweet=[]

class meanDegree(dict): #class to calculate average degree of vertices
    def __init__(self):
        self._total = 0.0
        self._count = 0

    def __setitem__(self, k, v):
        if k in self:
            self._total -= self[k]
            self._count -= 1
        dict.__setitem__(self, k, v)
        self._total += v
        self._count += 1

    def average(self):
        if self._count:
            return self._total/self._count

degree=meanDegree()
def remove_dups(seq, idfun=None): #removes duplicates hastags from a tweet
  if idfun is None:
    def idfun(x): return x
  seen={}
  result=[]
  for item in seq:
      marker=idfun(item)
      if marker in seen:continue
      seen[marker]=1
      result.append(item)
  return result

def remove_unicode(tweet): #removes the unicodes from tweets
    return ''.join([i if ord(i) > 31 and ord(i) < 128 else '' for i in tweet])

def create_graph(hashtags):
   if len(hashtags)>=2:  #check if number of hashtags are more than 1
       for i,v in enumerate(hashtags):
           if v not in graph.vertices():graph.add_vertex(v) #add new hashtags as vertex to graph
       for i,v in enumerate(hashtags): #added undirected edges in graph
           if len(hashtags)>2:
               if i==0:graph.add_edge({hashtags[0],hashtags[1]})
               elif i+1< len(hashtags): graph.add_edge({hashtags[i],hashtags[i+1]})
               elif i+1== len(hashtags): graph.add_edge({hashtags[0],hashtags[i]})
           else:
               if i+1 < len(hashtags):graph.add_edge({hashtags[i],hashtags[i+1]})
       for i,v in enumerate(hashtags):degree[v] =graph.vertex_degree(v)  #calculate average degree for new nodes
       rolling_degree.append(degree.average())



def evict_graph(hashtags,key):
   for i in range(len(hashtags)-1):
       if (i+1 < len(hashtags)) and hashtags[i] in graph.vertices() and hashtags in g[hashtags[i]]: #check if nodes exist if evict it
           g[hashtags[i]].remove(hashtags[i+1])
           g[hashtags[i+1]].remove(hashtags[i])
   isolated=graph.find_isolated_vertices() #get the isolated vertex
   if isolated:
       older_tweet.append(key)
       for i in isolated:
           del g[i]
           hashtags.remove(i)
   for i,v in enumerate(hashtags):degree[v] =graph.vertex_degree(v) #check the degree of graphs after evict
   rolling_degree.append(degree.average())

def tweet_processing(tweetFile):
  tweet_file = open(tweetFile)                        # Open the file for reading
  tweet_hash = {}                                     # Define a dictionary for keeping the hashtags as values and their id as keys
  tweet_id={}                                         # Define a dictionary for keeping the created_at as values and their id as keys
  first_tweet=True
  latest_date=None
  print("Started reading tweets")
  for tweet_line in tweet_file:                       # Loop for every tweet in the tweets file
    tweet = json.loads(tweet_line)                    # convert the json string to dictionary object
    if "entities" in tweet.keys():                    # Check whether entities tags present
      hashtags = tweet["entities"]["hashtags"]        #  - if present then extract the hashtags
      if hashtags:
            if first_tweet:
              latest_date=datetime.datetime.fromtimestamp(time.mktime(datetime.datetime.now().timetuple()),pytz.utc)               #set latest date to current datetime if its first tweet
              #latest_date=datetime.datetime.fromtimestamp(mktime_tz(parsedate_tz("Fri Oct 30 15:29:44 +0000 2015")),pytz.utc)
              first_tweet=False
            tweet_hash[tweet["id"]]=remove_dups(['#'+str((remove_unicode(ht['text']))).lower() for ht in hashtags if ht != None and len((remove_unicode(ht['text'])))>1 ]) #extracts the hastags cleans them and checks if length of hashtag is more than 1 character
            tweet_id[tweet["id"]]=[datetime.datetime.fromtimestamp(mktime_tz(parsedate_tz(tweet['created_at'])),pytz.utc),0]
            create_graph(tweet_hash[tweet["id"]]) #calls the

            for key,value in tweet_id.items():   #checks for old tweets if found evict them
                if (latest_date-value[0]).total_seconds()>60:
                    if len(tweet_hash[key])>=2: evict_graph(tweet_hash[key],key)

            #for i in older_tweet:  #removes old tweets from if
            #    if i in tweet_id.keys():del tweet_id[i]
            tweet_date=datetime.datetime.fromtimestamp(mktime_tz(parsedate_tz(tweet['created_at'])),pytz.utc)
            if tweet_date>=latest_date:latest_date=tweet_date

  feature2=open(outfile,'w')
  for degree in rolling_degree:feature2.write(str(degree)+'\n') #write into output file

  print("Processing is completed!!!")


if __name__ == '__main__':
    tweet_processing(infile)