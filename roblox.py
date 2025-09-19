import sys
import asyncio
import json
import socket
import os
from datetime import datetime
from colorama import Fore, Style

try:
    import aiohttp
except ImportError:
    print("Module not found")
    sys.exit(0)

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Console:
    @staticmethod
    def clear():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def timer():
        return Style.BRIGHT + Fore.BLACK + f"[{datetime.now().strftime('%I:%M:%S')}] "

    @staticmethod
    def log(query):
        print(Console.timer() + f"{Style.BRIGHT}{Fore.LIGHTMAGENTA_EX}INFO {Fore.WHITE}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK} >  {Fore.RESET}{Fore.WHITE}{query}")

    @staticmethod
    def success(query):
        print(Console.timer() + f"{Style.BRIGHT}{Fore.LIGHTGREEN_EX}SUCCESS {Fore.WHITE}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK} >  {Fore.RESET}{Fore.WHITE}{query}")

    @staticmethod
    def uid(query):
        return input(Console.timer() + f"{Style.BRIGHT}{Fore.LIGHTCYAN_EX}CHECKER {Fore.WHITE}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK} >  {Fore.RESET}{Fore.WHITE}{query}")


class File:
    def __init__(self):
        self.with_funds_path = "groups_with_funds.txt"
        self.no_funds_path = "groups_without_funds.txt"

    def store(self, data, has_funds: bool):
        path = self.with_funds_path if has_funds else self.no_funds_path
        with open(path, "a+", encoding="utf-8") as f:
            f.write(data + "\n")

    def purge(self):
        open(self.with_funds_path, "w", encoding="utf-8").close()
        open(self.no_funds_path, "w", encoding="utf-8").close()


class Checker:
    def __init__(self):
        self.roblox_cookie = {
            ""
        }
        self.console = Console()

    async def get_group_ids(self, user_id):
        group_ids = []
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(family=socket.AF_INET, ssl=False)) as session:
            try:
                async with session.get(f"https://groups.roproxy.com/v2/users/{user_id}/groups/roles") as response:
                    data = await response.json()
                    for group in data.get("data", []):
                        if group['role']['rank'] == 255:
                            group_ids.append(group['group']['id'])
            except Exception:
                pass
        return group_ids

    async def get_group_info(self, group_id):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(family=socket.AF_INET, ssl=False)) as session:
            try:
                async with session.get(f"https://groups.roproxy.com/v1/groups/{group_id}") as response:
                    data = await response.json()
                    return data.get("name", ""), data.get("memberCount", 0)
            except Exception:
                return "", 0

    async def get_clothing_count(self, group_id):
        count = 0
        url = "https://catalog.roproxy.com/v1/search/items/details"
        params = {
            "Category": "3",
            "CreatorTargetId": str(group_id),
            "CreatorType": "2",
            "SortType": "Relevance",
            "SortAggregation": "Relevance",
            "limit": "30",
        }

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(family=socket.AF_INET, ssl=False)) as session:
            while True:
                try:
                    async with session.get(url, params=params) as req:
                        data = await req.json()
                        count += len(data.get("data", []))
                        cursor = data.get("nextPageCursor")
                        if not cursor:
                            break
                        params["cursor"] = cursor
                except Exception:
                    break
        return count

    async def get_group_funds(self, group_id):
        async with aiohttp.ClientSession(cookies=self.roblox_cookie, connector=aiohttp.TCPConnector(family=socket.AF_INET, ssl=False)) as session:
            try:
                async with session.get(f'https://economy.roblox.com/v1/groups/{group_id}/currency') as response:
                    data = await response.json()
                    return data.get("robux", 0)
            except Exception:
                return 0

    async def get_pending_funds(self, group_id):
        async with aiohttp.ClientSession(cookies=self.roblox_cookie, connector=aiohttp.TCPConnector(family=socket.AF_INET, ssl=False)) as session:
            try:
                async with session.get(f"https://economy.roblox.com/v1/groups/{group_id}/revenue/summary") as response:
                    data = await response.json()
                    return data.get("pendingRobux", 0)
            except Exception:
                return 0

    async def get_total_visits(self, group_id):
        total = 0
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(family=socket.AF_INET, ssl=False)) as session:
            try:
                async with session.get(f'https://games.roproxy.com/v2/groups/{group_id}/games?accessFilter=All&sortOrder=Asc&limit=100') as response:
                    data = await response.json()
                    universe_ids = [game["universeId"] for game in data.get("data", [])]

                if not universe_ids:
                    return 0

                chunks = [universe_ids[i:i + 25] for i in range(0, len(universe_ids), 25)]
                for chunk in chunks:
                    ids = ",".join(str(u) for u in chunk)
                    async with session.get(f'https://games.roproxy.com/v1/games?universeIds={ids}') as res:
                        game_data = await res.json()
                        for game in game_data.get("data", []):
                            total += game.get("visits", 0)

            except Exception:
                pass

        return total

    async def get_total_games(self, group_id):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(family=socket.AF_INET, ssl=False)) as session:
            try:
                async with session.get(f'https://games.roproxy.com/v2/groups/{group_id}/games?accessFilter=All&sortOrder=Asc&limit=100') as response:
                    data = await response.json()
                    return len(data.get("data", []))
            except Exception:
                return 0

    async def check_groups(self, user_id):
        group_ids = await self.get_group_ids(user_id)

        for group_id in group_ids:
            group_name, group_members = await self.get_group_info(group_id)
            group_funds = await self.get_group_funds(group_id)
            pending_funds = await self.get_pending_funds(group_id)
            total_games = await self.get_total_games(group_id)
            total_visits = await self.get_total_visits(group_id)
            clothing_count = await self.get_clothing_count(group_id)

            result = f"Group ID: {group_id} | Group Name: {group_name} | Group Members: {group_members} | Group Funds: {group_funds} /\\ Pending Funds: {pending_funds} | Group Clothings: {clothing_count} | Group Games: {total_games} | Group GameVisits: {total_visits}"

            File().store(result, has_funds=(group_funds > 0))
            self.console.success(f"Stored data of '{group_id}'")


if __name__ == '__main__':
    checker = Checker()
    console = Console()
    console.clear()
    File().purge()
    user_id = console.uid("What's your Roblox Account ID: ")
    console.log("Starting Group Checker...")
    asyncio.run(checker.check_groups(user_id))
