# server

# install ansible (http://www.ansible.com.cn/docs/intro_installation.html):
$ brew install ansible

# add api in mideep_api/server.py

# run command on local:
$ make deploy-mideep-api

# login on mideep server, and run
$ sudo supervisorctl restart mideep-api