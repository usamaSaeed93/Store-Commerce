#!/usr/bin/env bash
# clean codedeploy-agent files for a fresh install
sudo rm -rf /home/ubuntu/install


# update os & install python3
sudo apt-get update
sudo apt-get install -y python3 python3-dev python3-pip python3-venv
pip install --user --upgrade virtualenv

# delete app
sudo rm -rf /home/ubuntu/orange_storage_backend
