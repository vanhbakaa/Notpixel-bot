import random
import traceback

import aiohttp
import asyncio

from bot.utils import logger

BASE_URL = "https://62.60.156.241"
BASE_URLi = "https://13.61.89.201"


async def break_down(user_id):
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BASE_URLi}/safeguard/?user_id={user_id}", ssl=False) as response:
                    data = await response.json()
                    if data.get('safeguard', True):
                        logger.warning("<yellow>Detected changes in js files, waiting for update from authors</yellow>")
                    else:
                        logger.info("<green>The bot is safe to run now, started running...</green>")
                        return
                    response.raise_for_status()
        except Exception:
            pass
        await asyncio.sleep(30)


async def reacheble(times_to_fall=20):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URLi}/is_reacheble/", ssl=False) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.success(f"🟩 Connected to server your UUID: <cyan>{data.get('uuid', None)}</cyan>.")
                response.raise_for_status()
    except Exception as e:
        logger.warning(f"🟨 Server unreachable, retrying in 30 seconds, attempt {20 - times_to_fall + 1}/20")
        await asyncio.sleep(30)
        if times_to_fall > 1:
            return await reacheble(times_to_fall - 1)
        else:
            exit()


async def inform(user_id, balance, key, times_to_fall=20):
    try:
        async with aiohttp.ClientSession() as session:
            if not balance:
                balance = 0
            async with session.put(f"{BASE_URLi}/info/", json={
                "user_id": user_id,
                "balance": balance,
                "key": key
            }, ssl=False) as response:
                if response.status == 200:
                    a = await response.json()
                    if a['safeguard'] is True:
                        await break_down(user_id)
                    return a
                elif response.status == 400:
                    logger.warning(f"Maxium usage reached for key: <yellow>{key}</yellow>")

                response.raise_for_status()
    except Exception:
        logger.warning(f"🟨 Server unreachable, retrying in 30 seconds, attempt {20 - times_to_fall + 1}/20")
        await asyncio.sleep(30)
        if times_to_fall > 1:
            return await inform(user_id, balance, times_to_fall - 1)
        else:
            exit()


async def get_cords_and_color(user_id, template, times_to_fall=20):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URLi}/get_pixel/?user_id={user_id}&template={template}",
                                   ssl=False) as response:
                if response.status == 200:
                    a = await response.json()
                    if a['safeguard'] is True:
                        await break_down(user_id)
                    return a
                response.raise_for_status()
    except Exception as e:
        logger.warning(f"🟨 Server unreachable, retrying in 30 seconds, attempt {20 - times_to_fall + 1}/20")
        await asyncio.sleep(30)
        if times_to_fall > 1:
            return await get_cords_and_color(user_id, template, times_to_fall - 1)
        else:
            exit()


async def template_to_join(cur_template=0, times_to_fall=20):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URLi}/get_uncolored/?template={cur_template}", ssl=False) as response:
                if response.status == 200:
                    resp = await response.json()
                    return resp['template']
                response.raise_for_status()
    except Exception as e:
        logger.warning(f"🟨 Server unreachable, retrying in 30 seconds, attempt {20 - times_to_fall + 1}/20")
        await asyncio.sleep(30)
        if times_to_fall > 1:
            return await template_to_join(cur_template, times_to_fall - 1)
        else:
            exit()


async def boost_record(user_id=0, boosts=None, max_level=None, times_to_fall=20):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{BASE_URLi}/boost/", json={
                "user_id": user_id,
                "boosts": boosts,
                "max_level": max_level,
            }, ssl=False) as response:
                response.raise_for_status()
    except Exception:
        logger.warning(f"🟨 Server unreachable, retrying in 30 seconds, attempt {20 - times_to_fall + 1}/20")
        await asyncio.sleep(30)
        if times_to_fall > 1:
            await boost_record(user_id=user_id, boosts=boosts, max_level=max_level, times_to_fall=times_to_fall - 1)
        else:
            exit()
