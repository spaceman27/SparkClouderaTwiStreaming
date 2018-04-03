from __future__ import print_function

import sys
import json
import happybase
import re

from datetime import datetime
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

# Documentation
# http://spark.apache.org/docs/latest/streaming-programming-guide.html#design-patterns-for-using-foreachrdd
# struct
#key: id
#user: author, location
#general: lang, created, created_ts, text, hashtags
#place: country, country_code, place_type, name, full_name
def parseData(row):
    try:
        # json
        data = json.loads(row)

        # filter broken data or retweet
        if 'user' not in data or data['text'].startswith('RT'):
            return {}

        return data
    except Exception as e:
        print("************************************** DEBUG: exception parser: {0}".format(str(e)))
        return {}
    
# 
def eachRDD(rdd):
    try:
        table = happybase.Connection("localhost").table("tweets") 

        listData = rdd.collect()
        
        batchTotal = len(listData)
        
        if batchTotal > 0:
            # Performing batch mutations
            # ref: http://happybase.readthedocs.io/en/latest/user.html#performing-batch-mutations
            b = table.batch()
            # put each tweet
            for data in listData:
                
                dictData = {}
                
                dictData['user:author'] = data['user']['screen_name']

                if data['user']['screen_name'] is not None:
                    dictData['user:location'] = data['user']['location']

                dictData['general:lang'] = data['lang']
                dictData['general:text'] = data['text']
                dictData['general:created'] = data['created_at']
                
                # convert to unix timestamp
                dictData['general:created_ts'] = datetime.strptime(data['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime("%s")

                if data['entities'] is not None:
                    hashtags = ["#" + hashtag["text"] for hashtag in data['entities']['hashtags']]
                    dictData['general:hashtags'] = ','.join(str(s) for s in hashtags)

                if data['place'] is not None:
                    dictData['place:country'] = data['place']['country']
                    dictData['place:country_code'] = data['place']['country_code']
                    dictData['place:place_type'] = data['place']['place_type']
                    dictData['place:full_name'] = data['place']['full_name']
                    dictData['place:name'] = data['place']['name']
                
                print("************************************** DEBUG: put to table with id: " + data['id_str'])
                b.put(data['id_str'], dictData)

            b.send()
            print("************************************** DEBUG: commit " + str(batchTotal) + " record(s) to hbase")
    except Exception as e:
        print("************************************** DEBUG: exception eachRDD: " + str(e))
        pass  
    
if __name__ == "__main__":
    zkQuorum = "localhost:2181"
    topic = "twitter-stream"

    # https://www.cloudera.com/documentation/enterprise/5-8-x/topics/spark_streaming.html
    sparkConf = SparkConf()
    #sparkConf.set("spark.streaming.receiver.writeAheadLog.enable", "true")
    sc = SparkContext("local[*]", appName="TwitterStreamKafka", conf=sparkConf)
    
    # Create a new StreamingContext.
    # @param sparkContext: L{SparkContext} object.
    # @param batchDuration: the time interval (in seconds) at which streaming data will be divided into batches
    # ref: https://spark.apache.org/docs/1.5.0/api/python/_modules/pyspark/streaming/context.html
    ssc = StreamingContext(sc, 10) # 2s 

    tweets = KafkaUtils.createStream(ssc, zkQuorum, "spark-streaming-consumer", {topic: 1})
    # Tweet processing. 
    # Kafka passes a tuple of message ID and message text. Message text is the tweet text.
    
    # Get data and filter
    tweets = tweets.map(lambda x: parseData(x[1])).filter(lambda x: len(x) > 0)
    
    # process for each RDD
    tweets.foreachRDD(eachRDD)
    
    # use checkpoint
    #checkpoint = "hdfs://localhost:8020/user/cloudera/twitter_stream_checkpoint"
    # write checkpoint
    #ssc.checkpoint(checkpoint)

    ssc.start()
    ssc.awaitTermination()
