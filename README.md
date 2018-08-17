# Lilbits
Collection of (very) small bits

### Eagle
Cam file used in Eagle for 274x exporting (works with OSH Park). Last used with Eagle 9.0.1

Will export the following:
```
*.GBL *.GBO *.GBS *.GKO *.GML *.GTL *.GTO *.GTP *.GTS *.TXT + .gbrjob
```

### grandMA Stuff
LUA plugin for sending TCP strings, used for PJLINK control
is called and receives parameters from macro as described in file

it is throwing a socket timeout error but it works
will brush it off as a grandMA conundrum

```
# example on shutting down projector

# set variables
SetVar $message="%1AVMT 31";
SetVar $send_ip="192.168.0.2"
SetVar $send_port=4352

# call plugin in the end
Plugin malinksend
```

### LED Stuff
(Very) Simple implementation of Open Pixel Control.
Different approach to the official python version. Used in Touchdesigner to send pixel data to a Fadecandy
