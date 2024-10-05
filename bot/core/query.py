import asyncio
import random
from itertools import cycle

import aiohttp
import requests
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from bot.core.agents import generate_random_user_agent
from bot.config import settings
import cloudscraper
from datetime import datetime, timedelta
from tzlocal import get_localzone
import time as time_module

from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers
from random import randint

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def calc_id(x: int, y: int, x1: int, y1: int):
    px_id = randint(min(y, y1), max(y1, y))*1000
    px_id += randint(min(x, x1), max(x1, x))+1
    # print(px_id)
    return px_id

class Tapper:
    def __init__(self, query: str, session_name, multi_thread):
        self.query = query
        self.session_name = session_name
        self.first_name = ''
        self.last_name = ''
        self.user_id = ''
        self.auth_token = ""
        self.last_claim = None
        self.last_checkin = None
        self.balace = 0
        self.maxtime = 0
        self.fromstart = 0
        self.balance = 0
        self.checked = [False] * 5
        self.multi_thread = multi_thread

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy):
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
            return True
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")
            return False

    def login(self, session: requests.Session):
        response = session.get("https://notpx.app/api/v1/users/me", headers=headers, verify=False)
        if response.status_code == 200:
            logger.success(f"{self.session_name} | <green>Logged in.</green>")
            return True
        else:
            print(response.json())
            logger.warning("{self.session_name} | <red>Failed to login</red>")
            return False

    def get_user_data(self, session: requests.Session):
        response = session.get("https://notpx.app/api/v1/mining/status", headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            print(response.json())
            return None

    def generate_random_color(self):
        r = randint(0, 255)
        g = randint(0, 255)
        b = randint(0, 255)
        return "#{:02X}{:02X}{:02X}".format(r, g, b)

    def generate_random_pos(self):
        return randint(1, 1000000)

    def get_cor(self, session: requests.Session):
        res = session.get("https://raw.githubusercontent.com/vanhbakaa/notpixel-3x-points/refs/heads/main/data4.json")
        if res.status_code == 200:
            cor = res.json()
            paint = random.choice(cor['data'])
            color = paint['color']
            random_cor = random.choice(paint['cordinates'])
            # print(f"{color}: {random_cor}")
            px_id = calc_id(random_cor['start'][0], random_cor['start'][1], random_cor['end'][0], random_cor['end'][1])
            return [color, px_id]

    def repaint(self, session: requests.Session, chance_left):
        #  print("starting to paint")
        if settings.X3POINTS:
            data = self.get_cor(session)
            payload = {
                "newColor": data[0],
                "pixelId": data[1]
            }
        else:
            data = [str(self.generate_random_color()), int(self.generate_random_pos())]
            payload = {
                "newColor": data[0],
                "pixelId": data[1]
            }
        response = session.post("https://notpx.app/api/v1/repaint/start", headers=headers, json=payload, verify=False)
        if response.status_code == 200:
            if settings.X3POINTS:
                logger.success(
                    f"{self.session_name} | <green>Painted <cyan>{data[1]}</cyan> successfully new color: <cyan>{data[0]}</cyan> | Earned <light-blue>{int(response.json()['balance']) - self.balance}</light-blue> | Balace: <light-blue>{response.json()['balance']}</light-blue> | Repaint left: <yellow>{chance_left}</yellow></green>")
                self.balance = int(response.json()['balance'])
            else:
                logger.success(
                    f"{self.session_name} | <green>Painted <cyan>{data[1]}</cyan> successfully new color: <cyan>{data[0]}</cyan> | Earned <light-blue>{int(response.json()['balance']) - self.balance}</light-blue> | Balace: <light-blue>{response.json()['balance']}</light-blue> | Repaint left: <yellow>{chance_left}</yellow></green>")
                self.balance = int(response.json()['balance'])
        else:
            print(response.text)
            logger.warning(f"{self.session_name} | Faled to repaint: {response.status_code}")

    def repaintV2(self, session: requests.Session, chance_left, i, data):
        if i % 2 == 0:
            payload = {
                "newColor": data[0],
                "pixelId": data[1]
            }
        else:
            data1 = [str(self.generate_random_color()), int(self.generate_random_pos())]
            payload = {
                "newColor": data1[0],
                "pixelId": data[1]
            }
        response = session.post("https://notpx.app/api/v1/repaint/start", headers=headers, json=payload, verify=False)
        if response.status_code == 200:
            if i % 2 == 0:
                logger.success(
                    f"{self.session_name} | <green>Painted <cyan>{data[1]}</cyan> successfully new color: <cyan>{data[0]}</cyan> | Earned <light-blue>{int(response.json()['balance']) - self.balance}</light-blue> | Balace: <light-blue>{response.json()['balance']}</light-blue> | Repaint left: <yellow>{chance_left}</yellow></green>")
                self.balance = int(response.json()['balance'])
            else:
                logger.success(
                    f"{self.session_name} | <green>Painted <cyan>{data[1]}</cyan> successfully new color: <cyan>{data1[0]}</cyan> | Earned <light-blue>{int(response.json()['balance']) - self.balance}</light-blue> | Balace: <light-blue>{response.json()['balance']}</light-blue> | Repaint left: <yellow>{chance_left}</yellow></green>")
                self.balance = int(response.json()['balance'])
        else:
            print(response.text)
            logger.warning(f"{self.session_name} | Faled to repaint: {response.status_code}")


    def auto_task(self, session: cloudscraper.CloudScraper):
        pass


    async def auto_upgrade_paint(self, session: requests.Session):
        res = session.get("https://notpx.app/api/v1/mining/boost/check/paintReward", headers=headers, verify=False)
        if res.status_code == 200:
            logger.success(f"{self.session_name} | <green>Upgrade paint reward successfully!</green>")
        await asyncio.sleep(random.uniform(2,4))

    async def auto_upgrade_recharge_speed(self, session: requests.Session):
        res = session.get("https://notpx.app/api/v1/mining/boost/check/reChargeSpeed", headers=headers, verify=False)
        if res.status_code == 200:
            logger.success(f"{self.session_name} | <green>Upgrade recharging speed successfully!</green>")
        await asyncio.sleep(random.uniform(2,4))

    async def auto_upgrade_energy_limit(self, session: requests.Session):
        res = session.get("https://notpx.app/api/v1/mining/boost/check/energyLimit", headers=headers, verify=False)
        if res.status_code == 200:
            logger.success(f"{self.session_name} | <green>Upgrade energy limit successfully!</green>")


    def claimpx(self, session: requests.Session):
        res = session.get("https://notpx.app/api/v1/mining/claim", headers=headers, verify=False)
        if res.status_code == 200:
            logger.success(f"{self.session_name} | <green>Successfully claimed <cyan>{res.json()['claimed']} px</cyan> from mining!</green>")
        else:
            logger.warning(f"{self.session_name} | <yellow>Failed to claim px from mining: {res.json()}</yellow>")

    async def run(self, proxy: str | None) -> None:
        access_token_created_time = 0
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        headers["User-Agent"] = generate_random_user_agent(device_type='android', browser_type='chrome')
        http_client = CloudflareScraper(headers=headers, connector=proxy_conn)
        session = requests.Session()

        if proxy:
            proxy_check = await self.check_proxy(http_client=http_client, proxy=proxy)
            if proxy_check:
                proxy_type = proxy.split(':')[0]
                proxies = {
                    proxy_type: proxy
                }
                session.proxies.update(proxies)
                logger.info(f"{self.session_name} | bind with proxy ip: {proxy}")

        token_live_time = randint(1000, 1500)
        while True:
            try:
                if time_module.time() - access_token_created_time >= token_live_time:
                    # tg_web_data = await self.get_tg_web_data(proxy=proxy)
                    headers['Authorization'] = f"initData {self.query}"
                    access_token_created_time = time_module.time()
                    token_live_time = randint(1000, 1500)

                local_timezone = get_localzone()
                current_time = datetime.now(local_timezone)
                start_time = current_time.replace(hour=settings.SLEEP_TIME[0], minute=0, second=0, microsecond=0)
                end_time = current_time.replace(hour=settings.SLEEP_TIME[1], minute=0, second=0, microsecond=0)

                if end_time < start_time:
                    end_time += timedelta(days=1)

                if settings.NIGHT_MODE and (start_time <= current_time <= end_time):
                    time_to_sleep = (end_time - current_time).total_seconds()
                    logger.info(f"{self.session_name} | Sleeping for {time_to_sleep} seconds until {end_time}.")
                    await asyncio.sleep(time_to_sleep)


                if self.login(session):
                    user = self.get_user_data(session)

                    if user:
                        self.maxtime = user['maxMiningTime']
                        self.fromstart = user['fromStart']
                        self.balance = int(user['userBalance'])

                        if user['charges'] > 0:
                            # print("starting to paint 1")
                            total_chance = int(user['charges'])
                            i = 0
                            data = self.get_cor(session)
                            while total_chance > 0:
                                total_chance -= 1
                                i += 1
                                if settings.X3POINTS:
                                    self.repaintV2(session, total_chance, i, data)
                                else:
                                    self.repaint(session, total_chance)
                                sleep_ = random.uniform(1, 2)
                                logger.info(f"{self.session_name} | Sleep <cyan>{sleep_}</cyan> before continue...")
                                await asyncio.sleep(sleep_)

                        logger.info(
                            f"{self.session_name} | Pixel Balance: <light-blue>{int(user['userBalance'])}</light-blue> | Pixel available to paint: <cyan>{user['charges']}</cyan>")
                        r = random.uniform(2, 4)
                        if float(self.fromstart) >= self.maxtime / r:
                            self.claimpx(session)
                            await asyncio.sleep(random.uniform(2, 5))
                        if settings.AUTO_TASK:
                            res = session.get("https://notpx.app/api/v1/mining/task/check/x?name=notpixel",
                                              headers=headers, verify=False)
                            if res.status_code == 200 and res.json()['x:notpixel'] and self.checked[1] is False:
                                self.checked[1] = True
                                logger.success("<green>Task Not pixel on x completed!</green>")
                            res = session.get("https://notpx.app/api/v1/mining/task/check/x?name=notcoin",
                                              headers=headers, verify=False)
                            if res.status_code == 200 and res.json()['x:notcoin'] and self.checked[2] is False:
                                self.checked[2] = True
                                logger.success("<green>Task Not coin on x completed!</green>")
                            res = session.get("https://notpx.app/api/v1/mining/task/check/paint20pixels",
                                              headers=headers, verify=False)
                            if res.status_code == 200 and res.json()['paint20pixels'] and self.checked[3] is False:
                                self.checked[3] = True
                                logger.success("<green>Task paint 20 pixels completed!</green>")


                        if settings.AUTO_UPGRADE_PAINT_REWARD:
                            await self.auto_upgrade_paint(session)
                        if settings.AUTO_UPGRADE_RECHARGE_ENERGY:
                            await self.auto_upgrade_recharge_speed(session)
                        if settings.AUTO_UPGRADE_RECHARGE_ENERGY:
                            await self.auto_upgrade_recharge_speed(session)

                    else:
                        logger.warning(f"{self.session_name} | <yellow>Failed to get user data!</yellow>")

                else:
                    logger.warning(f"invaild query: <yellow>{self.query}</yellow>")

                if self.multi_thread:
                    sleep_ = randint(settings.SLEEP_TIME_BETWEEN_EACH_ROUND[0],
                                     settings.SLEEP_TIME_BETWEEN_EACH_ROUND[1])
                    logger.info(f"{self.session_name} | Sleep {sleep_}s...")
                    await asyncio.sleep(sleep_)
                else:
                    await http_client.close()
                    session.close()
                    break

            except InvalidSession as error:
                raise error

            except Exception as error:
                logger.error(f"{self.session_name} | Unknown error: {error}")
                await asyncio.sleep(delay=randint(60, 120))


async def run_query_tapper(query: str, name: str, proxy: str | None):
    try:
        sleep_ = randint(1, 15)
        logger.info(f" start after {sleep_}s")
        # await asyncio.sleep(sleep_)
        await Tapper(query=query, session_name=name, multi_thread=True).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"Invalid Query: {query}")

async def run_query_tapper1(querys: list[str], proxies):
    proxies_cycle = cycle(proxies) if proxies else None
    name = "Account"

    while True:
        i = 0
        for query in querys:
            try:
                await Tapper(query=query,session_name=f"{name} {i}",multi_thread=False).run(next(proxies_cycle) if proxies_cycle else None)
            except InvalidSession:
                logger.error(f"Invalid Query: {query}")

            sleep_ = randint(settings.DELAY_EACH_ACCOUNT[0], settings.DELAY_EACH_ACCOUNT[1])
            logger.info(f"Sleep {sleep_}s...")
            await asyncio.sleep(sleep_)

        sleep_ = randint(settings.SLEEP_TIME_BETWEEN_EACH_ROUND[0], settings.SLEEP_TIME_BETWEEN_EACH_ROUND[1])
        logger.info(f"<red>Sleep {sleep_}s...</red>")
        await asyncio.sleep(sleep_)
