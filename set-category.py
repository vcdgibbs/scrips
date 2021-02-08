#!/usr/bin/env python3

'''
Description:  This script can be used to add or remove categories from VMs in Prism Central.
              The original idea was took from Stephane Bourdeaud @ https://github.com/sbourdeaud/nutanix/blob/master/prism/prism-central/set-category.ps1
              All parameters and values are case sensitive.

Parameters:

    -help   : display this text as help.
   
   -prism <ip>     : IP of Prism Central.

   -user <username> : username who will execute the commands.

   -vm <vm_name>    : name of the VM to edit (as displayed in Prism Central)  (1)

   -sourceCSV <csv_file> : Indicate the path of a comma separated file including a list of VMs to modify. (1)
                           The format of each line (with headers) is: 
                           vm_name,category_name,category_value.

   -category <category_name> : Name of the category to assign to the vm (which must already exists in Prism Central). 

   -value <value_name>  : Name of the category value to assign to the vm (which must already exists in Prism Central).

   -add     : Adds the specified category:value to VM.

   -remove  : Removes the specified category:value to VM.

Link:  https://github.com/vcdgibbs/scripts

Notes:

Author: Victor D'Gibbs (victor.dgibbs@nutanix.com)
Revision:  February 5, 2021

(1) -vm and -sourceCSV are mutually exclusive, you one or the another one, but never toghether.
'''


import requests
import json
import urllib3
import sys
import getpass
import stdiomask
from utils import params,Colores

'''
Se desabilita el "Warning" de conexion insegura. Esto lo dejo asi solo por estar en un ambiente de desarrrollo.
En un ambiente productivo esto no deberia estar.
'''
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

pars=(params(sys.argv))
print(pars)


if  ("add" in pars) and ("remove" in pars):
    print("Decídete po wn!!")
    exit()

# Ingresar la password:
####Password = stdiomask.getpass()
# Por ahora dejo la password en duro
Password = "bootCamp123!"


# Set de parametros
User = "admin"

# Variables
PC_IP = "10.42.70.39"
API_Server_End_Point="https://" + PC_IP + ":9440/api/nutanix/v3/"
PrismCreds = {
    "User" : User,
    "Password" : Password
    }
headers = {'ContentType':'application/json','cache-control': 'no-cache'}

# API Calls to Prism Central
def Prism_API_Call(Method, URL, Credentials, Payload=None):
    print(Colores.fg.green +"[INFO] Making a ", Method, " call to ", URL, Colores.reset)
    if Method == "GET":
        # Payload not needed.
        r = requests.get(URL, auth=(Credentials["User"], Credentials["Password"]), verify=False)
        # print(r.status_code)
        if r.status_code==200:
            print(Colores.fg.green +"[INFO] - all good, response code ", r.status_code, " as expected :)", Colores.reset)
        else:
            print(Colores.fg.red+"[ERROR] - Response code ", r.status_code, Colores.reset)
            t=json.dumps(r.json())
            print (t)
    # Python returns a "dict" with the JSON info, so returned value should be json.dumps('d) in order to use it as JSON in another API Call.  
    return r.json()



VM_UUID="a06a4857-0d0a-4ca0-a90c-aabcaf11ed7a"
comURL=API_Server_End_Point + "vms/" + VM_UUID
Method="GET"
resp = Prism_API_Call(Method,comURL,PrismCreds)

# print(resp.status_code)
# print(resp)



# 1. Does Category exist?

Category="Environment"
Value="Production"

print(Colores.fg.green + "[INFO] Checking " + Category + ":" + Value + " exists in " + PC_IP)
comURL=API_Server_End_Point + "categories/" +  Category + "/" + Value
Method="GET"
resp = Prism_API_Call(Method,comURL,PrismCreds)
#print(json.dumps(resp))
#R = json.dumps(resp)
#print(R["code"])
try:

    if resp["code"]!=200:
        print(Colores.fg.red +"[ERROR] - Category " + Category + ":" + Value + " NOT found in " + PC_IP)
        #continue
except:
    print(Colores.fg.green + "[INFO] Category " + Category + ":" + Value + " found in " + PC_IP)