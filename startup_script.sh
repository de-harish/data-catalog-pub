# PRIMARY REQUIREMENT - HAVE PYTHON3.7> SETUP
##Update your package lists and upgrade existing packages by running the following commands:
sudo apt update
sudo apt upgrade -y
##Install Python 3.7 by executing the following command:
sudo apt install python3.7
##Once the installation is complete, you can verify the Python version by running:
python3.7 --version
##To set Python 3.7 as the default version, you'll need to update the symlinks for python and python3. Run the following commands:
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1
##Verify that the default version has been updated by running:
python --version
python3 --version
# Install Pip3
sudo apt install python3-pip
# Git is installed by default. You need to setup the user name and email
git config --global user.name "de-harish"
git config --global user.email "harish.ramesh@talabat.com"
# Clone talabat data catalog repo
git clone https://github.com/talabat-dhme/data-catalog.git
# Install Dependencies
pip3 install cython
pip3 install numpy
pip3 install -r ~/data-catalog/databuilder/requirements.txt
# install docker
sudo apt install docker-compose
#Add user to docker group (if not already added)
sudo usermod -aG docker $USER
sudo usermod -aG sudo $USER
# Create a symbolic link to /usr/bin using the following command
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
# Restart docker service
sudo service docker restart

# run docker
    #sudo docker-compose -f docker-amundsen.yml up -d

# check services are running in the following ports
    # Elastic search - http://35.214.56.176:9200/
    # neo4j - http://35.214.56.176:7474/browser/
    # Frontend - http://35.214.56.176:5000/

# install npm
sudo apt-get install --reinstall python3-apt
sudo apt update

#FOR FRONT END CHANGES
#Make necessary changes to the frontend app and create a new build using a sample command below. Pick the version from the data_catalog/docker-amundsen.yml file
#sudo docker build -t tlb-amundsen-custom-image:0.3.9 .

# Update the data_catalog/docker-amundsen.yml file with the updated image and rerun the docker