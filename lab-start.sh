#/bin/bash
cd ~/34334
sudo apt-get install iperf

if [ -z "$(sudo docker images 34334:ids -q)" ] 
then 
	wget https://files.cyberteknologi.dk/ids-$(uname -m).tar.gz -O ids.tar.gz
	gunzip ids.tar.gz 
	sudo docker load -i ids.tar
	rm ids.tar
 	rm ids.tar.gz
fi
file1="./daemon.json"
file2="/etc/docker/daemon.json"

# Compare the files
if ! cmp -s "$file1" "$file2"; then
    echo "Files are different. Copying $file1 to $file2 and restarting Docker service."
    sudo cp "$file1" "$file2"
    # Restart Docker service
    sudo systemctl restart docker
else
    echo "Docker build ok as is - No action needed"
fi
sudo python lab_webapp.py
