import json
import random
import requests
import time
from bot.utils import logger

def reachable(times_to_fall=10):
    try:
        response = requests.get("https://16.16.232.163/is_reacheble/", verify=False)
        response.raise_for_status()
        logger.success("Connected to server.")
    except Exception as e:
        logger.error(f"Server unreachable, retrying in 30 seconds, attempt {10 - times_to_fall + 1}/10")
        if times_to_fall > 0:
            time.sleep(30)
            return reachable(times_to_fall - 1)
        exit()

def participate(username, times_to_fall=10):
    try:
        response = requests.put("https://16.16.232.163/owner_info/",
                                 json={"telegram_tag": username}, verify=False)
        response.raise_for_status()
        logger.success(f"We will write you on @{username} if you win")
    except Exception as e:
        logger.error(f"Server unreachable, retrying in 30 seconds, attempt {10 - times_to_fall + 1}/10")
        if times_to_fall > 0:
            time.sleep(30)
            return participate(username, times_to_fall - 1)
        exit()

def inform(user_id, balance, times_to_fall=10):
    try:
        if not balance:
            balance = 0
        response = requests.put("https://16.16.232.163/info/", json={
            "user_id": user_id,
            "balance": balance,
        }, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Server unreachable, retrying in 30 seconds, attempt {10 - times_to_fall + 1}/10")
        if times_to_fall > 0:
            time.sleep(30)
            return inform(user_id, balance, times_to_fall - 1)
        exit()

def get_cords_and_color(user_id, template, times_to_fall=10):
    try:
        response = requests.get(f"https://16.16.232.163/get_pixel/?user_id={user_id}&template={template}", verify=False)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Server unreachable, retrying in 30 seconds, attempt {10 - times_to_fall + 1}/10")
        if times_to_fall > 0:
            time.sleep(30)
            return get_cords_and_color(user_id, template, times_to_fall - 1)
        exit()

def template_to_join(cur_template=0, times_to_fall=10):
    try:
        response = requests.get(f"https://16.16.232.163/get_uncolored/?template={cur_template}", verify=False)
        if response.status_code == 200:
            resp = response.json()
            return resp['template']
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Server unreachable, retrying in 30 seconds, attempt {10 - times_to_fall + 1}/10")
        if times_to_fall > 0:
            time.sleep(30)
            return template_to_join(cur_template, times_to_fall - 1)
        exit()
