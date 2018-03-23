Requisites:
- if host machine is physical window machine:
    + Need to Enable virtualization in BIOS and enable VT-x support
    + Then install the Hyper-V feature and Management Tools by run powershell
	  Install-WindowsFeature -Name Hyper-V -IncludeManagementTools -Restart
- if using a azure virtual machine, create a window server 2016 DV3 or EV3 size and enable nested virtualization
    https://docs.microsoft.com/en-us/azure/virtual-machines/windows/nested-virtualization
	if you choose to run the script, make sure remove hyper v role from server, so virtual box can use its own hypervisor instead of window hypervisor
	https://serverfault.com/questions/598223/removing-hyper-v-role-from-windows-server-2012-r2

Installation Guide:
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
    http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html?printOnly=1
  + Python 3.62 (Window 64 bit)
    https://www.python.org/ftp/python/3.6.4/python-3.6.4-amd64.exe
  + Spark 2.3 (replacement for Hadoop map reduce, still rely on HDFS)
    http://apache.mirrors.tds.net/spark/spark-2.3.0/spark-2.3.0-bin-hadoop2.7.tgz
https://www.youtube.com/watch?v=lQxlO3coMxM

CDH Overview
https://www.cloudera.com/documentation/enterprise/latest/topics/cdh_intro.html

