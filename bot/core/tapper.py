import asyncio
import json
import re
import datetime
import traceback
from time import time
from urllib.parse import unquote, quote

import aiohttp
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered
from pyrogram.raw import types
from pyrogram.raw.functions.messages import RequestAppWebView

from bot.config import settings

from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers, headers_squads

from random import randint, uniform

from .image_checker import get_cords_and_color, template_to_join, inform, boost_record, break_down
from ..utils.firstrun import append_line_to_file


class Tapper:
    def __init__(self, tg_client: Client, first_run: bool, multithread: bool, key: str):
        self.tg_client = tg_client
        self.first_run = first_run
        self.session_name = tg_client.name
        self.start_param = ''
        self.main_bot_peer = 'notpixel'
        self.squads_bot_peer = 'notgames_bot'
        self.joined = None
        self.balance = 0
        self.template_to_join = 0
        self.user_id = 0
        self.multi_thread = multithread
        self.key = key

    async def get_tg_web_data(self, proxy: str | None, ref:str, bot_peer:str, short_name:str) -> str:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()

                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)
            peer = await self.tg_client.resolve_peer(bot_peer)

            if bot_peer == self.main_bot_peer and not self.first_run:
                if self.joined is False:
                    web_view = await self.tg_client.invoke(RequestAppWebView(
                        peer=peer,
                        platform='android',
                        app=types.InputBotAppShortName(bot_id=peer, short_name=short_name),
                        write_allowed=True,
                        start_param=f"f{self.template_to_join}_t"
                    ))
                    self.joined = True
                else:
                    web_view = await self.tg_client.invoke(RequestAppWebView(
                        peer=peer,
                        platform='android',
                        app=types.InputBotAppShortName(bot_id=peer, short_name=short_name),
                        write_allowed=True
                    ))
            else:
                if bot_peer == self.main_bot_peer:
                    logger.info(f"{self.session_name} | First run, using ref")
                    self.first_run = False
                    await append_line_to_file(self.session_name)
                web_view = await self.tg_client.invoke(RequestAppWebView(
                    peer=peer,
                    platform='android',
                    app=types.InputBotAppShortName(bot_id=peer, short_name=short_name),
                    write_allowed=True,
                    start_param=ref
                ))

            auth_url = web_view.url

            tg_web_data = unquote(
                string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))

            start_param = re.findall(r'start_param=([^&]+)', tg_web_data)

            user = re.findall(r'user=([^&]+)', tg_web_data)[0]
            self.user_id = json.loads(user)['id']

            init_data = {
                'auth_date': re.findall(r'auth_date=([^&]+)', tg_web_data)[0],
                'chat_instance': re.findall(r'chat_instance=([^&]+)', tg_web_data)[0],
                'chat_type': re.findall(r'chat_type=([^&]+)', tg_web_data)[0],
                'hash': re.findall(r'hash=([^&]+)', tg_web_data)[0],
                'user': quote(user),
            }

            if start_param:
                start_param = start_param[0]
                init_data['start_param'] = start_param
                self.start_param = start_param

            ordering = ["user", "chat_instance", "chat_type", "start_param", "auth_date", "hash"]

            auth_token = '&'.join([var for var in ordering if var in init_data])

            for key, value in init_data.items():
                auth_token = auth_token.replace(f"{key}", f'{key}={value}')

            await asyncio.sleep(10)

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()
            return auth_token

        except InvalidSession as error:
            raise error

        except Exception as error:
            if "[420 FLOOD_WAIT_X]" in str(error):
                logger.warning(f"{self.session_name} | Get data failed, Retrying... (This is normal don't ask me about it -_-)")
                await asyncio.sleep(delay=3)
            else:
                logger.error(f"{self.session_name} | 🟥 Unknown error during Authorization: {error}")
                await asyncio.sleep(delay=3)

    async def join_squad(self, http_client, tg_web_data: str, user_agent):
        custom_headers = headers_squads
        custom_headers['User-Agent'] = user_agent
        bearer_token = None
        try:
            custom_headers["Host"] = "api.notcoin.tg"
            custom_headers["bypass-tunnel-reminder"] = "x"
            custom_headers["TE"] = "trailers"

            if tg_web_data is None:
                logger.error(f"{self.session_name} | 🟥 Invalid web_data, cannot join squad")
            custom_headers['Content-Length'] = str(len(tg_web_data) + 18)
            custom_headers['x-auth-token'] = "Bearer null"
            qwe = f'{{"webAppData": "{tg_web_data}"}}'
            r = json.loads(qwe)
            login_req = await http_client.post("https://api.notcoin.tg/auth/login", json=r, headers=custom_headers)

            login_req.raise_for_status()

            login_data = await login_req.json()

            bearer_token = login_data.get("data", {}).get("accessToken", None)
            if not bearer_token:
                raise Exception
            logger.success(f"{self.session_name} | 🟩 <green>Logged in to NotGames</green>")
        except Exception as error:
            logger.error(f"{self.session_name} | 🟥 Unknown error when logging in to NotGames: {error}")

        custom_headers["Content-Length"] = "26"
        custom_headers["x-auth-token"] = f"Bearer {bearer_token}"


        try:
            logger.info(f"{self.session_name} | Joining squad..")
            join_req = await http_client.post("https://api.notcoin.tg/squads/absolateA/join",
                                              json=json.loads('{"chatId": -1002312810276}'), headers=custom_headers)

            join_req.raise_for_status()
            logger.success(f"{self.session_name} | 🟩 <green>Joined squad</green>")
        except Exception as error:
            logger.error(f"{self.session_name} | 🟥 Unknown error when joining squad: {error}")


    async def login(self, http_client: aiohttp.ClientSession):
        try:

            response = await http_client.get("https://notpx.app/api/v1/users/me")
            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | 🟥 Unknown error when logging: {error}")
            logger.warning(f"{self.session_name} | 🟨 Bot overloaded retrying logging in")
            await asyncio.sleep(delay=randint(3, 7))
            await self.login(http_client)

    async def get_user_info(self, http_client: aiohttp.ClientSession):
        try:
            user = await http_client.get('https://notpx.app/api/v1/users/me')
            user.raise_for_status()
            user_json = await user.json()
            return user_json
        except Exception as error:
            logger.error(f"{self.session_name} | <red>Unknown error when processing user info: {error}</red>")
            await asyncio.sleep(delay=3)

    async def check_proxy(self, http_client: aiohttp.ClientSession, service_name, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://ipinfo.io/json', timeout=aiohttp.ClientTimeout(20))
            response.raise_for_status()

            response_json = await response.json()
            ip = response_json.get('ip', 'NO')
            country = response_json.get('country', 'NO')

            logger.info(f"{self.session_name} |🟩 Logging in with proxy IP {ip} and country {country}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")


    async def join_tg_channel(self, link: str):
        if not self.tg_client.is_connected:
            try:
                await self.tg_client.connect()
            except Exception as error:
                logger.error(f"{self.session_name} | 🟥 Error while TG connecting: {error}")

        try:
            parsed_link = link.split('/')[-1]
            logger.info(f"{self.session_name} | 🟨 Joining tg channel {parsed_link}")

            await self.tg_client.join_chat(parsed_link)

            logger.success(f"{self.session_name} | 🟩 <green>Joined tg channel <cyan>{parsed_link}<cyan></green>")

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()
        except Exception as error:
            logger.error(f"{self.session_name} | 🟥 Error while join tg channel: {error}")
            await asyncio.sleep(delay=3)

    async def get_balance(self, http_client: aiohttp.ClientSession):
        try:
            balance_req = await http_client.get('https://notpx.app/api/v1/mining/status')
            balance_req.raise_for_status()
            balance_json = await balance_req.json()
            return balance_json['userBalance']
        except Exception as error:
            logger.error(f"{self.session_name} | 🟥 Unknown error when processing balance: {error}")
            await asyncio.sleep(delay=3)

    async def get_status(self, http_client: aiohttp.ClientSession):
        try:
            balance_req = await http_client.get('https://notpx.app/api/v1/mining/status')
            balance_req.raise_for_status()
            balance_json = await balance_req.json()
            return balance_json
        except Exception as error:
            logger.error(f"{self.session_name} | 🟥 Unknown error when processing status: {error}")
            await asyncio.sleep(delay=3)

    async def tasks(self, http_client: aiohttp.ClientSession):
        try:
            stats = await http_client.get('https://notpx.app/api/v1/mining/status')
            stats.raise_for_status()
            stats_json = await stats.json()
            done_task_list = stats_json['tasks'].keys()
            #logger.debug(done_task_list)
            if randint(0, 5) == 3:
                league_statuses = {"bronze": [], "silver": ["leagueBonusSilver"], "gold": ["leagueBonusSilver", "leagueBonusGold"], "platinum": ["leagueBonusSilver", "leagueBonusGold", "leagueBonusPlatinum"]}
                possible_upgrades = league_statuses.get(stats_json["league"], "Unknown")
                if possible_upgrades == "Unknown":
                    logger.warning(f"{self.session_name} | 🟨 <yellow>Unknown league: {stats_json['league']}, contact support with this issue. Provide this log to make league known. </yellow>")
                else:
                    for new_league in possible_upgrades:
                        if new_league not in done_task_list:
                            tasks_status = await http_client.get(f'https://notpx.app/api/v1/mining/task/check/{new_league}')
                            tasks_status.raise_for_status()
                            tasks_status_json = await tasks_status.json()
                            status = tasks_status_json[new_league]
                            if status:
                                logger.success(f"{self.session_name} | 🟩 <green>League requirement met. Upgraded to <yellow>{new_league} 🏆</yellow>.</green>")
                                current_balance = await self.get_balance(http_client)
                                logger.info(f"{self.session_name} | Current balance: <cyan>{current_balance}</cyan> px")
                            else:
                                logger.warning(f"{self.session_name} | 🟨 <yellow>League requirements not met.</yellow>")
                            await asyncio.sleep(delay=randint(10, 20))
                            break

            for task in settings.TASKS_TO_DO:
                if task not in done_task_list:
                    if task == 'paint20pixels':
                        repaints_total = stats_json['repaintsTotal']
                        if repaints_total < 20:
                            continue
                    if ":" in task:
                        entity, name = task.split(':')
                        task = f"{entity}?name={name}"
                        if entity == 'channel':
                            if not settings.JOIN_TG_CHANNELS:
                                continue
                            await self.join_tg_channel(name)
                            await asyncio.sleep(delay=3)
                    tasks_status = await http_client.get(f'https://notpx.app/api/v1/mining/task/check/{task}')
                    tasks_status.raise_for_status()
                    tasks_status_json = await tasks_status.json()
                    status = (lambda r: all(r.values()))(tasks_status_json)
                    if status:
                        logger.success(f"{self.session_name} | 🟩 <green>Task requirements met. Task <cyan>{task}</cyan> completed</green>")
                        current_balance = await self.get_balance(http_client)
                        logger.info(f"{self.session_name} | Current balance: <cyan>{current_balance} </cyan>px")
                    else:
                        logger.warning(f"{self.session_name} | 🟨 Task requirements were not met <yellow>{task}</yellow>")
                    if randint(0, 1) == 1:
                        break
                    await asyncio.sleep(delay=randint(10, 20))

        except Exception as error:
            logger.error(f"{self.session_name} | 🟥 Unknown error when processing tasks: {error}")

    async def make_paint_request(self, http_client: aiohttp.ClientSession, yx, color, delay_start, delay_end):
        paint_request = await http_client.post('https://notpx.app/api/v1/repaint/start',
                                                json={"pixelId": int(yx), "newColor": color})
        paint_request.raise_for_status()
        paint_request_json = await paint_request.json()
        cur_balance = paint_request_json.get("balance", self.balance)
        change = cur_balance - self.balance
        if change <= 0:
            change = 0
        self.balance = cur_balance
        logger.success(f"{self.session_name} | <green> 🖌 Painted <cyan>{yx}</cyan> with color: <cyan>{color}</cyan> | got <red>+{change:.1f}</red> px 🔳</green>")
        await asyncio.sleep(delay=randint(delay_start, delay_end))

    async def paint(self, http_client: aiohttp.ClientSession, retries=20):
        try:
            stats = await http_client.get('https://notpx.app/api/v1/mining/status')
            stats.raise_for_status()
            stats_json = await stats.json()
            charges = stats_json.get('charges', 24)
            self.balance = stats_json.get('userBalance', 0)
            maxCharges = stats_json.get('maxCharges', 24)
            logger.info(f"{self.session_name} | Total charges: <yellow>{charges}/{maxCharges} ⚡️</yellow>")
            for _ in range(charges - 1):
                try:
                    q = await get_cords_and_color(user_id=self.user_id, template=self.template_to_join)
                except Exception as error:
                    logger.info(f"{self.session_name} | 🟨 <yellow>No pixels to paint</yellow>")
                    return
                coords = q["coords"]
                color3x = q["color"]
                yx = coords
                await self.make_paint_request(http_client, yx, color3x, 2, 5)

        except Exception as error:
            await asyncio.sleep(delay=10)
            if retries > 0:
                logger.warning(f"{self.session_name} | 🟨 Unknown error occurred retrying to paint...")
                await self.paint(http_client=http_client, retries=retries-1)

    async def upgrade(self, http_client: aiohttp.ClientSession):
        try:
            status_req = await http_client.get('https://notpx.app/api/v1/mining/status')
            status_req.raise_for_status()
            status = await status_req.json()
            boosts = status['boosts']
            boosts_max_levels = {
                "energyLimit": settings.ENERGY_LIMIT_MAX_LEVEL,
                "paintReward": settings.PAINT_REWARD_MAX_LEVEL,
                "reChargeSpeed": settings.RECHARGE_SPEED_MAX_LEVEL,
            }
            await boost_record(user_id=self.user_id, boosts=boosts, max_level=boosts_max_levels)
            for name, level in sorted(boosts.items(), key=lambda item: item[1]):
                while name not in settings.IGNORED_BOOSTS and level < boosts_max_levels[name]:
                    try:
                        upgrade_req = await http_client.get(f'https://notpx.app/api/v1/mining/boost/check/{name}')
                        upgrade_req.raise_for_status()
                        logger.success(f"{self.session_name} | <green>🟩 Upgraded boost: <cyan>{name}<cyan><green>")
                        level += 1
                        await asyncio.sleep(delay=randint(2, 5))
                    except Exception as error:
                        logger.warning(f"{self.session_name} | 🟨 Not enough money to keep upgrading.")
                        await asyncio.sleep(delay=randint(5, 10))
                        return
        except Exception as error:
            logger.error(f"{self.session_name} | 🟥 <red>Unknown error when upgrading: {error}</red>")
            await asyncio.sleep(delay=3)

    async def claim(self, http_client: aiohttp.ClientSession):
        try:
            logger.info(f"{self.session_name} | 🟨 Claiming mine reward...")
            response = await http_client.get(f'https://notpx.app/api/v1/mining/status')
            response.raise_for_status()
            response_json = await response.json()
            await asyncio.sleep(delay=5)
            for _ in range(2):
                try:
                    response = await http_client.get(f'https://notpx.app/api/v1/mining/claim')
                    response.raise_for_status()
                    response_json = await response.json()
                except Exception as error:
                    logger.info(f"{self.session_name} | 🟥 First claiming not always successful, retrying..")
                    await asyncio.sleep(delay=randint(20,30))
                else:
                    break

            return response_json['claimed']
        except Exception as error:
            logger.error(f"{self.session_name} |🟥 Unknown error when claiming reward: {error}")
            await asyncio.sleep(delay=3)

    async def in_squad(self, http_client: aiohttp.ClientSession):
        try:
            logger.info(f"{self.session_name} | 🟨 Checking if you're in squad")
            stats_req = await http_client.get(f'https://notpx.app/api/v1/mining/status')
            stats_req.raise_for_status()
            stats_json = await stats_req.json()
            league = stats_json["league"]
            squads_req = await http_client.get(f'https://notpx.app/api/v1/ratings/squads?league={league}')
            squads_req.raise_for_status()
            squads_json = await squads_req.json()
            squad_id = squads_json.get("mySquad", {"id": None}).get("id", None)
            return True if squad_id else False
        except Exception as error:
            logger.error(f"{self.session_name} | <red> 🟥 Unknown error when checking squad reward: {error}</red>")
            await asyncio.sleep(delay=3)
            return True

    async def notpx_template(self, http_client: aiohttp.ClientSession):
        try:
            stats_req = await http_client.get(f'https://notpx.app/api/v1/image/template/my')
            stats_req.raise_for_status()
            cur_template = await stats_req.json()
            cur_template = cur_template["id"]
            return cur_template
        except Exception as error:
            return 0

    async def j_template(self, http_client: aiohttp.ClientSession, template_id):
        try:
            resp = await http_client.put(f"https://notpx.app/api/v1/image/template/subscribe/{template_id}")
            resp.raise_for_status()
            await asyncio.sleep(randint(1, 3))
            return resp.status == 204
        except Exception as error:
            logger.error(f"🟥 <red>Unknown error upon joining a template: {error}</red>")
            return False

    async def join_template(self, http_client: aiohttp.ClientSession):
        try:
            tmpl = await self.notpx_template(http_client)
            self.template_to_join = await template_to_join(tmpl)
            return str(tmpl) != self.template_to_join
        except Exception as error:
            pass
        return False

    async def run(self, user_agent: str, proxy: str | None) -> None:
        access_token_created_time = 0
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None
        headers["User-Agent"] = user_agent

        async with aiohttp.ClientSession(headers=headers, connector=proxy_conn, trust_env=True) as http_client:
            if proxy:
                await self.check_proxy(http_client=http_client, service_name="NotPixel", proxy=proxy)

            ref = settings.REF_ID
            logger.info(f"{self.session_name} | 🔑 Your key: <yellow>{self.key}</yellow>")
            if self.multi_thread:
                delay = randint(settings.START_DELAY[0], settings.START_DELAY[1])
                logger.info(f"{self.session_name} | Starting in <yellow>{delay}</yellow> seconds")
                await asyncio.sleep(delay=delay)


            token_live_time = randint(600, 800)
            while True:
                try:
                    if settings.NIGHT_MODE:
                        current_utc_time = datetime.datetime.utcnow().time()

                        start_time = datetime.time(settings.NIGHT_TIME[0], 0)
                        end_time = datetime.time(settings.NIGHT_TIME[1], 0)

                        next_checking_time = randint(settings.NIGHT_CHECKING[0], settings.NIGHT_CHECKING[1])

                        if start_time <= current_utc_time <= end_time:
                            logger.info(f"{self.session_name} | Current UTC time is <yellow>{current_utc_time.replace(microsecond=0)}</yellow>, so bot is sleeping, next checking in <yellow>{round(next_checking_time / 3600, 1)}</yellow> hours")
                            await asyncio.sleep(next_checking_time)
                            continue

                    if time() - access_token_created_time >= token_live_time:
                        tg_web_data = await self.get_tg_web_data(proxy=proxy, bot_peer=self.main_bot_peer, ref=ref, short_name="app")
                        if tg_web_data is None:
                            continue
                            
                        await inform(self.user_id, 0, key=self.key)

                        http_client.headers["Authorization"] = f"initData {tg_web_data}"
                        logger.info(f"{self.session_name} | <light-blue>💠 Started logining in 💠</light-blue>")
                        user_info = await self.login(http_client=http_client)
                        logger.success(f"{self.session_name} | <green>✅ Successful login</green>")
                        access_token_created_time = time()
                        token_live_time = randint(600, 800)


                    await asyncio.sleep(delay=randint(1, 3))

                    user = await self.get_user_info(http_client)
                    balance = user['balance']
                    status = await self.get_status(http_client)
                    maxtime = status['maxMiningTime']
                    fromstart = status['fromStart']
                    logger.info(f"{self.session_name} | Balance: <cyan>{balance} px 🔲</cyan> | Total repaints: <red>{user['repaints']} 🎨</red> | User league: <yellow>{status['league']} 🏆</yellow>")
                    await inform(self.user_id, balance, key=self.key)

                    if await self.join_template(http_client=http_client):
                        tmpl_req = await self.j_template(http_client=http_client, template_id=self.template_to_join)
                        if not tmpl_req:
                            await asyncio.sleep(randint(5, 15))
                            retry = await self.j_template(http_client=http_client, template_id=self.template_to_join)
                            if not retry:
                                self.joined = False
                                delay = randint(60, 120)
                                logger.info(f"{self.session_name} | 🖼 Joining to template restart in <yellow>{delay}</yellow> seconds.")
                                await asyncio.sleep(delay=delay)
                                token_live_time = 0
                                continue
                            else:
                                logger.success(f"{self.session_name} | <green>Successfully join template: <cyan>{self.template_to_join} 🖼</cyan></green>")

                    if settings.AUTO_DRAW:
                        await self.paint(http_client=http_client)

                    if settings.CLAIM_REWARD:
                        r = uniform(2, 4)
                        if float(fromstart) >= maxtime / r:
                            reward_status = await self.claim(http_client=http_client)
                            logger.success(f"{self.session_name} | <green>Claimed: <cyan>{reward_status} px 🔳</cyan></green>")

                    if True:
                        if not await self.in_squad(http_client=http_client):
                            tg_web_data = await self.get_tg_web_data(proxy=proxy, bot_peer=self.squads_bot_peer,
                                                                     ref="cmVmPTQ2NDg2OTI0Ng==", short_name="squads")
                            await self.join_squad(http_client, tg_web_data, user_agent)
                        else:
                            logger.success(f"{self.session_name} | 🟩 You're already in squad")

                    if settings.AUTO_TASK:
                        logger.info(f"{self.session_name} |🟨 Auto task started")
                        await self.tasks(http_client=http_client)
                        logger.info(f"{self.session_name} | 🟩 Auto task finished")

                    if settings.AUTO_UPGRADE:
                        await self.upgrade(http_client=http_client)

                    if self.multi_thread:
                        sleep_time = randint(settings.SLEEP_TIME[0], settings.SLEEP_TIME[1])
                        logger.info(f"{self.session_name} | 🟨 Sleep <yellow>{round(sleep_time / 60, 1)}</yellow> minutes")
                        await asyncio.sleep(delay=sleep_time)
                    else:
                        await http_client.close()
                        logger.info(f"====<blue>Completed session</blue>: <cyan>{self.session_name}</cyan>====")
                        return


                except InvalidSession as error:
                    raise error

                except Exception as error:
                    # traceback.print_exc()
                    logger.error(f"{self.session_name} | 🟥 Unknown error:")
                    print(error)
                    await asyncio.sleep(delay=randint(60, 120))


async def run_tapper(tg_client: Client, user_agent: str, proxy: str | None, first_run: bool, multithread: bool, key: str):
    try:
        await Tapper(tg_client=tg_client, first_run=first_run, multithread=multithread, key=key).run(user_agent=user_agent, proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")

