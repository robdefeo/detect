Basically get close to this https://wit.ai/docs/intro but better suited

##Install

Download corpus files
`python2.7 -m nltk.downloader all`


####Environment variables
Run from app directory
````
dokku config:set detection MONGOHQ_GETTER_URL="mongodb://getter:getter@paulo.mongohq.com:10030/getter"
dokku config:set detection MONGOHQ_DETECTION_URL="mongodb://detection:detection@linus.mongohq.com:10016/detection"

dokku config:set detection MAIL_USER="admin@jemboo.com"
dokku config:set detection MAIL_PASSWORD="xxxxx"
dokku config:set detection MAIL_FROM="errors@jemboo.com"
dokku config:set detection MAIL_TO="xxxxx@xxxxx.com"

````
