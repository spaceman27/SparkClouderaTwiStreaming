import os
# setup pyspark jars
os.environ["PYSPARK_SUBMIT_ARGS"] = "--jars /home/cloudera/twitter_stream/libs/spark-core_2.11-1.5.2.logging.jar,/usr/lib/hbase/hbase-spark-1.2.0-cdh5.14.0.jar,/usr/lib/hive/lib/guava-14.0.1.jar,/usr/lib/hive/lib/hive-hbase-handler-1.1.0-cdh5.14.0.jar,/usr/lib/hbase/lib/htrace-core.jar,/usr/lib/zookeeper/zookeeper.jar,/usr/lib/hbase/hbase-client.jar,/usr/lib/hbase/hbase-common.jar,/usr/lib/hbase/hbase-protocol.jar,/usr/lib/hbase/hbase-server.jar,/usr/lib/hbase/hbase-hadoop-compat.jar,/usr/lib/hbase/hbase-hadoop2-compat.jar,/usr/lib/hbase/lib/metrics-core-2.2.0.jar pyspark-shell"

from pyspark import SparkContext
from pyspark.sql import SparkSession

from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return 'Twitter Streaming Data Mining'

@app.route("/totalbycountry")
def totalbycountry():
    return queryToJson('SELECT place_country, place_country_code, COUNT(*) AS total\
                        FROM default.tweets\
                        WHERE place_country IS NOT NULL\
                        GROUP BY place_country, place_country_code')

@app.route("/bylang/<lang>")
def byHashtag(lang):
    return queryToJson('SELECT * FROM default.tweets WHERE general_lang="' + lang + '"')

@app.route("/tophashtag/<int:val>")
def topten(val):
    return queryToJson('SELECT hashtag AS hashtag, COUNT(*) AS total\
                        FROM default.tweets LATERAL VIEW explode(SPLIT(general_hashtags,",")) aTable AS hashtag\
                        WHERE general_hashtags IS NOT NULL AND LENGTH(general_hashtags) > 0\
                        GROUP BY hashtag\
                        ORDER BY total DESC\
                        LIMIT ' + str(val))

def queryToJson(sql):
    return jsonify(query(sql).toJSON().collect())

def query(sql):
    return getSparkContext().sql(sql)

def getSparkContext():
    sqlContext = SparkSession\
        .builder\
        .appName("RestAPI-Spark-Hive-Hbase")\
        .config("hive.metastore.uris", "thrift://127.0.0.1:9083")\
        .enableHiveSupport()\
        .getOrCreate()
        
    return sqlContext

if __name__ == '__main__':
    #visible to another machine
    app.run(host='quickstart.cloudera',debug=True)
    #app.run(host='localhost',debug=True)