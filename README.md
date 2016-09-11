# Anonymous Electronic-Cash - A proof-of-concept implementation of the Anonymous Credentials Light scheme for electronic-cash


##	Install Vagrant and Virtual Machine on Windows 10
Install Vagrant following guidelines from their website . 
Install VirtualBox following guidelines from their website .
Move to the folder where the project will be set up. Run the following two commands to install the Ubuntu operating system.
```vagrant init hashicorp/precise64
vagrant up```

Vagrant automatically installs Ubuntu 12.04 LTS 64-bit which already includes Python. The virtual machine and the host machine are automatically set up to have a shared folder. This allows editing to be done from either machine.


##	Install Python Packages
SSH into this machine by running the following command:
```vagrant ssh```
Install Django using the instructions provided on the website  (the default database is also set in the process).
Install Petlib using the instructions provided on the website .
The Merchant’s website requires Pillow . Install this with the following commands.
```sudo apt-get install python-dev
sudo apt-get install libjpeg8-dev
sudo ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib
sudo pip install pillow```

To combine Bootstrap formatting with Django forms, install Django-bootstrap3 .
```sudo pip install django-bootstrap3```

To install Coverage , run the following.
```sudo pip install coverage```


##	Install Project
Unzip project file into the shared folder.
In the project file there are the folders for the three websites – websites_bank, websites_merchant, and websites_wallet. Inside each folder is a folder with the same name, which contains settings.py. In each there are three variables.
```WALLET_URL = 'http://192.168.33.10:8000/wallet'
MERCHANT_URL = 'http://192.168.33.10:8080/merchant'
BANK_URL = 'http://192.168.33.10:8090/bank'```

These must be updated to the IP address of the virtual machine. 


##	Run Project
As there are three websites, three console windows are required to SSH into the virtual machine. Each terminal into the virtual machine must be in each of the three websites folders. For example, ```cd ../../vagrant/Project/websites_wallet```. Then the following two commands must be run (with the IP addresses matching previous).
```export PYTHONPATH=/vagrant/Project
python manage.py runserver 192.168.33.10:8000```
 
