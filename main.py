import requests, asyncio, aiohttp, time
from datetime import datetime


HA_URL = "http://localhost:8123/api/services/light/turn_on"
TOKEN = ""

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "content-type": "application/json"
}

ENTITY = "light.calex_gaming_light_bar"

TEAM_COLORS = {
    "Audi": [[255,0,0], [150,150,150]],
    "Ferrari": [[255,0,0], [255,255,0]],
    "Mercedes": [[0,255,255], [150,150,150]],
    "McLaren": [[255,120,0], [80,80,80]],
    "RedBull": [[0,0,255], [255,255,0]],
    "Racing Bulls": [[0,0,255], [0,0,0]]
}

async def setIdle(session, rgb=[255,0,0], brightness=200, transition=1):
    payload = {
        "entity_id": "light.calex_gaming_light_bar",
        "rgb_color": rgb,
        "brightness": brightness,
        "transition": transition
    }
    await session.post(HA_URL, headers=HEADERS, json=payload)

async def idle(session):
    end = time.time() + 180
    while time.time() < end:
        await setIdle(session, brightness=150)
        await asyncio.sleep(1)
        await setIdle(session)
        await asyncio.sleep(1)
    raise SystemExit


async def setColor(session, rgb, transition=0):
    payload = {"entity_id": ENTITY, "rgb_color": rgb, "brightness": 200, "transition": transition}
    await session.post(HA_URL, headers=HEADERS, json=payload)

async def turnOff(session, transition=0):
    payload = {"entity_id": ENTITY, "brightness": 5, "transition": transition}
    await session.post(HA_URL, headers=HEADERS, json=payload)


flash_flag = None
winner_team = None
color = None

async def flashTask(session):
    global flash_flag, color

    while True:
        if flash_flag:
            color = flash_flag
            await setColor(session, flash_flag)
            await asyncio.sleep(0.8)
            await turnOff(session)
            await asyncio.sleep(0.8)
        else:
            await asyncio.sleep(0.7)
            await setColor(session, color)


flashTimeout_task = None

async def flashTimeout(session, duration=8):
    global flash_flag, flashTimeout_task

    if flashTimeout_task is not None and not flashTimeout_task.done():
        flashTimeout_task.cancel()

    async def timeout():
        global flash_flag
        current_color = flash_flag
        await asyncio.sleep(duration)
        flash_flag = None
        await setColor(session, current_color)

    flashTimeout_task = asyncio.create_task(timeout())


async def flashMonitor(session):
    global flash_flag, winner_team
    last_status = "INIT"
    apiToken = ""
    while True:
        try:
            apiHeaders = {
                "accept": "application/json",
                "Authorization": f"Bearer {apiToken}"
            }
            async with session.get("https://api.openf1.org/v1/race_control?session_key=latest", headers = apiHeaders) as resp:
                data = await resp.json()
                flag = data[-1]["flag"]
                message = data[-1]["message"].lower()
                target_time = datetime(2026, 3, 14, 9, 0 ,0)
                now = datetime.now()
                timestamp = data[-1]["date"]
                timestamp = datetime.fromisoformat(timestamp)
                #print(data)

                if flag != last_status and now >= target_time:
                    last_status = flag

                    if flag in ["CLEAR", "GREEN"] or flag is None:
                        print(f"\x1b[96mFlag changed to: \x1b[92m| GREEN |\x1b[96m " + timestamp.strftime("%H:%M:%S") + "\033[0m")
                        flash_flag = [0,255,0]
                        asyncio.create_task(flashTimeout(session))

                    elif flag and "YELLOW" in flag and not message.startswith("safety"):
                        print(f"\x1b[96mFlag changed to: \x1b[93m| YELLOW |\x1b[96m " + timestamp.strftime("%H:%M:%S") + "\033[0m")
                        flash_flag = [255,255,0]
                        asyncio.create_task(flashTimeout(session))


                    elif flag and "YELLOW" in flag and message.startswith("safety"):
                        print(f"\x1b[96mFlag changed to: \x1b[93m| YELLOW / SC |\x1b[96m " + timestamp.strftime("%H:%M:%S") + "\033[0m")
                        flash_flag = [255,255,0]
                        asyncio.create_task(flashTimeout(session, 16))

                    elif flag == "RED":
                        print(f"\x1b[96mFlag changed to: \x1b[91m| RED |\x1b[96m " + timestamp.strftime("%H:%M:%S") + "\033[0m")
                        flash_flag = [255,0,0]
                        asyncio.create_task(flashTimeout(session, 16))


                    elif flag == "CHEQUERED":
                        print(f"\x1b[96mFlag changed to: \x1b[97m| CHEQUERED |\x1b[96m " + timestamp.strftime("%H:%M:%S") + "\033[0m")
                        flash_flag = [255,255,255]
                        asyncio.create_task(flashTimeout(session, 20))
                        await asyncio.sleep(20)
                        winner_team = await getWinner(session)
                        if winner_team:
                            await celebrate(session, winner_team)
                            await idle(session)
                        else:
                            await setColor(session, [155,0,255])
                            await asyncio.sleep(10)
                            await idle(session)

        except Exception as e:
            print(f"Error in flashMonitor: {e}")

        await asyncio.sleep(3)


async def getWinner(session):
    try:
        results_data = await session.get(
            "https://api.openf1.org/v1/session_result?session_key=latest&position=1"
        )
        results = await results_data.json()
        driver_number = results[0]["driver_number"]

        driver_info = await session.get(
            f"https://api.openf1.org/v1/drivers?driver_number={driver_number}"
        )
        driver_data = await driver_info.json()
        first_driver = driver_data[0]
        team = first_driver.get("team_name", "Mercedes")
        print(f"Winner team: {team}")
        return team

    except Exception as e:
        print(f"Error fetching winner: {e}")
        return None

async def celebrate(session, team):
    colors = TEAM_COLORS.get(team, [[255,0,255],[255,192,203]])
    end_time = asyncio.get_event_loop().time() + 10

    while asyncio.get_event_loop().time() < end_time:
        await setColor(session, colors[0])
        await asyncio.sleep(0.8)
        await setColor(session, colors[1])
        await asyncio.sleep(0.8)



async def main():
    async with aiohttp.ClientSession() as session:
        await setColor(session, [255,0,0])
        print("Pre-race: solid red")
        time.sleep(5)

        await asyncio.gather(
            flashTask(session),
            flashMonitor(session)
        )

if __name__ == "__main__":
    asyncio.run(main())
