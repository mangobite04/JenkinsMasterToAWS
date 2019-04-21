#!/usr/bin/env python

import boto3

ec2 = boto3.resource('ec2', region_name='eu-west-1')

user_data = '''#!/bin/bash
wget -O /etc/yum.repos.d/jenkins.repo http://pkg.jenkins.io/redhat-stable/jenkins.repo
rpm --import http://pkg.jenkins.io/redhat-stable/jenkins.io.key
yum install -y jenkins
yum remove -y java-1.7*
yum install -y java-1.8*
#java -Djenkins.install.runSetupWizard=false -jar /usr/lib/jenkins/jenkins.war
var1=`curl http://169.254.169.254/latest/meta-data/local-ipv4`
pass=`sudo cat /var/lib/jenkins/secrets/initialAdminPassword` && echo 'jenkins.model.Jenkins.instance.securityRealm.createAccount("adminuser", "password123")' | sudo java -jar /var/cache/jenkins/war/WEB-INF/jenkins-cli.jar -auth admin:$pass -s http://"$var1":8080/ groovy =
java -jar /var/cache/jenkins/war/WEB-INF/jenkins-cli.jar -auth admin:$pass -s http://"$var1":8080/ install-plugin EC2
service jenkins restart'''

# Instance Creation and Tagging
instance = ec2.create_instances(
	ImageId='ami-08935252a36e25f85', 
	MinCount=1, 
	MaxCount=1, 
	KeyName='my_keypair_name', 
	SecurityGroupIds=['sg-ec15e091'], 
	InstanceType='t2.micro',
	BlockDeviceMappings=[
    	{
        	'DeviceName': '/dev/xvda',
        	'Ebs': {
            	'VolumeSize': 30,
            	'VolumeType': 'standard'
        	}
    	}
	],
    TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'eu00jmaster01',
                    },
                    {
                        'Key': 'LinuxDomain',
                        'Value': 'testlab.com',
                    },
                    {
                        'Key': 'Dtap',
                        'Value': 'DTA',
                    },
                    {
                        'Key': 'Owner',
                        'Value': 'Devesh',
                    },
                ],
            },
        ],
    UserData=user_data)
    
for instances in instance:
  print("waiting for the instance to be running state")
  instances.wait_until_running()
  instances.reload()
  print("Instance id ", instances.id)
  print("Instance state ", instances.state['Name'])
  print("Instance public DNS", instances.public_dns_name)
  print("Instance private DNS ", instances.private_dns_name)
