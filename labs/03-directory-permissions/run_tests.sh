./setup.sh


sudo -u dev python3 /tmp/file_rename_tester.py

#
#sudo -u partner_component python3 /tmp/file_access_tester.py
#
#
#
#sudo -u third_party python3 /tmp/file_access_tester.py



# Copy the results to home
sudo mv /tmp/*.json /home/dev
sudo chown dev:dev /home/dev/*.json



sudo ./cleanup.sh