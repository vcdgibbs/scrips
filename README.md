# Scripts
---
`set-category.py` allows you to set or unset categories to VMs. the format could be:

```
$ set-category.py -prism <ip_prism_central> -user <prism_central_usarname> -password <password> -vm <vm_name> -category <category_name> -value <value_name> add|remove
```
or you can specify a file.csv with
```
$ set-category.py -prism <ip_prism_central> -user <prism_central_usarname> -password <password> -sourceCSV <your_file.csv> add|remove
```
Password is optional, you will be asked.

...select `add` or `remove` in the command... self explanatory, doesn't it?

If you choose a file.csv, the format is:

```
vm_name,category_name,value_name
vm01,Environment,Dev
vm02,AppTier,LB
vm03, Environment, Production
#vm04, AppType,Apache
vm05, System, File Server
```
- First line (header) will not be processed, so if you put a VM in the first row, it will be processed as header and do nothing with it.
- Whitespaces preceding to a names (as in vm03) will be deleted (`' Environment'` --> `'Environment'`)
- Whitespaces between strings (as in vm05) will be replaced with underscores (`'File Server'` --> `'File_Server'`)
- Put a `'#'` at the beginig of to row to skip this one. VM names with # will be skipped.
- Empty rows or with less|more that 3 columns will be omitted.
---

`get-vm-info.py` allows you to get information about a VM. the format is:
```
$ get-vm-info.py -prism <ip_prism_central> [-user <prism_central_usarname>] [-password <password>] -vm <vm_name> [-indent <#>] uuid|spec|status
```
parameters in [ ] are optional, username and password will be asked if not provided as parameters.

you will get:

The vm UUID if `uuid`is selected, the vm `spec` configuration in json format or the vm `status` in json format.

JSON will be written in a single line unless you specify the `indent` parameter. `indent` can be any numbre from 1 to 8.