# email: JeffPeery@yahoo.com
# copyright 2011, property of Jeff Peery

import _winreg

OPC_SERVERS_DA1_KEY = r"HKEY_CLASSES_ROOT\Component Categories\{63D5F430-CFE4-11D1-B2C8-0060083BA1FB}"
OPC_SERVERS_DA2_KEY = r"HKEY_CLASSES_ROOT\Component Categories\{63D5F432-CFE4-11D1-B2C8-0060083BA1FB}"
OPC_SERVERS_DA3_KEY = r"HKEY_CLASSES_ROOT\Component Categories\{CC603642-66D7-48F1-B69A-B625E73652D7}"
OPC_SERVERS_KEYS = [OPC_SERVERS_DA1_KEY, OPC_SERVERS_DA2_KEY, OPC_SERVERS_DA3_KEY]
ODBC_DATA_SOURCE_KEY = r"HKEY_CURRENT_USER\Software\ODBC\Odbc.ini\ODBC Data Sources"
	 
def walk(top, writeable=False):
    """walk the registry starting from the key represented by
    top in the form HIVE\\key\\subkey\\..\\subkey and generating
    (key_name, key), subkey_names, values at each level.

    subkey_names are simply names of the subkeys of that key
    values are 3-tuples containing (name, data, data-type).
    See the documentation for _winreg.EnumValue for more details.
    """
    keymode = _winreg.KEY_READ
    if writeable:
        keymode |= _winreg.KEY_SET_VALUE
    if "\\" not in top:
        top += "\\"
    root, subkey = top.split("\\", 1)
    key = _winreg.OpenKey(getattr(_winreg, root), subkey, 0, keymode)

    subkeys = []
    i = 0
    while True:
        try:
            subkeys.append(_winreg.EnumKey(key, i))
            i += 1
        except EnvironmentError:
            break

    values = []
    i = 0
    while True:
        try:
            values.append(_winreg.EnumValue(key, i))
            i += 1
        except EnvironmentError:
            break

    yield (top, key), subkeys, values
    for subkey in subkeys:
        for result in walk(top.rstrip("\\") + "\\" + subkey, writeable):
            yield result

def GetDBLabels():
    keypath = ODBC_DATA_SOURCE_KEY
    s = []
    for (key_name, key), subkey_names, values in walk(keypath):
        level = key_name.count("\\")
##        print " "*level, key_name
        for name, data, datatype in values:
##            print " ", " " * level, name, "=>", data
            s.append(data)
    return s

def GetOPCServerLabels(keypath):
    s = []
    for (key_name, key), subkey_names, values in walk(keypath):
        level = key_name.count("\\")
##            print " "*level, key_name
        for name, data, datatype in values:
##                print " ", " " * level, name, "=>", data
            s.append(data)
    return s

##print GetDBLabels()

##for keypath in OPC_SERVERS_KEYS:
##    print GetOPCServerLabels(r"HKEY_CLASSES_ROOT\Component Categories\{0227cf95-1f01-11d6-a4e5-00e02921ea26}")
