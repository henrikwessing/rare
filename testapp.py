import os
import re
import sys
import pwd
import time
import json
import webbrowser


#docker handling code
import lab
import argparse
import netifaces
import traceback
import subprocess

from multiprocessing import Process

parser = argparse.ArgumentParser(description='Course 34334 Lab')
parser.add_argument('--debug', action='store_true', default=False)
args = parser.parse_args()

print('[*] Firefox eksekveres på http://127.0.0.1:5000')
webbrowser.open('http://127.0.0.1:5000')
  

