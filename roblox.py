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
            ".ROBLOSECURITY": "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_CAEaAhAB.14D247506472471FAFA0F8979EB89F9AAE5FF7496EC20ECC57AE1D3C99413B7AA70F3424B8028176383B1416E161330746B4293F07E8907B2E1ADB5E29F7AD6F976D7D387286FBA4FEA1ED3A205363B01264BF2253F9B20A7601B1CFEC1B381DF328F1755327ABDF5677A44E4E96A8FA2CC8432A964BC6F1A27E58EB614E416DBD2DD329E8BFF132FE4807AB0EF653A77F4F1B24C4A63E3F175E15EB2FDB874904761D890ECCF91F6B0E4847F23AF447771CCF3662A3E5028B5C090CAC9E9B23B557DC99312C3B3010E14B452D612276FEC5F32344E40423EE0B6F99056E03AFF31572B9C8EB9ED87C5FB7D724F354FF1AAFEBA8A8EEDF25F0289B462F3FDB2401261EC6538E8123BFCD09429CA0955F5D543603D97A82B000B1AFFF75BAE98AFF259FC426D4949CC9F51E84367ABC20D4708CA9AA13A5C2C0EFBE5DBAF271B8A7E1F42197057A6865709C46FF1F9BE968A221B7856E5684A79B1EDD67396A8DA74EDE383136D7C9F58F51439D4A116FF03DA9FFAF3B33C78F0BEAEBE602428B856CFCAFB65A3F82595A81B8E59FB305056B8A07056739CCD98294C66608397B613EC9E28BF3C4DCE04B43D8C0FCDA1E8CEFD5364DF53709846FCFB6BEBB93970A01A2B9C358A0B5BABC75635F1687239019787A74029345D31FEF179D00DBFEDD580D678E7C446CF5A0E7C8BD9EF680800BCB11B3113D30EC5BDE6C48EC743FDB9905F1DCD49163AA6C5100EF8725290C6ECE759A65B1E4EBBE7B001353325A4F4F5B03BC0718841F7AE1EAA3D771C32835783288EF97478866202246E205893D4843D127D715D14CF663CC956614EA90CD32D1A1E53F1EBC4E59E829F291076C50CA3AAC2133FF251259AEA0FD02C163EC7AE73F3A89810B3A9EFAF124690F4523530ACD00164BF0FA11A27E0D6FF2D77D60722FC13CE0C4A6CD4D244463D0FC03C421B04F755D4DD2474B6239E3D5657E7B77ACAFF5DF8D913D2B5789C85C1689B8AD5E3B95DEB0362B098AAC8B2F694864250E85BF1B7CC9B40AD7991332F894A70763A5F1B8A6F009B246EBD2EA9861888A4B82A74E63665BC51A63178D09EB26006B6D651E7006012D44FB74FBD50EA57BA7AEF7A450F91CCAC0FA6FD4FEDD91837195030D754D1458174020A7A08F69C0BBBB2BF7A8DD73A84045428A5FEFD5B650FEB7AD476AA48007D83B657D2952FEE6D8A82525AA845AA8C2B7E0DC63C1B74227618660CBA4FA7FE07C20DDB85F9C36BB1F7591579E02AB26761E09E6AC290D89D6E53A01806A46C9D599B7ADC1D5"
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
