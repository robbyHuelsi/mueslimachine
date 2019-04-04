# Install: #

### Update und Upgrade Sortware ###
    sudo apt-get update && sudo apt-get upgrade

### Install Python 3 ###
    wget https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tar.xz
    tar xf Python-3.6.3.tar.xz
    cd Python-3.6.3
    ./configure
    make
    sudo make altinstall
    cd .. && sudo rm -r Python-3.6.3
    rm Python-3.6.3.tar.xz

### Install PIP for Python 3 ###
    sudo apt-get install python3-pip

### Install Flask with addons ###
    sudo pip3 install flask
    sudo pip3 install flask-mysql
    sudo pip3 install flask_nav

### Install MySQL ###
    sudo apt-get install mysql-server && sudo apt-get install mysql-client

