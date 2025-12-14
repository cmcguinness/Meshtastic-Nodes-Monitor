# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Meshtastic Monitor is a Flask-based web application that monitors and displays Meshtastic mesh network activity. It connects to a local Meshtastic node via HTTP or Serial and provides a UI for tracking packets, messages, nodes, and network activity.

## Running the Application

### Setup
```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `sample-config.toml` to `config.toml` and update the latitude/longitude settings before running.

### Running
- **WiFi connection**: `python app.py <ip-address-of-node>`
- **Serial connection**: `python app.py /dev/<serial-device>`
- **Quick start**: `./start.sh` (activates venv and runs app)

The connection address can also be set via the `DEVICE_ADDRESS` environment variable. If no address is provided, the app uses the default in mesh.py (line 11).

The app automatically opens a browser window on startup and finds an available port (usually not 5000 on macOS).

## Architecture

### Core Singleton Pattern
The application uses singletons extensively for shared state:
- **Mesh** (mesh.py): Manages the connection to the Meshtastic node. Connects via TCPInterface (WiFi) or SerialInterface (serial port detection based on path starting with '/')
- **Status** (status.py): Maintains packet counts, messages, and packet history with configurable limits
- **NodeData** (nodedata.py): Caches and refreshes node data from the mesh network every 5 minutes
- **Config** (config.py): Loads and provides access to config.toml settings

### Message Flow
1. **Listener** (listener.py) subscribes to Meshtastic events via pubsub
2. **Message** (message.py) processes incoming packets, categorizes by type (TEXT_MESSAGE_APP, TELEMETRY_APP, POSITION_APP, NODEINFO_APP, TRACEROUTE_APP, ENCRYPTED_MSG)
3. **Status** updates are pushed to the UI via polling endpoint `/api/updates`

### Threading and Locking
- Trace routes run in background threads (app.py:61-72) since sendTraceRoute blocks
- NodeData uses locks when flattening data to prevent race conditions (nodedata.py:28)

### Data Persistence
Controlled by `config.toml` settings:
- `persist_data`: Saves messages/packets between sessions in `persisted_data.pkl`
- `append_log`: Controls whether `packetlog.txt` is appended or overwritten on restart
- `max_packets` and `max_messages`: Server-side limits (separate from UI display limits)

### Frontend Architecture
- Single-page app with tabs (Packets, Messages, Nodes, Settings)
- Polls `/api/updates` endpoint for new data
- All dynamic content in static/index.js
- Node ID clicks trigger popup menus for: view details, open map, trace route, send DM

## Key Configuration Points

### mesh.py
- Line 11: `DEFAULT_DEVICE` sets fallback connection address
- Lines 28-33: Connection address priority: command line arg > DEVICE_ADDRESS env var > DEFAULT_DEVICE
- Lines 38-41: Connection type detection (serial if path starts with '/')

### config.toml Structure
```toml
[location]
my_latitude = ...
my_longitude = ...

[data]
append_log = true/false
persist_data = true/false
max_packets = 1024
max_messages = 1024

[debug]
http_logging = false
```

## Important Notes

- Do not kill `python app.py` processes indiscriminately; verify the process is from this app
- The app gets disconnected when the computer sleeps; restart required
- Connection retry logic exists in listener.py (4 attempts with 5-second delays)
- Distance calculations require valid lat/long in config.toml
- Flash messages are used for one-time notifications (e.g., trace route failures) and are cleared after being read once
