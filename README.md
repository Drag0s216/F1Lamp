#F1Lamp

An RGB lamp that mirrors live F1 race flag status in real time, running on a Raspberry Pi acting as its own Home Assistant.

How It Works:

Runs on a Raspberry Pi 4B (Raspberry Pi OS Lite), which also acts as the Home Assistant host controlling the RGB lamp.
The Python script requests api.openf1.org for the latest race control flag (Green, Yellow, Red, Safety Car, Chequered, etc.).
Based on the flag, it sends a color update to the RGB lamp through Home Assistant's API.


asyncio was used in order to prevent overlapping flag changes from stepping on each other (a Yellow flag flash getting cut off mid-update by a new Green flag event for example).

The lamp flashes the corresponding color for a few seconds, then settles on solid.
At the end of the race, the script checks the winning team via the OpenF1 API and flashes the lamp in that team's colors. (Not yet tested live! This path only runs after a Chequered flag event, which is hard to test outside an actual race.)


Tech Stack

Python 3, asyncio, aiohttp
OpenF1 API for live race control data
Home Assistant (self-hosted on the same Raspberry Pi) for lamp control
Raspberry Pi OS Lite (or any other device that can be used as a Home Assistant)


Known Limitations

The winner-celebration path (post-Chequered flag) hasn't been tested against a real race finish yet.
Currently tied to one specific lamp entity and Home Assistant instance; I'm not sure if it will work on other lamps/setups.
