# SFTP Remote Server for Publishing
Files are published using SFTP.

## Server and folder
Host is internal-sftp.sephoraus.com. 
Files to be published are uploaded to folder /inbound/BTC/retailData/prod/vendor/mySephoraLearningV2
The value of the Host and the folder will be kept in env for easy changing across environments.

## Credentials
userId is SephoraRDIInternal
This userID and its Password is to be in the .env so that it is secure

## Property Names
Property names should start with SFTP_OUTBOUND. For example - SFTP_OUTBOUND_HOST