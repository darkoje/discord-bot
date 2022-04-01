import discord
import random
import json
import requests

# INSERT YOUR OWN DISCORD BOT API HERE
my_discord_api_key = ""

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


# CONVERT ETH TO USD BY USING CURRENT PRICE FROM COINGECKO
def convert_eth_to_usd(quantity_eth):
    api_url = "https://api.coingecko.com/api/v3/coins/ethereum"
    data = requests.get(api_url).json()
    eth_price = data['market_data']['current_price']['usd']
    eth_price = round(float(eth_price), 2)
    price_usd = eth_price * quantity_eth
    return price_usd


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
