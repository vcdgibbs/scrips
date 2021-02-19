#!/usr/bin/env python3

helpMsg='''
get-vm-info.py -params value option

Description:  Retrieve either the VM's UUID,the complete JSON Config or the JSON Status of the named VM.

Parameters:
   -prism <ip>      : Prism Central IP address.
   -user <username> : username who will execute the commands. (optional)
   -password <pwd>  : username's password (optional)
   -vm <vm_name>    : name of the VM to get the info (as displayed in Prism Central).
   -indent <#>      : Indentation spaces (1 to 8) for the JSON (to look nice, not only 1 line).

Options:
   uuid     : Get the VM's UUID
   spec     : Get the complete configuration in JSON.  This JSON can be used to update the 
              VM.
   status   : Get the status in JSON.
   help    : display this text as help.

Link:  https://github.com/vcdgibbs/scripts

Notes:

Author: Victor D'Gibbs (victor.dgibbs@nutanix.com)
Revision:  February 19, 2021

To do:
- My imagination is not working today for this script.

'''
import requests
import json
import urllib3
import sys
import stdiomask
from utils import *

'''
Se desabilita el "Warning" de conexion insegura. Esto lo dejo asi solo por estar en un ambiente de desarrrollo.
En un ambiente productivo esto no deberia estar.
'''
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# let's construct a DICT class from the arguments:
pars = params2dict(sys.argv)

if "error" in pars:
    printError(pars['error'])
    exit(1)

if "help" in pars:
    print(helpMsg)
    exit(0)

if "prism" in pars:
    if valid_ip(pars['prism']):
        PC_IP=pars["prism"]
        try:
            t_url="https://"+PC_IP+":9440/console/#login"
            r1 = requests.get(t_url, verify=False)
        except:
            printError("Trying to go to "+ t_url + ", but it is unreachable, is the Prism Central IP address " + PC_IP + " Correct?")
            exit(1)

    else:
        print(Colores.fg.red+"[Error] Please provide a valid IP address." + Colores.reset)
        exit(1)
else:
    print(Colores.fg.red+"[Error] Prism Central address not provided." + Colores.reset)
    exit(1)

if "vm" in pars:
    vm_name=pars["vm"]
else:
    printError("Please provide the VM name.")
    exit(1)

if "indent" in pars.keys():
    if is_number(pars["indent"]):
        indt=int(pars["indent"])
    else:
        indt=0
else:
    indt=0


if  ("uuid" in pars):
    if "spec" in pars:
        printError("Could you please decide if you want the UUID or the specs? I can't do both!")
        exit(1)
    if "status" in pars:
        printError("Could you please decide if you want the UUID or the status? I can't do both!")
        exit(1)

if  ("uuid" not in pars) and ("spec" not in pars) and ("status") not in pars:
    printError("Could you please specify what do you need the retrieve? I will not decide for you.")
    exit(1)

if "user" in pars:
    User = pars["user"]
else:
    User = input("User: ")

if "password" in pars:
    Password = pars["password"]
else:
    Password = stdiomask.getpass()



# Variables
API_Server_End_Point="https://" + PC_IP + ":9440/api/nutanix/v3/"
PrismCreds = {
    "User" : User,
    "Password" : Password
    }
headers = {'ContentType':'application/json','Accept':'application/json'}

###################################################################################
# API Calls to Prism Central
# https://httpstatuses.com/ is a good page to know the HTTP status codes
###################################################################################

def Prism_API_Call(Method, URL, Credentials, Payload=None):
    #printInfo("Making a " + Method + " call to " + URL)
    us=Credentials["User"]
    pw=Credentials["Password"]
   
    # GET ##########################################################
    if Method == "GET":
        if Payload == None:
            r = requests.get(URL, auth=(us,pw), verify=False)
        else:
            r = requests.get(URL, auth=(us,pw), json=Payload, verify=False)

        if r.status_code!=200 and r.status_code!=202:
            printError("Response code " + str(r.status_code))
    
    # POST #########################################################
    if Method == "POST":
        if Payload == None:
            r = requests.post(URL, auth=(us,pw), verify=False)
        else:
            r = requests.post(URL, auth=(us,pw), json=Payload, verify=False)

        if r.status_code!=200 and r.status_code!=202:
            printError("Response code " + str(r.status_code))

    # PUT ##########################################################
    if Method == "PUT":
        if Payload == None:
            r = requests.put(URL, auth=(us,pw), verify=False)
        else:
            r = requests.put(URL, auth=(us,pw), json=Payload, verify=False)

        if r.status_code!=200 and r.status_code!=202:
            printError("Response code " + str(r.status_code))

    # Python returns a "dict" with the JSON info, so returned value should be json.dumps('d) in order to use it as JSON in another API Call.
    # if returned JSON hasn't status code, I add it to the Dictionay.
    ret =  r.json()
    if "code" not in ret:
        ret["code"]=r.status_code
    return ret



###############################################################
# Get VM details, UUID 
###############################################################

# Let's get the VM details
comURL=API_Server_End_Point + "vms/list"
flt="vm_name==" + vm_name
pl={
    "kind":"vm",
    "filter": flt
    }

try:
    vd = Prism_API_Call("POST",comURL,PrismCreds,pl)
    tvm = vd["metadata"]["total_matches"]
    if tvm==0:
        printWarning("VM name \'" + vm_name + "\' does not exist the cluster. (Names are case sensitive)")
        exit(1)
    if tvm > 1:
        # I can't decide which VM to assign the category to.
        printWarning("There are " + str(tvm) + " with VM with the same name \'" + vm_name + "\'. Skiping the VM")
        exit(1)
except:
        printError("Something get wrong, finishing")
        exit(1)

t_vm=vd["entities"][0]
# deleteing old 'categories' key, I will use only 'categories_mapping' key:
t_vm["metadata"]["use_categories_mapping"]=True
t_vm["metadata"].pop("categories")

# Let's get the JSON VM config in VM_Config field:
VM_Config={
    "spec" : t_vm["spec"], 
    "api_version" : vd["api_version"],
    "metadata": t_vm["metadata"]
    }

# Let's get the JSON VM status in VM_Status field:
VM_Status={
    "status" : t_vm["status"], 
    "api_version" : vd["api_version"],
    "metadata": t_vm["metadata"]
    }


# and let's get the VM UUID:
VM_md={"metadata":t_vm["metadata"]}
VM_UUID=VM_md["metadata"]["uuid"]

if "uuid" in pars:
    print(VM_UUID)
    exit(0)

if "spec" in pars:
    if indt == 0 or indt > 8:
        print(json.dumps(VM_Config))
    else:
        print(json.dumps(VM_Config, indent=indt))
    exit(0)
else:
    if indt == 0 or indt > 8:
        print(json.dumps(VM_Status))
    else:
        print(json.dumps(VM_Status, indent=indt))
    exit(0)

