#!/bin/bash
packages=("tshark" "ethtool")
for item in "${packages[@]}"; do 
 echo "Checking installation of $item"
 if dpkg -s "$item" &> /dev/null; then
  echo "$item is already installed."
 else 
  echo "$item is not installed. Installing..."
 apt-get update
 apt-get install -y "$item" 
 fi  
done
python3 lab_webapp.py
