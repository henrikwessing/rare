import errno
import os
import re
import sys
import pwd
import time
import json
import webbrowser


#docker handling code
from lab_app import *
import lab
import argparse
import netifaces
import traceback
import subprocess

from multiprocessing import Process

parser = argparse.ArgumentParser(description='RARE P4 Lab')
parser.add_argument('--debug', action='store_true', default=False)
args = parser.parse_args()

NSROOT = lab.ns_root

# import the Flask class from the flask module, try to install if we don't have it
try:
    from flask import Flask, render_template, request, jsonify
except:
    try:
        subprocess.check_call(['pip3', 'install', 'flask'])
        from flask import Flask, render_template, request, jsonify

    except:
        subprocess.check_call(['apt-get', 'install', 'python3-flask'])
        from flask import Flask, render_template, request, jsonify

# create the application object
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def get_connections():
    """this should return all of the machines that are connected"""
    done = []
    for ns in lab.ns_root.ns:
  #      print(ns.name + "  " + ns.pid)
        for nic in ns.nics:    
            print("------ " + nic)
            if 'root' in nic:
                yield 1,ns.pid
            else:
                if nic not in done:
                    os = c(nic).pid
                    yield ns.pid, os
        done.append(ns.name)

def psef(grep):
    """this is python replacement for ps -ef"""
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        try:
            #read the command line from /proc/<pid>/cmdline
            with open(os.path.join('/proc', pid, 'cmdline'), 'rb') as cmd:
                cmd = cmd.read()
                if grep in cmd:
                    return pid, cmd

        #if the proc terminates before we read it
        except IOError:
            continue

    return False


def buildlab():
	
	print("Building lab in own process")
	time.sleep(3)
	lab.check_dumpcap()
  #see if we can run docker
	try:
		images = subprocess.check_output([b'docker', b'images']).split(b'\n')
	except (OSError,subprocess.CalledProcessError) as e:
		# if e is of type subprocess.CalledProcessError, assume docker is installed but service isn't started
		if type(e) == subprocess.CalledProcessError:
			subprocess.call(['service', 'docker', 'start'])

	lab.docker_build('images/')
  #adding logic to handle writing daemon.json so we can disable docker iptables rules
	daemon_f = '/etc/docker/daemon.json'
	if not os.path.isfile(daemon_f):
		with open(daemon_f, 'w+') as f:
			f.write('{ "iptables": true }')
	subprocess.call(['iptables', '-P', 'INPUT', 'ACCEPT'])
	subprocess.call(['iptables', '-P', 'FORWARD', 'ACCEPT'])
	subprocess.call(['iptables', '-P', 'OUTPUT', 'ACCEPT'])
	subprocess.call(['iptables', '-t', 'nat', '-F'])
	subprocess.call(['iptables', '-t', 'mangle', '-F'])
	subprocess.call(['iptables', '-F'])
	subprocess.call(['iptables', '-X'])

    #lab.docker_clean()

	time.sleep(10)
	print("Ready to serve")
	Process.terminate

# use decorators to link the function to a url
@app.route('/')
def launcher():

    dockers = []

    for docker in NSROOT.ns:
        dockers.append(docker)
    text = { 	'title': 'P4 tutorial', 
    		'text' : 'Establish networks using buttons to the left' }

    return render_template('launcher.html', dockers=dockers, text=text)


@app.route('/building')
def waiting():
	return("Wait while lab is being built")

@app.route('/getnet')
def getnet():

    """This returns the nodes and edges used by visjs, node = { 'id': ns.pid, 'label': ns.name, 'title': ip_address }
        edges = { 'from': ns_connected_from, 'to': ns_connected_to }"""
    data = {}
    data['nodes'] = []
    data['edges'] = []

    for ns in lab.ns_root.ns:
        tmp = {}
        tmp['id'] = ns.pid
        tmp['label'] = ns.name
      #  tmp['type'] = ns.type

        if ns.name=='internet':
            tmp['color'] = 'rgb(0,255,0)'
        
        
        tmp_popup = ''
        for nics in ns.get_nic_info():
            print(nics)
            interface, (mac, ip) = nics.popitem()
            # { 'nic' : ip }
            tmp_popup += f"{interface} : {ip} ({mac}) \n"



        tmp['title'] = tmp_popup

        if ns.type == 'switch':
            tmp['label']= 'sw'
            tmp['color']= 'blue'
            tmp['title']='Switch: '+ns.name


        data['nodes'].append(tmp)

    tmp_popup = ''
    #now add the root ns
    for ips in lab.ns_root.get_ips():
        tmp_popup += '%s : %s \n' % ips.popitem()

    data['nodes'].append({'id' : 1, 'label' : 'localhost', 'color' : 'rgb(204,0,0)', 'title' : tmp_popup})

    for f,t in get_connections():
        tmp = {}
        tmp['from'] = f
        tmp['to'] = t
        tmp['color'] = 'grey'
        data['edges'].append(tmp)

 #   print(data)
    return jsonify(**data)


@app.route('/setup_p4_1')
def setup_p4_1():
    if len(NSROOT.ns) >= 1:
        return 'Update Lab'
    try:
        lab.setup_bmv2("l2-reflector")
        time.sleep(3)
        return 'Update Lab'

    except:
        print(traceback.format_exc())
        return 'Error'

@app.route('/setup_p4_2')
def setup_p4_2():
    if len(NSROOT.ns) >= 1:
        return 'Update Lab'
    try:
        lab.setup_bmv2("l2-forwarding",host_if='eth0')
        time.sleep(3)
        return 'Update Lab'

    except:
        print(traceback.format_exc())
        return 'Error'

@app.route('/shutdown')
def shutdownlab():
	"""cleans up mess"""
	print("Nu er vi i shutdown")
	try:
		lab.ns_root.shutdown()
		time.sleep(3)
		return 'SUCCESS'
	except:
		print(traceback.format_exc())
		return 'FEJL'






# start the server with the 'run()' method
if __name__ == '__main__':

    script_dir = os.path.dirname(os.path.realpath(__file__))
    cwd = os.getcwd()

    if script_dir != cwd:
        print('[*] Not run from the script directory, changing dirs')
        #move to the directory the script is stored in
        os.chdir(script_dir)
    app.config['DEBUG'] = args.debug
    p = Process(target=buildlab)
    p.start()
    print('[*] Lab Launched, Start browser at http://127.0.0.1:5000')
    print('[*] Do not close this terminal. Closing Terminal will terminate lab.')
    app.run(use_reloader=False)
   

   
   


 

  

