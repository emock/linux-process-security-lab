./setup.sh

#nc -l 127.0.0.1 8080 &

#TODO WONTFIX Some Output or Concurrency issue - use setup and cleanup manually!

#echo "Waiting for 3 seconds"
#sudo -u dev python3 /tmp/fd_visibility.py > /tmp/victim.log 2>&1 &
#
## Timeout is needed to prevent Race Conditions - Writing to log may not be finished
#sleep 1
#echo "Waiting..."

#victim_pid=$(cat /tmp/victim.log | head -n1)
#
#echo "----------------------------"
#echo "Victim PID: $victim_pid"
#echo "----------------------------"

echo "----------------------------"
echo "Reading out FD as same User"
echo "----------------------------"
sudo -u dev python3 /tmp/attacker.py "$victim_pid"

echo "----------------------------"
echo "Reading out FD as partner2"
echo "----------------------------"
sudo -u partner2 python3 /tmp/attacker.py "$victim_pid"

#############################
# Cleanup Directories
#############################

kill "$victim_pid"

#rm -rf /tmp/lab-03*
rm -rf /tmp/*.py


echo "Lab 01 cleanup complete."