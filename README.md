# Meshtastic Monitor

This program was created because I wanted to have a better idea of what was going on in my Meshtastic neighgorhood, and I wanted to have a better sense of what happened when I sent / received messages.

It uses the Python API to talk to a local node over HTTP or Serial (although I'm sure you could modify it to work over BLE).

Here's what the display looks like:

![screenshot](doc/screenshot.png)

Across the top are a count of packet types received.

The left panel logs all text messages received; if they are encrypted and we cannot decode them, it simply says `*** ENCRYPTED TEXT ***`.

The right panel logs all packets seen and, in many cases, reports some interesting information from them (but by all means not all of the information).

If you click on a node in the right panel, you have two choices:

![packetmenu](doc/packetmenu.png)

Open in Map will open a Meshtastic map in a new tab and focus on the node in question.

View Details opens a pop-up:

![details](doc/details.png)



## Running

You'll need to install the requirements via `pip install -r requirements.txt`.  It would probably be a good idea to creatre a virtual environment for it first.  Then just run:

* For connection over WiFi: `python app.py ip-address-of-node`
* For connection over Serial: `python app.py /dev/...`

There are default connections in mesh.py if you don't provide an ip-address or serial device.

It will open a browser window to the app on its own.

