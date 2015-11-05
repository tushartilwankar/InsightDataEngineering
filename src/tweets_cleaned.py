__author__ = 'tushar'
import os
import json
import sys

dir = os.path.dirname(__file__)
infile=os.path.abspath(os.path.join(dir,'..',sys.argv[1]))
outfile=os.path.abspath(os.path.join(dir,'..',sys.argv[2]))


def is_unicode(tweet):
    if not any(ord(str(c)) > 31 and ord(str(c)) < 128  for c in tweet)  :
        return True
    else:
        return False

def check_ascii(tweet): #check if tweet contains A-z/a-z
    if  any((ord(str(c)) >= 65 and ord(str(c)) <= 90) or(ord(str(c)) >= 97 and ord(str(c)) <= 122)  for c in tweet)  :
        return True
    else:
        return False


def remove_unicode(tweet): #removes the unicodes from tweets
    return ''.join([i if ord(i) > 31 and ord(i) < 128 else '' for i in tweet])

def cleaner(tweetFile):
  print("Started reading tweets for feature 1")
  tweet_file = open(tweetFile)
  unicode_cnt=0
  feature1=open(outfile,'w')
  for tweet_line in tweet_file:
    tweet = json.loads(tweet_line) #reads the json
    if "text" in tweet.keys():      #check if tweet has any text
        clean_tweet=remove_unicode(tweet["text"].strip().replace('\n', ' ').replace('\r', '').replace('\t',' ')) #exracts text out of tweet and cleans it
        if is_unicode(tweet["text"]): unicode_cnt+=1   #keep count of unicode
        if len(clean_tweet.strip())>1 and check_ascii(clean_tweet):feature1.write(clean_tweet+' (timestamp: '+tweet["created_at"]+')\n')
  feature1.write('\n'+str(unicode_cnt) +' tweets contained unicode.')
  print("Tweets cleaning completed")
if __name__ == '__main__':
    cleaner(infile)
