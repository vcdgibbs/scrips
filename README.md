# Scripts
---
`set-category.py` allows you to set or unset categories to VMs. the format could be:

```
$ set-category.py -prism <ip_prism_central> -user <prism_central_usarname> -vm <vm_name> -category <category_name> -value <value_name> add|remove
```
or you can specify a file.csv with
```
$ set-category.py -prism <ip_prism_central> -user <prism_central_usarname> -sourceCSV <your_file.csv> add|remove
```

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

