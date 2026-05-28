./setup.sh


sudo -u dev python3 /tmp/file_rename_tester.py

sudo -u dev python3 /tmp/file_write_tester.py

# Copy the results to home
sudo mv /tmp/*.json /home/dev
sudo chown dev:dev /home/dev/*.json



#############################
# Cleanup Directories
#############################

sudo rm -rf /tmp/lab-03*
sudo rm -rf /tmp/*.py