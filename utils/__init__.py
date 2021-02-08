#!/usr/bin/env python3

class Colores:
    reset='\033[0m'
    bold='\033[01m'
    disable='\033[02m'
    underline='\033[04m'
    reverse='\033[07m'
    strikethrough='\033[09m'
    invisible='\033[08m'
    class fg:
        black='\033[30m'
        red='\033[31m'
        green='\033[32m'
        orange='\033[33m'
        blue='\033[34m'
        purple='\033[35m'
        cyan='\033[36m'
        lightgrey='\033[37m'
        darkgrey='\033[90m'
        lightred='\033[91m'
        lightgreen='\033[92m'
        yellow='\033[93m'
        lightblue='\033[94m'
        pink='\033[95m'
        lightcyan='\033[96m'
    class bg:
        black='\033[40m'
        red='\033[41m'
        green='\033[42m'
        orange='\033[43m'
        blue='\033[44m'
        purple='\033[45m'
        cyan='\033[46m'
        lightgrey='\033[47m'

# Fucntion to get a dict class with parameter
'''
The idea is the convert params of:

$ command -param1 val1 -param2 val2 option1 option2

so "-param1 val1" will be a key:value pair as {"param1":"val1"}
and 
if "option1" is text, it will we a key:value pair as {"option1":True}
if "option1" is a number, it will be as {"option1":number} 
'''
def is_number(n):
       try:
           float(n)   # Type-casting the string to `float`.
                      # If string is not a valid `float`, 
                      # it'll raise `ValueError` exception
       except ValueError:
           return False
       return True

def params(args):
    #print(len(args))
    # args[0] -> comando mismo
    # args[1] .. args[n] -> parametros

    p={}
    # option_number
    on=1 
    i=1

    while i<len(args):
        try:
            if args[i][0] == "-":
                # We expect a value for a parameter, so next argument cant begin with '-'
                if args[i+1][0] == "-":
                    p={"error":"expected value"}
                    break
                #print("está " + args[i][0] + " bien?" +args[i])
                temp=args[i].strip('-')
                p[temp]=args[i+1]
                i+=2
            else:
                if is_number(args[i]):
                        nopt = "option" + str(on)
                        p[nopt]=args[i]
                        on+=1
                else:
                    p[args[i]]=True
                i+=1
            #p[args[i]]=args[i+1]
        except:
            p={"error":"expected value"}
            i+=1
            break
        
    return p









''' 
para una funcion de print mas elegante:

quantity = 3
itemno = 567
price = 49.95
myorder = "I want {} pieces of item {} for {} dollars."
print(myorder.format(quantity, itemno, price))

'''