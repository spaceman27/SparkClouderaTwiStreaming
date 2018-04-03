## Requisites:
- if host machine is physical window machine:
    + Need to Enable virtualization in BIOS and enable VT-x support
    + Then install the Hyper-V feature and Management Tools by run powershell
	  Install-WindowsFeature -Name Hyper-V -IncludeManagementTools -Restart
- if using a azure virtual machine, create a window server 2016 DV3 or EV3 size and enable nested virtualization
    https://docs.microsoft.com/en-us/azure/virtual-machines/windows/nested-virtualization
	if you choose to run the script, make sure remove hyper v role from server, so virtual box can use its own hypervisor instead of window hypervisor
	https://serverfault.com/questions/598223/removing-hyper-v-role-from-windows-server-2012-r2

Installation Guide:


## Installation
- Download Cloudera QuickStart VM 5.14(Virtual Box)
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
	
  Install the following components to CentOS 6.7 (Cloudera VM)
  + install Java SDK 1.8
  ```
    yum install java-1.8.0-openjdk    
  ```
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


CDH Overview
https://www.cloudera.com/documentation/enterprise/latest/topics/cdh_intro.html

