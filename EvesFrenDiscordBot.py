import discord
import random
import json
import requests
import datetime

# EVE'S FREN BOT

# INSERT YOUR API KEYS HERE
my_discord_api_key = ""
opensea_api_key = ""

# LOAD CLIENT
client = discord.Client()

# LOAD EMOJI DICT
with open('emojis.json', encoding="utf8") as json_file:
    emoji_data = json.load(json_file)
emoji_dict = emoji_data

# LOAD REACTIONS DICT
with open('reactions.json', encoding="utf8") as json_file:
    reactions_data = json.load(json_file)
reactions_dict = reactions_data


# GET TRENDING COINS
def get_trending_coins():
    api_url = "https://api.coingecko.com/api/v3/search/trending"
    try:
        data = requests.get(api_url).json()
    except Exception as e:
        print(e)
        data = {"coins": [{"item":{"id":"none","name":"Not found","symbol":"?","market_cap_rank":0,"thumb":""}}],"exchanges": []}
    return data


# CONVERT ETH TO USD BY USING CURRENT PRICE FROM COINGECKO
def convert_eth_to_usd(quantity_eth):
    api_url = "https://api.coingecko.com/api/v3/coins/ethereum"
    data = requests.get(api_url).json()
    eth_price = data['market_data']['current_price']['usd']
    eth_price = round(float(eth_price), 2)
    price_usd = eth_price * quantity_eth
    return price_usd


# GET RAT MILK BALANCE
def get_rat_milk_balance(wallet_address):
    url = "https://www.theweirdos.com/api/participant?wallet=" + wallet_address
    balance = requests.request("GET", url).json()[0]['amount']
    if balance:
        return balance
    else:
        return None


# GET OPENSEA COLLECTION
def get_os_collection(slug):
    url = "https://api.opensea.io/api/v1/collection/" + slug + "/"
    headers = {"Accept": "application/json"}
    data = requests.request("GET", url, headers=headers).json()['collection']
    name = data['name']
    image = data['image_url']
    featured_image = data['featured_image_url']
    banner_image = data['banner_image_url']
    floor_price = data['stats']['floor_price']
    one_day_sales = int(data['stats']['one_day_sales'])
    total_supply = int(data['stats']['total_supply'])
    total_volume = data['stats']['total_volume']
    return name, image, featured_image, banner_image, floor_price, one_day_sales, total_supply, total_volume


# GET COINGECKO COIN
def get_coingecko_coin(url):
    data = requests.get(url).json()
    name = data['name']
    symbol = data['symbol']
    coin_price = data['market_data']['current_price']['usd']
    large_image = data['image']['large']
    mc = data['market_data']['market_cap']['usd']
    mc_rank = data['market_cap_rank']
    mc = f"{mc:,}"
    price_change_percentage_1h_in_currency = str(round(data['market_data']['price_change_percentage_1h_in_currency']['usd'], 2)) + " %"
    price_change_percentage_24h_in_currency = str(round(data['market_data']['price_change_percentage_24h_in_currency']['usd'], 2)) + " %"
    coin_price = "**" + str(round(float(coin_price), 2)) + " USD**"
    return name, symbol, coin_price, large_image, mc_rank, mc, price_change_percentage_1h_in_currency, price_change_percentage_24h_in_currency


# GET OPENSEA TOP10 SOLD COLLECTIONS IN LAST 5 MINUTES
def get_top10_sales_5min():
    five_minutes_ago = (datetime.datetime.now() - datetime.timedelta(minutes=5, microseconds=0))
    timestamp_5_min_ago = str(five_minutes_ago.timestamp()).split(".")[0]
    all_sales = {}

    def get_sales(five_min_ago, next=""):
        if not next:
            url = "https://api.opensea.io/api/v1/events?event_type=successful&only_opensea=true&occurred_after=" + five_min_ago
        else:
            url = "https://api.opensea.io/api/v1/events?event_type=successful&only_opensea=true&occurred_after=" + five_min_ago + "&cursor=" + next
        headers = {"Accept": "application/json", "X-API-KEY": opensea_api_key}
        response = requests.request("GET", url, headers=headers)
        data = response.json()
        next = data['next']
        sales = data['asset_events']

        for sale in sales:
            if sale['payment_token']:
                collection_slug = sale['collection_slug']

                price = (int(sale['total_price'])) / 10 ** 18

                # FILTER OUT ITEMS WITH PRICE LOWER THAN 0.05
                if price > 0.05:

                    # CONSTRUCT ALL SALES DICTIONARY
                    if collection_slug in all_sales:
                        sales_number = all_sales[collection_slug]['sales']
                        sales_number = sales_number + 1
                        all_sales[collection_slug]['sales'] = sales_number

                    else:
                        all_sales[collection_slug] = {'sales': 1}

        if not next:
            return
        else:
            get_sales(five_min_ago, next=next)

    get_sales(timestamp_5_min_ago)
    sorted_by_sales = dict(sorted(all_sales.items(), key=lambda item: item[1]['sales'], reverse=True))
    thetop10 = {k: sorted_by_sales[k] for k in list(sorted_by_sales)[:10]}
    return thetop10


# ON THE BOT START
@client.event
async def on_ready():
    for guild in client.guilds:
        print(
            f'{client.user} is connected to the following guilds:\n'
            f'{guild.name}(id: {guild.id})'
        )


# WHEN THE MESSAGE HAPPENS
@client.event
async def on_message(message):

    # BOT IGNORES IT'S OWN MESSAGES!
    if message.author == client.user:
        return

    # GAS PRICE FEATURE
    if "!gwei" in message.content.lower():

        await message.add_reaction("⛽")
        response = requests.get("https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=" + opensea_api_key)
        data = response.json()

        last_block = data['result']['LastBlock']
        safe_gas_price = data['result']['SafeGasPrice']
        proposed_gas_price = data['result']['ProposeGasPrice']
        fast_gas_price = data['result']['FastGasPrice']

        currentgwei = int(safe_gas_price)
        response2 = requests.get("https://api.etherscan.io/api?module=stats&action=ethprice&apikey=" + opensea_api_key)
        data2 = response2.json()

        ethusd = data2['result']['ethusd']
        print("[ETH PRICE] " + str(ethusd) + "USD")

        gweiusdprice = float((10 ** -9) * float(currentgwei) * float(ethusd))
        print("[GWEI PRICE] " + str(gweiusdprice) + "USD")

        # EMBED
        embed = discord.Embed()
        embed.add_field(name="Last block", value=str(last_block), inline=True)
        embed.add_field(name="Safe gas price", value=str(safe_gas_price) + " GWEI", inline=False)
        embed.add_field(name="Proposed gas price", value=str(proposed_gas_price) + " GWEI", inline=False)
        embed.add_field(name="Fast gas price", value=str(fast_gas_price) + " GWEI", inline=False)
        embed.add_field(name="ETH price", value=str(ethusd) + " USD", inline=True)
        embed.add_field(name="GWEI price", value=str(gweiusdprice) + " USD", inline=True)

        await message.channel.send(embed=embed)

    # HUMAN FEATURE
    if "!human" in message.content.lower():
        await message.add_reaction("🌇")
        number = message.content.lower().split(" ")[1]
        image_url = "https://storage.googleapis.com/humans-metaverse/images-final/" + str(number) + ".png"
        salary_url = "https://api.kriptorog.org/hotm/" + str(number)  # {"job": "Teacher", "unclaimed": "1435.71"}
        opensea_link = "https://opensea.io/assets/0x8a9ece9d8806eb0cde56ac89ccb23a36e2c718cf/" + str(number)

        data = requests.get(salary_url).json()
        job = data['job']
        unclaimed = data['unclaimed']

        # EMBED
        embed = discord.Embed()
        embed.set_image(url=image_url)
        embed.add_field(name="HOTM", value="HUMAN #" + str(number), inline=False)
        embed.add_field(name="JOB", value=job, inline=True)
        embed.add_field(name="UCLAIMED $HOTM", value=unclaimed, inline=True)
        embed.add_field(name="Opensea", value=f"[OpenSea LINK]({opensea_link})", inline=False)
        await message.channel.send(embed=embed)
        print("!human")

    # RANDOM HUMAN FEATURE
    if "!random" in message.content.lower():

        await message.add_reaction("🌇")

        number = random.randint(0, 6499)
        image_url = "https://storage.googleapis.com/humans-metaverse/images-final/" + str(number) + ".png"
        salary_url = "https://api.kriptorog.org/hotm/" + str(number)  # {"job": "Teacher", "unclaimed": "1435.71"}
        opensea_link = "https://opensea.io/assets/0x8a9ece9d8806eb0cde56ac89ccb23a36e2c718cf/" + str(number)

        data = requests.get(salary_url).json()
        job = data['job']
        unclaimed = data['unclaimed']

        # EMBED
        embed = discord.Embed()
        embed.set_image(url=image_url)
        embed.add_field(name="RANDOM HUMAN", value="HUMAN #" + str(number), inline=False)
        embed.add_field(name="JOB", value=job, inline=True)
        embed.add_field(name="UCLAIMED $HOTM", value=unclaimed, inline=True)
        embed.add_field(name="Opensea", value=f"[OpenSea LINK]({opensea_link})", inline=False)
        await message.channel.send(embed=embed)
        print("!random")

    # EMOJI DICT FEATURE
    for key, value in emoji_dict.items():
        if key in message.content.lower():
            print(value)
            await message.add_reaction(value)

    # REACTIONS DICT FEATURE
    for key, value in reactions_dict.items():
        if key in message.content.lower():
            print(key)
            await message.channel.send(value)

    # COINGECKO TRENDING COINS
    if "!gecko" in message.content.lower():

        coins = get_trending_coins()['coins']
        composition = ""
        count = 0
        for coin in coins:
            count = count + 1
            coin_id = coin['item']['id']
            name = coin['item']['name']
            symbol = coin['item']['symbol']
            mc_rank = coin['item']['market_cap_rank']
            urled_slug = "https://www.coingecko.com/en/coins/" + coin_id
            # thumb = coin['item']['thumb']
            inject = f"{count}. symbol: {symbol} | id: [{coin_id}]({urled_slug}) | name: {name} | mc_rank: {mc_rank}"
            composition = composition + inject + "\n"

        # CREATE EMBED
        embed = discord.Embed()
        embed.add_field(name="🔥🦎🦎🦎 COINGECKO TRENDING COINS 🦎🦎🦎🔥", value=composition, inline=False)
        embed.set_footer(text="try !coin id for more info, and remember ALWAYS DYOR!")
        await message.add_reaction("🦎")
        await message.channel.send(embed=embed)
        print("!gecko")

    # TOP10 OPENSEA COLLECTIONS IN THE LAST 5 MINUTES FEATURE
    if "!hot" in message.content.lower():

        await message.add_reaction("⏳")
        top10 = get_top10_sales_5min()

        # CREATE EMBED
        embed = discord.Embed()

        print("TOP 10 OPENSEA SALES IN THE LAST 5 MINUTES")
        count = 0
        composition = ""
        for single in top10.items():
            count = count + 1
            slug = single[0]
            sales = single[1]['sales']
            urled_slug = "https://opensea.io/collection/" + slug
            inject = f"{count}. [{slug}]({urled_slug})" + " " + str(sales) + " sales"
            composition = composition + inject + "\n"

        # SEND MESSAGE
        embed.add_field(name="🔥 TOP 10 OPENSEA COLLECTIONS IN THE LAST 5 MINUTES 🔥", value=composition, inline=False)
        embed.set_footer(text="ALWAYS DYOR!")
        await message.remove_reaction("⏳", client.user)
        await message.add_reaction("✅")
        await message.channel.send(embed=embed)

    # RAT MILK BALANCE FEATURE
    if "!milk" in message.content.lower():
        milk_wallet = message.content.lower().split(" ")[1]
        milk_balance = get_rat_milk_balance(milk_wallet)
        if milk_balance:
            await message.add_reaction("🥛")
            await message.channel.send("**" + str(milk_balance) + " ml**" + " of rat melk!")

    # OPENSEA FLOOR FEATURE
    if "!floor" in message.content.lower():
        search_term = message.content.lower().split(" ")[1]
        print(search_term)
        name, image, featured_image, banner_image, floor_price, one_day_sales, total_supply, total_volume = get_os_collection(search_term)
        in_usd = round(convert_eth_to_usd(floor_price), 2)

        # CREATE EMBED
        embed = discord.Embed()
        embed.set_author(name=name, icon_url=image)  # working :)
        embed.set_thumbnail(url=image)
        embed.add_field(name="OS Floor Price", value="**" + str(floor_price) + " ETH** (" + str(in_usd) + " USD)", inline=False)
        embed.add_field(name="24h sales", value=str(one_day_sales), inline=True)
        embed.add_field(name="Total Supply", value=str(total_supply), inline=True)
        embed.add_field(name="Total Volume", value=str(total_volume) + " ETH", inline=True)
        embed.set_image(url=banner_image)

        # SEND MESSAGE
        await message.channel.send(embed=embed)

    # COINGECKO COIN FEATURE
    if "!coin" in message.content.lower():
        search_term = message.content.lower().split(" ")[1]
        print(search_term)
        api_url = "https://api.coingecko.com/api/v3/coins/" + search_term
        name, symbol, coin_price, large_image, mc_rank, mc, price_change_percentage_1h_in_currency, price_change_percentage_24h_in_currency = get_coingecko_coin(api_url)

        # CREATE EMBED
        embed = discord.Embed(title=name, description="symbol: " + symbol)
        embed.set_thumbnail(url=large_image)
        embed.add_field(name="Price", value=coin_price, inline=False)
        embed.add_field(name="MC", value=mc, inline=True)
        embed.add_field(name="Rank", value=mc_rank, inline=True)
        embed.add_field(name="1h change", value=price_change_percentage_1h_in_currency, inline=False)
        embed.add_field(name="24h change", value=price_change_percentage_24h_in_currency, inline=True)

        # SEND EMBED TO DISCORD
        await message.channel.send(embed=embed)

    # DICE FEATURE
    if message.content == "!roll":
        roll = random.randint(1, 6)
        await message.add_reaction("🎲")
        await message.channel.send("Result: " + "**" + str(roll) + "**")

    # SIMPLE MATH OPERATIONS FEATURE
    operations = ["+", "-", "*", "/"]
    for operation in operations:
        if operation in message.content:
            try:
                fullmsg = message.content
                values = fullmsg.split(operation)
                x = values[0]
                y = values[1]
                if operation == "+":
                    result = float(x) + float(y)
                elif operation == "-":
                    result = float(x) - float(y)
                elif operation == "*":
                    result = float(x) * float(y)
                elif operation == "/":
                    result = float(x) / float(y)
                else:
                    # THIS IS IMPOSSIBLE LOL
                    result = "error"
                await message.add_reaction("🧮")
                await message.channel.send("Result: " + "**" + str(result) + "**")
            # NO TIME TO DO IT BETTER (EVERYTHING DONE ON THE FLY, BUT THIS DOES THE JOB)
            except:
                pass

# RUN THE BOT
client.run(my_discord_api_key)
