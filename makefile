# install ansible (http://www.ansible.com.cn/docs/intro_installation.html):
#   brew install ansible
# add add your pub key to target machine: /home/ansible/.ssh/authorized_keys
# (optional) mac osx make autocompletion: http://stackoverflow.com/questions/33760647/makefile-autocompletion-on-mac/36044470#36044470

ping:
	ansible -i ansible_hosts all -m ping -vvvv

deploy-mideep-api:
	# ansible -i ansbile_hosts -u ansible web -m command -a "date"
	ansible -i ansible_hosts -u ansible web -m synchronize -a "src=mideep_api dest=/var/app/enabled rsync_opts='--exclude=.* --exclude=makefile --exclude=__pycache__'"
