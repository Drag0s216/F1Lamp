# 🏎️ F1Lamp

An RGB lamp that mirrors live F1 race flag status in real time, running on a Raspberry Pi acting as its own Home Assistant.

---

## ⚙️ How It Works

* **Hardware & Host:** Runs on a Raspberry Pi 4B (Raspberry Pi OS Lite), which also acts as the Home Assistant host controlling the RGB lamp.
* **API Polling:** The Python script requests `api.openf1.org` for the latest race control flag (Green, Yellow, Red, Safety Car, Chequered, etc.).
* **Home Assistant Control:** Based on the flag, it sends a color update to the RGB lamp through Home Assistant's API.
* **Async Concurrency:** `asyncio` was used in order to prevent overlapping flag changes from stepping on each other (a Yellow flag flash getting cut off mid-update by a new Green flag event, for example).
* **Lighting Pattern:** The lamp flashes the corresponding color for a few seconds, then settles on solid.
* **Winner Celebration:** At the end of the race, the script checks the winning team via the OpenF1 API and flashes the lamp in that team's colors. *(Not yet tested live! This path only runs after a Chequered flag event, which is hard to test outside an actual race.)*

---

## 🧰 Tech Stack

| Component / Tool | Purpose |
| :--- | :--- |
| **Python 3** (`asyncio`, `aiohttp`) | Core logic, asynchronous polling, and API requests |
| **OpenF1 API** | Live race control data and telemetry |
| **Home Assistant** | Self-hosted on the Raspberry Pi for lamp control |
| **Raspberry Pi OS Lite** | Lightweight host OS |

---

## ⚠️ Known Limitations

* The winner-celebration path (post-Chequered flag) hasn't been tested against a real race finish yet.
* Currently tied to one specific lamp entity and Home Assistant instance; I'm not sure if it will work on other lamps/setups.

---

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-41BDF5?style=for-the-badge&logo=home-assistant&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-C51A4A?style=for-the-badge&logo=Raspberry-Pi&logoColor=white)
