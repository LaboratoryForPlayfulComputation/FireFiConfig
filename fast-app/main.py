from typing import Optional

from fastapi import FastAPI, Request

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from shutil import which

import subprocess


templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index(request: Request):
    
    # we want to know if we are connected to a zerotier network
    zerotier_exists = which("zerotier-cli") is not none
    # we want to know what the IP addresses are for all zerotier networks
    zerotier_list = []
    if zerotier_exists:
        zerotier_raw = subprocess.Popen(['zerotier-cli', 'listnetworks'], stdout=subprocess.PIPE)
        zerotier_list, err = zerotier_raw.communicate()

    
    # we want to enable connecting to a wifi network
    wifi_ap_array = scan_wifi_networks()

    # we want to know if we are emitting a hotspot
    # we want to know if we are connected to a wifi network
    # we want to know what network(s) we are connected to either via 
    # ethernet (eth) or wifi (wlan)
    connections = scan_internet_connections()


    return templates.TemplateResponse("index.html", \
        {"request": request, "wifi_ap_array": wifi_ap_array, "connections_array": connections, 
        "zerotier_exists": zerotier_exists, "zerotier_list": zerotier_list})

@app.get("/items/{id}")
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})


######## FUNCTIONS ##########

def scan_wifi_networks():
    # only works on a linux box
    iwlist_raw = subprocess.Popen(['iwlist', 'scan'], stdout=subprocess.PIPE)
    ap_list, err = iwlist_raw.communicate()
    ap_array = []

    for line in ap_list.decode('utf-8').rsplit('\n'):
        if 'ESSID' in line:
            ap_ssid = line[27:-1]
            if ap_ssid != '':
                ap_array.append(ap_ssid)

    return ap_array

def scan_internet_connections():

    # {"name" : "Mp", "interface": [eth/wlan], "flags": flags here,
    # "running": True/False, 'inet': 192.168.8.220, 'is_wifi': True/False}

    # only works on a linux box
    ifconfig_raw = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE)
    int_list, err = ifconfig_raw.communicate()
    connections = []

    networks = int_list.decode('utf-8').rsplit('\n\n')

    for network in networks:
        # beginning of a network chunk
        network = network.strip()
        if network.startswith("eth") or network.startswith("wlan"):
            interface = network.split(":")[0]
            flags = network[network.index("<") + 1: network.index(">")].split(",")
            running = 'RUNNING' in flags
            is_wifi = network.startswith("wlan")
            if running:
                pieces = network.split()
                inet_ind = pieces.index('inet')
                inet_addr = pieces[inet_ind + 1]
            else:
                inet_addr = "none"
            net_dict = {"interface": interface, "flags": flags, "running": running, \
                "inet": inet_addr, "is_wifi": is_wifi}
            connections.append(net_dict)
        
    return connections