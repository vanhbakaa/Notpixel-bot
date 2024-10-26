import json
import random
import requests
import time
from bot.utils import logger


ENDPOINT = "https://62.60.156.241"
def reachable(times_to_fall=20):
    try:
     
        response = requests.get(f"{ENDPOINT}/is_reacheble/", verify=False)
        if response.status_code == 200:
            data = response.json()
            logger.success(f"Connected to server. Your UUID:{data.get('uuid', None)}")
        response.raise_for_status()
    except Exception as e:
        logger.warning(f"Server unreachable, retrying in 30 seconds, attempt {20 - times_to_fall + 1}/10")
        if times_to_fall > 1:
            time.sleep(30)
            return reachable(times_to_fall - 1)
        exit()

def inform(user_id, balance, times_to_fall=20):
    try:
        if not balance:
            balance = 0
        response = requests.put(f"{ENDPOINT}/info/", json={
            "user_id": user_id,
            "balance": balance,
        }, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning(f"Server unreachable, retrying in 30 seconds, attempt {20 - times_to_fall + 1}/10")
        if times_to_fall > 1:
            time.sleep(30)
            return inform(user_id, balance, times_to_fall - 1)
        exit()

def get_cords_and_color(user_id, template, times_to_fall=20):
    try:
        response = requests.get(f"{ENDPOINT}/get_pixel/?user_id={user_id}&template={template}", verify=False)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning(f"Server unreachable, retrying in 30 seconds, attempt {20 - times_to_fall + 1}/10")
        if times_to_fall > 1:
            time.sleep(30)
            return get_cords_and_color(user_id, template, times_to_fall - 1)
        exit()

def template_to_join(cur_template=0, times_to_fall=20):
    try:
        response = requests.get(f"{ENDPOINT}/get_uncolored/?template={cur_template}", verify=False)
        if response.status_code == 200:
            resp = response.json()
            return resp['template']
        response.raise_for_status()
    except Exception as e:
        logger.warning(f"Server unreachable, retrying in 30 seconds, attempt {20 - times_to_fall + 1}/10")
        if times_to_fall > 1:
            time.sleep(30)
            return template_to_join(cur_template, times_to_fall - 1)
        exit()
