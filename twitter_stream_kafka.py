from __future__ import absolute_import, print_function

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from pyspark.sql.types import *
from kafka import KafkaProducer
from kafka.errors import KafkaError
from http.client import IncompleteRead

producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

#api keys
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

class StdOutListener(StreamListener):
    def on_data(self, data):
        try:
            producer.send("twitter-stream", data.encode('utf-8'))
            print("************************************** data *********************************")
            print(data)
        except:
            pass
        return True

    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    
    # https://stackoverflow.com/questions/28717249/error-while-fetching-tweets-with-tweepy
    while True:
        try:
            # Connect/reconnect the stream
            stream = Stream(auth, l)
            # filter by trump
            stream.filter(track=['trump'])
        except KeyboardInterrupt:
            print("************************************** DEBUG: KeyboardInterrupt")
            stream.disconnect()
            break
        except: # reconnect
            print("************************************** DEBUG: IncompleteRead raised")
            continue