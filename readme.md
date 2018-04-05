## Requisites:
- if host machine is physical window machine:
    + Need to Enable virtualization in BIOS and enable VT-x support
    + Then install the Hyper-V feature and Management Tools by run powershell
	  Install-WindowsFeature -Name Hyper-V -IncludeManagementTools -Restart
- if using a azure virtual machine, create a window server 2016 DV3 or EV3 size and enable nested virtualization
    https://docs.microsoft.com/en-us/azure/virtual-machines/windows/nested-virtualization
	if you choose to run the script, make sure remove hyper v role from server, so virtual box can use its own hypervisor instead of window hypervisor
	https://serverfault.com/questions/598223/removing-hyper-v-role-from-windows-server-2012-r2


## Installation
- Download Cloudera QuickStart(Virtual Box)
  
  https://downloads.cloudera.com/demo_vm/virtualbox/cloudera-quickstart-vm-5.13.0-0-virtualbox.zip
  
- Open the VM, modify setting:
   + 4-8 GB RAM
   + at least 2 CPU cores then start the VM 
   + virtual image path is correct 
   
  Troubleshoot for starting the VM
  
  https://community.cloudera.com/t5/Hadoop-101-Training-Quickstart/How-to-setup-Cloudera-Quickstart-Virtual-Machine/ta-p/35056
  
  Once you launch the VM, you are automatically logged in as the cloudera user:
	username: cloudera
	password: cloudera
=======
  Install Java 1.8
  ```
    yum install java-1.8.0-openjdk    
    export PATH=/usr/java/jdk1.8.0_161/bin:$PATH
    sudo update-alternatives --config java    
    java -version
  ```
  make sure we have java 1.8 on set

1. Make sure that yum is up to date by running this command: `sudo yum -y update`

2. Install Kafka follow by this [link from Cloudera](https://www.cloudera.com/documentation/kafka/latest/topics/kafka_installing.html#concept_ctb_k1c_d5)
   ```
   sudo yum -y clean all
   sudo yum -y install kafka
   sudo yum -y install kafka-server
   ```
3. Install Python 3.6
    * CentOS Development Tools
    `sudo yum -y groupinstall development`
    * Install IUS:
    `sudo yum -y install https://centos6.iuscommunity.org/ius-release.rpm`
    * Install Python 3.6
    `sudo yum -y install python36u`
    * Check install by running this command: `python3.6 -V` with output
    `Python 3.6.1`
    * Install Python development that require by install _`happybase`_:
    `sudo yum install python36u-devel.x86_64`
    * Install PIP:
    `sudo yum -y install python36u-pip`
4. Create _virtualenv_ with name **"twitter"** in **/home/cloudera** directory
   ```
   mkdir environments
   cd environments
   python3.6 -m venv twitter
   ```

5. Install PySpark and other libraries to virtualenv from HOME folder

    * Move to virtualenv **"twitter"**:
    `source /home/cloudera/environments/twitter/bin/activate`
    * Upgrade setup tools:
    `pip install --upgrade setuptools`
    * Install PySpark:
    `pip install pyspark`
    * Install Jupyterlab:
    `pip install jupyterlab`
    * Install other Python lib:
    ```
        pip install kafka
        pip install tweepy
        pip install happybase
        pip install -U flask
        pip install -U flask-cors
        pip install pandas
        python -mpip install matplotlib
    ```
6. Install Microsoft's Core Fonts for JupyterLab Virtualization follow by this [link](http://mscorefonts2.sourceforge.net/):
   ```
   sudo yum install curl cabextract xorg-x11-font-utils fontconfig
   sudo rpm -i https://downloads.sourceforge.net/project/mscorefonts2/rpms/msttcore-fonts-installer-2.6-1.noarch.rpm
   ```


Troubleshoot:
   + Azure auto close connection if idle > 4 minutes, lead to user log out
     * Option 1: increase keep alive tcp timeout
	 https://blogs.technet.microsoft.com/nettracer/2010/06/03/things-that-you-may-want-to-know-about-tcp-keepalives/
	 * option 2: use azure cli to set TCP timeout on VM (recommended)
     Install Azure powershell CLI
     https://docs.microsoft.com/en-us/powershell/azure/install-azurerm-ps?view=azurermps-5.5.0
	 Set idle time to 30 minutes
	 Set-AzurePublicIP -PublicIPName 52.168.31.28 -IdleTimeoutInMinutes 30 -VM BigdataServer
	 https://azure.microsoft.com/en-us/blog/new-configurable-idle-timeout-for-azure-load-balancer/

=======
## Deployment

1. Getting Twitter API keys

    * Create a twitter account if you do not already have one. 
    * Go to https://apps.twitter.com/ and log in with your twitter credentials. 
    * Click "Create New App" 
    * Fill out the form, agree to the terms, and click "Create your Twitter application" 
    * In the next page, click on "API keys" tab, and copy your "API key" and "API secret". 
    * Scroll down and click "Create my access token", and copy your "Access token" and "Access token secret".

2. Open Terminal and start Kafka server:
   `sudo service kafka-server start`
3. Create Kafka topic:
   `kafka-topics --create --zookeeper localhost:2181 --topic twitter-stream --partitions 1 --replication-factor 1`
4. Start `hbase shell` and create new table with structure:
    * Key: id_str
    * Column family **user**: author, location
    * Column family **general**: lang, created, text, hashtags
    * Column family **place**: country, country_code, name, full_name, place_type

    by running this command:
      `create 'tweets', 'user', 'general', 'place'`

5. Start `hive` and create new table:
   ```sql
   CREATE EXTERNAL TABLE tweets(id string, user_author string, user_location string,
       general_lang string, general_created string, general_created_ts string, general_text string, general_hashtags string,
       place_country string, place_country_code string, place_name string, place_full_name string, place_place_type string)
   STORED BY 'org.apache.hadoop.hive.hbase.HBaseStorageHandler'
   WITH SERDEPROPERTIES ('hbase.columns.mapping' = ':key,user:author,user:location,general:lang,general:created,general:created_ts,general:text,general:hashtags,place:country,place:country_code,place:name,place:full_name,place:place_type')
   TBLPROPERTIES ('hbase.table.name' = 'tweets');
   ```
   
6. Create Hive view for casting string timestamp to timestamp:
   ```sql
   CREATE VIEW vw_tweets AS
   SELECT id, user_author, user_location, general_lang, general_created,
       from_unixtime(CAST(general_created_ts AS INT)) AS general_created_ts, general_text, general_hashtags,
       place_country, place_country_code, place_name, place_full_name, place_place_type FROM tweets;
   ```
7. Copy file **twitter_stream.zip** to Clouder Home directory and extract, make sure your extracted directory path is:  `/home/cloudera/twitter_stream/`
8. Open file **twitter_stream_kafka.py** and update api keys

## Test and Debug

#### NOTE: all command bellow run from virtualenv "twitter", you must see your terminal start with:
   `(twitter) [cloudera@quickstart ~]$`

1. **Spark Submit receive streaming from Kafka and put data to Hbase**: open new Terminal, active "twitter" virtualenv and run this command: 
   `spark-submit --master local[*] --jars /home/cloudera/twitter_stream/libs/spark-streaming-kafka-0-8-assembly_2.11-2.3.0.jar /home/cloudera/twitter_stream/spark_kafka_process.py`
    * Debug: after start twitter streaming from step 2 bellow, you can search in Terminal with key word _DEBUG:_
        * `************************************** DEBUG: put`: Put data to Hbase table but not commit
        * `************************************** DEBUG: commit`: Commit batch rows to Hbase
        * `************************************** DEBUG: exception eachRDD: `: error when process each RDD
    * TrackingSpark jobs by open this url: [http://quickstart.cloudera:4040/jobs/](http://quickstart.cloudera:4040/jobs/) (url maybe difference)
2. **Twitter Streaming and send to Kafka**: open new Terminal, active "twitter" virtualenv and run

   `python /home/cloudera/twitter_stream/twitter_stream_kafka.py`

3. **Restful API**:
    * Open new Terminal, active "twitter" virtualenv and run this command:

      `python /home/cloudera/twitter_stream/rest_api.py`

    * Test by open this url: [http://quickstart.cloudera:5000/](http://quickstart.cloudera:5000/)
4. Incase you want to test small data:
    * Open new Terminal and start Kafka producer by this command:

      `kafka-console-producer --broker-list localhost:9092 --topic twitter-stream`

    * Copy data from file **twitter_test.json** and paste to Terminal
5. Open new Terminal and start **JupyterLab**:

    `jupyter lab --no-browser --port=8889 --ip=quickstart.cloudera`

    * you can access JupyterLab from url show in Terminal like: http://quickstart.cloudera:8889/?token=xxxx
6. In JupyterLab open file `result_virtualization.ipynb` and _Run All Cells_ from menu _Run_ to show virtualazation

## Troubleshot

1. Sometime Hbase service dead and you must be restart by commands:
   ```
   sudo service hbase-master restart;
   sudo service hbase-regionserver restart;
   ```
2. Sometime when you run file `twitter_stream_kafka.py` some exception when raise, please restart by run that command
3. Run `twitter_stream_kafka.py` and got 401 code: correct you date time
4. Exception when run Hive: `java.lang.RuntimeException: java.lang.RuntimeException: The root scratch dir: /tmp/hive on HDFS should be writable. Current permissions are: rwx------` run this command to give permission: `sudo chmod -R 777 /tmp/hive`

## Some useful commands

1. Restart Hive service: `sudo service hive-server2 restart`
2. Kafka commands:
    * Restart service: `sudo service kafka-server restart`
    * Delete topic: `kafka-topics --delete --zookeeper localhost:2181 --topic twitter-stream`
    * List all topics: `kafka-topics --list --zookeeper localhost:2181`
    * Start producer for manual send data: `kafka-console-producer --broker-list localhost:9092 --topic twitter-stream`
3. Hbase command:
    * Truncate table: `truncate 'tweets'`
4. using Beeline instead of Hive command:
    * Enter Beeline: `beeline`
    * Connect to Hive server: `!connect jdbc:hive2://localhost:10000 hive cloudera`

## Reference

1. Cloudera [https://www.cloudera.com/](https://www.cloudera.com/)
2. Pandas Virtualization: [https://pandas.pydata.org/pandas-docs/stable/visualization.html](https://pandas.pydata.org/pandas-docs/stable/visualization.html)
3. Matplotlib - pyplot: [https://matplotlib.org/api/pyplot_api.html](https://matplotlib.org/api/pyplot_api.html)
4. Spark Document: [https://spark.apache.org/docs/latest/](https://spark.apache.org/docs/latest/)
5. [https://www.google.com/](https://www.google.com/)
6. [https://stackoverflow.com/](https://stackoverflow.com/)
