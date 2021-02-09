#!/usr/bin/env python3

helpMsg='''

set-category.py -params value option

Description:  This script can be used to add or remove categories from VMs in Prism Central.
              The original idea was took from Stephane Bourdeaud's powershell script @ 
              https://github.com/sbourdeaud/nutanix/blob/master/prism/prism-central/set-category.ps1
              All values are case sensitive.

Parameters:

   -prism <ip>      : IP of Prism Central.

   -user <username> : username who will execute the commands.

   -vm <vm_name>    : name of the VM to edit (as displayed in Prism Central)  (1)

   -sourceCSV <csv_file> : Indicate the path of a comma separated file including a list of VMs to modify. (1)(2)
                      The format of each line (with headers) is: 

                      vm_name,category_name,category_value.

                      You can comment some VMs with '#' at the begining of the VM name, so those VMs will not be 
                      assigned to the Category:Value specified. e.g.

                      vm01, Environment, Production
                      #vm02, Evironment, Dev

                      In this example, vm01 will be assigned to Environment:Production, vm02 will be skipped.
                    

   -category <category_name> : Name of the category to assign to the vm (which must already exists in Prism Central). 

   -value <value_name>  : Name of the category value to assign to the vm (which must already exists in Prism Central).

Options:

   add     : Adds the specified category:value to VM.

   remove  : Removes the specified category:value to VM.

   help    : display this text as help.

Link:  https://github.com/vcdgibbs/scripts

Notes:

Author: Victor D'Gibbs (victor.dgibbs@nutanix.com)
Revision:  February 5, 2021

(1) -vm and -sourceCSV are mutually exclusive, you one or the another one, but never toghether.
(2) VM can't have duplicated names in the cluster, I can't decide the correct UUID.
'''


import requests
import json
import urllib3
import sys
import csv
import getpass
import stdiomask
from utils import *

'''
Se desabilita el "Warning" de conexion insegura. Esto lo dejo asi solo por estar en un ambiente de desarrrollo.
En un ambiente productivo esto no deberia estar.
'''
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

pars=params2dict(sys.argv)

##################### CONTROL #####################
#print(pars)

# Checking parameters and fill vars
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

if "user" in pars:
    User=pars["user"]
else:
    printError("Please provide a Prism Central username.")
    exit(1)

if  ("add" in pars) and ("remove" in pars):
    printError("Could you please decide if you want to add or remove? I can't do both!")
    exit(1)

if  ("add" not in pars) and ("remove" not in pars):
    printError("Could you please specify either add or remove? I will not decide for you.")
    exit(1)

if ("sourcecsv" in pars):
    printInfo("Using CSV file. Parameters -vm -category and -value will not be used.")
    # Let's fill a Dictionary field with the category and value associated to the VM.
    # Note: all initial whitespaces will be removed and in between will be replaced by a underscore ('_') character.

    with open(pars['sourcecsv']) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                #print(f'Column names are {", ".join(row)}')
                # Init some vars
                myVarItem={}
                myListVMs={}
                line_count += 1
            else:
                # Make sure row has 3 values
                if len(row) != 3:
                    continue
                nn=row[0].strip()
                cc=row[1].strip()
                vv=row[2].strip()
                myVarItem = { 
                    "vm_name" : nn.replace(" ", "_"),
                    "category_name" : cc.replace(" ", "_"),
                    "value_name" : vv.replace(" ", "_")
                }
                vmn = "vm" + str(line_count)
                myListVMs[vmn] = myVarItem
                line_count += 1
        #print(f'\tProcessed {line_count} lines.')
        # print(myListVMs)
    #exit(0)


else:
    if "vm" in pars and "category" in pars and "value" in pars:
        # código para dict de una sola VM
        myVarItem = { 
            "vm_name" : pars['vm'],
            "category_name" : pars['category'],
            "value_name" : pars['value']
        }
        myListVMs = { "vm1" : myVarItem }
        print(myListVMs)
    else:
        printError("Please provide the VM with Category and Value information or CSV file")


# Ingresar la password:
# Password = stdiomask.getpass()
# Por ahora dejo la password en duro
Password = "bootCamp123!"

# Variables
API_Server_End_Point="https://" + PC_IP + ":9440/api/nutanix/v3/"
PrismCreds = {
    "User" : User,
    "Password" : Password
    }
headers = {'ContentType':'application/json','cache-control': 'no-cache','Accept':'application/json'}

# API Calls to Prism Central
def Prism_API_Call(Method, URL, Credentials, Payload=None):
    printInfo("Making a " + Method + " call to " + URL)
    us=Credentials["User"]
    pw=Credentials["Password"]
   
    # GET
    if Method == "GET":
        if Payload == None:
            r = requests.get(URL, auth=(us,pw), verify=False)
        else:
            r = requests.get(URL, auth=(us,pw), json=Payload, verify=False)
        # print(r.status_code)
        # Quiero entregar el status_code? del bloque siguiente:
        if r.status_code==200:
            printInfo("- all good, response code " + str(r.status_code) + " as expected :)")
        else:
            printError("- Response code " + str(r.status_code))
            #t=json.dumps(r.json())
            #print (t)
    
    # POST
    if Method == "POST":
        if Payload == None:
            r = requests.post(URL, auth=(us,pw), verify=False)
        else:
            # Control:
            # print(pl)
            # print(type(pl))
            r = requests.post(URL, auth=(us,pw), json=Payload, verify=False)
            # print(r.status_code)
            # Quiero entregar el status_code?
        if r.status_code==200:
            printInfo("- all good, response code " + str(r.status_code) + " as expected :)")
        else:
            printError("- Response code " + str(r.status_code))


    # Python returns a "dict" with the JSON info, so returned value should be json.dumps('d) in order to use it as JSON in another API Call.
    # if returned JSON hasn't status code, I add it to the Dictionay.
    ret =  r.json()
    if "code" not in ret:
        ret["code"]=r.status_code
    #print(type(ret))
    return ret

for VMS in myListVMs:
    #print(VMS)
    #print(myListVMs[VMS]["vm_name"])
    printInfo(Colores.reverse + "Let's process VM name \'" + myListVMs[VMS]["vm_name"] + "\'.")
    if myListVMs[VMS]["vm_name"][0] == "#":
        printInfo(myListVMs[VMS]["vm_name"].strip("#") + " marked with #, will do nothing with this one.")
        continue
    ###############################################################
    # 1. Does Category exist?
    ###############################################################
    Category = myListVMs[VMS]["category_name"]
    Value = myListVMs[VMS]["value_name"]
    printInfo("Checking whether " + Category + ":" + Value + " exists in " + PC_IP)
    comURL=API_Server_End_Point + "categories/" +  Category + "/" + Value
    Method="GET"
    resp = Prism_API_Call(Method,comURL,PrismCreds)
    # resp is a 'dict' field    
    if "code" not in resp:
        resp["code"]=200
    try:
        if resp["code"]!=200:
            printWarning("Category " + Category + ":" + Value + " NOT found in " + PC_IP + ". (Categories and Values are case sensitive)")
            continue
        else:
            printInfo("Category " + Category + ":" + Value + " found in " + PC_IP)
    except:
        #print(Colores.fg.green + "[INFO] Category " + Category + ":" + Value + " found in " + PC_IP)
        printError("Unexpected error.")
        exit(1)

    ###############################################################
    # 2. Get VM details
    ###############################################################
   
    # Let's get the VM UUID
    # VM_UUID = {}
    comURL=API_Server_End_Point + "vms/list"
    flt="vm_name==" + myListVMs[VMS]["vm_name"]
    pl={
        "kind":"vm",
        "filter": flt
        }
    print(type(pl))
    try:
        vd = Prism_API_Call("POST",comURL,PrismCreds,pl)
        tvm = vd["metadata"]["total_matches"]
        if tvm==0:
            printWarning("VM name \'" + myListVMs[VMS]["vm_name"] + "\' does not exist the cluster. (Names are case sensitive)")
            continue
        if tvm > 1:
            printWarning("There are " + str(tvm) + " with VM with the same name \'" + myListVMs[VMS]["vm_name"] + "\'. Skiiping the VM")
            continue
    except:
            printError("Something get wrong, finishing")
            exit(1)
    
    print(json.dumps(vd, indent=2))
    print(vd.keys())
    t_vm=vd["entities"][0]
    #print(Colores.fg.yellow)
    #print(type(t_vm))
    #print(json.dumps(t_vm, indent=2))

    #t_vm=vd.get("entities")
    #print("t_vm es una:")
    #print(type(t_vm))
    #print(len(t_vm))
    # solo tiene 1 elemento la lista, debo procesarlo más
    
    print(Colores.reset)
    print(Colores.fg.orange + "#################### asignar VM_Config ########################")
    #print(t_vm["spec"])
    VM_Config={"spec":t_vm["spec"]}
    #print(type(VM_Config))
    print(json.dumps(VM_Config, indent=2))
    
    print(Colores.reset + "#################### Obtener UUID ########################")
    VM_md={"metadata":t_vm["metadata"]}
    #print(type(VM_md))
    #print(json.dumps(VM_md, indent=2))
    VM_UUID=VM_md["metadata"]["uuid"]
    print("UUID de la VM: "+ VM_UUID)
    
'''
## acli vm.get uuid -> JSON de la VM
VM_UUID="a06a4857-0d0a-4ca0-a90c-aabcaf11ed7a"
comURL=API_Server_End_Point + "vms/" + VM_UUID
Method="GET"
resp = Prism_API_Call(Method,comURL,PrismCreds)
'''