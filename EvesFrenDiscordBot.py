import discord
import random
import json
import requests
import datetime

# EVE'S FREN BOT

# INSERT YOUR API KEYS HERE
my_discord_api_key = ""
opensea_api_key = ""
etherscan_api_key = ""


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

    if message.content.lower() == "!roadmap":
        print("!roadmap")
        await message.add_reaction("🗺")
        embed = discord.Embed()
        embed.add_field(name="✅ Q4 2021 **Humans of the Metaverse NFT**", value="Mint Sold out in 14 minutes", inline=True)
        embed.add_field(name="✅ Q1 2022 **Houses and Offices**", value="A never-ending city that provides utility in a fun and engaging way for the holders. A place for other NFT projects to build and create communities.", inline=True)
        embed.add_field(name="✅ Q1 2022 **Land sold out**", value="Land sold out!", inline=True)
        embed.add_field(name="✅ Q1 2022 **Land and buildings new skins**", value="**Land and buildings new skins**", inline=True)
        embed.add_field(name="✅ Q2 2022 **Meta City interface redesign**", value="Redesign the Meta City platform to support easier integrations, analytics, scalability and refactoring.", inline=True)
        embed.add_field(name="✅ Q2 2022 **News**", value="An aggregator for the most relevant projects for our community. it aggregates discord announcements and twitter posts in one place so everyone can have an easier life within this rapidly changing market. On top of that, it will offer a set of the latests posts regarding web3 from trusted sources, such as: Binance blog, Coinbase, etc..", inline=True)
        embed.add_field(name="✅ Q2 2022 **Alpha Club**", value="Exclusive WL and alpha for our community that can bought using $HOTM", inline=True)

        embed.add_field(name="⏱  Q2 2022 **Open-source**",value="We are opening the gates to new developers that can start and build around the core of our infrastructure. Well done development will be rewarded!", inline=True)
        embed.add_field(name="⏱ Q2 2022 **The Oracle**", value="Bigger possibilities in writing the story of your humans.", inline=True)
        embed.add_field(name="⏱ Q2-Q3 2022 **Bank: DAO**", value="We release our DAO contract and fund the contract. The community will be able to submit and vote for initiatives that will funded from the DAO budget.", inline=True)
        embed.add_field(name="⏱ Q3 2022 - **NFT Projects enroll**", value="We release the **B2B** functionality where NFT projects will be able to buy land from secondary markets and setup a community with features exclusively for members of their communities.", inline=True)
        embed.add_field(name="⏱ Q4 2022 - **Museum**", value="Even though NFTs are considered investment assets, art should still be one of the primary sources of interest within this space. The MetaCity Museum will serve as a launchpad for highly talented artists to make a name for themselves.", inline=True)
        embed.add_field(name="⏱ **Future development**", value="**Future development**", inline=True)

        await message.channel.send(embed=embed)

    if message.content.lower() == "!constitution":
        print("!constitution")

        await message.add_reaction("📜")

        embed_intro = discord.Embed()
        embed_intro.set_author(name="Humans of the Metaverse - DAO Constitution")
        text_intro = "This constitution is a framework for governance of the Humans of the Metaverse NFT Community (HOTM). Bylaws are set to identify and limit the power of the DAO. Funds within the DAO treasury shall be prioritized to first protect and ensure the long-term viability of HOTM and second to fund continuing development and improvement of the HOTM community in a manner that benefits all members."
        embed_intro.add_field(name="\u200b", value=text_intro, inline=False)
        await message.channel.send(embed=embed_intro)

        embed = discord.Embed()
        article_1 = """
            The DAO votes will be weighted in this manner;
            Founding Team’s 4 Wallets (each gets 538 votes) 20%
            HOTM Counsel NFT (each gets 61 votes) 20%
            HOTM NFT (each gets 1 vote) - 60%
        """
        embed.add_field(name="📜 Article 1\u200b", value=article_1, inline=False)
        article_2 = " The DAO can vote to allocate funds from the treasury by a simple majority approval of all votes cast where a minimum threshold of half of all eligible votes must be met."
        embed.add_field(name="📜 Article 2", value=article_2, inline=False)
        article_3 = "The DAO can add, modify, or remove articles by a simple majority approval of all votes cast where a minimum threshold of half of all eligible votes must be met."
        embed.add_field(name="📜 Article 3", value=article_3, inline=False)
        article_4 = "The DAO may only vote to dissolve itself by adding an article of dissolution. In the event of a successful vote of dissolution, all DAO holdings will revert back to the Development team."
        embed.add_field(name="📜 Article 4", value=article_4, inline=False)
        article_5 = "The DAO cannot vote to approve any project which would knowingly engage in illegal activity."
        embed.add_field(name="📜 Article 5", value=article_5, inline=False)
        article_6 = "The DAO will have any funds already available to it within the DAO Treasury as well as 50% of all royalties from the HOTM Genesis NFT Collection going forward."
        embed.add_field(name="📜 Article 6", value=article_6, inline=False)
        article_7 = "The DAO cannot remove or modify any of the initial seven articles, if an additional article contradicts one of the initial six articles it cannot be enacted."
        embed.add_field(name="📜 Article 7", value=article_7, inline=False)
        article_8 = """
            a. The Founding Team has 4 wallets that are weighted to each have 5% of any vote that they participate in.
            b. The Founding Team cannot force a vote themselves but have to go to the Voice of the Community to bring votes forward.
            c. The Founding Team cannot withdraw funds from the DAO Treasury
            d. The Founding Team cannot dissolve the DAO
            e. The Founding Team can be hired by the DAO as an outside contractor to work on projects that the DAO has authorized, but they have the right to refuse any work.
                """
        embed.add_field(name="📜 Article 8 - Founding Team", value=article_8, inline=False)
        article_9 = """        
            a. There will be a group of 7 community members elected through popular vote by the DAO twice a year; February and August.
            b. The 7 positions each have different roles to fill:
                1. 2 will be Voices of the Museum
                2. 2 will be Voices of Project Collaboration
                3. 2 will be Voices of Future Development
                4. 1 will be The Voice of the Journalist
            c. If there is ever a vacancy in any of these 7 positions the Founding Team can choose to fill that position with a chosen community member for the remainder of the term, or they can elect to hold a DAO vote for that position.
            d. Any Voice that is absent for more than 30 days will have a recall vote submitted to the DAO. For the member to be recalled a majority must vote in favor and a minimum threshold of 50% of the DAO must vote.
                """
        embed.add_field(name="📜 Article 9 - The Voice of the Community", value=article_9, inline=False)
        article_9b = """
            e. The Voices of the Community will be held to a higher standard, if at any time they are acting in a way inappropriate to their station and the representation of the HOTM community the DAO can start a recall vote with 20 DAO members in agreement. A majority of votes would be needed with a majority of active voters reaching a quorum in order for someone to be recalled from their position as a Voice of the Community.
            f. The Voices of the Community will host a monthly forum open to all members of the DAO which will be announced at least 48 hours in advance.
            g. If any DAO member wishes to bring a vote before the DAO they can petition the Voices of the Community and at least 2 Voices need to stand in approval of the proposal moving forward to a vote.
        """
        embed.add_field(name="\u200b", value=article_9b, inline=False)
        article_10 = """        
            a. Any member of the DAO may bring a vote to the DAO by getting 2 members of the Voice of the Community to support them or 19 additional members of the DAO to support them. 
            b. Members of the DAO will be considered inactive until they vote on a DAO proposal. If a member misses 3 consecutive votes or all votes within a month they will be considered inactive. 
            c. To regain active status within the DAO a member must vote in an active proposal.
            d. Any member of the DAO can submit to become a member of the Voice of the Community by stating intention to run for position at least one week prior to the election.
                """
        embed.add_field(name="📜 Article 10 - DAO Members", value=article_10, inline=False)
        article_11 = """        
            a. There are 2 ways to bring a vote to the DAO. 
                a.i. Any member of the Voice of the Community can bring a vote to the DAO if they get a cosponsor from the other Voices for their vote. 
                a.ii. Any current member of the DAO can bring a vote to the full DAO by securing 19 cosponsors from other members of the DAO or 2 sponsors from the Voices. 
            b. Votes are made publicly on a ballot. A ballot may contain multiple propositions but ballots do not require each proposition be voted in order for the ballot to be counted. 
            c. A vote brought to the DAO by the Voices of the Community can be given as few as 48 hours before the results will be tallied. 
                """
        embed.add_field(name="📜 Article 11 - Voting", value=article_11, inline=False)
        article_11b = """
            d. A spontaneous vote brought by other DAO members will be given as few as 72 hours before the results will be tallied. 
            e. If a vote ever reaches the point where it can no longer be approved or denied, it will immediately pass or fail regardless of the time that has elapsed (ie a vote to pull money from the treasury that reached 51% of total eligible votes in either yay or nay would pass or fail immediately).
            f. Members of the inactive roster will not be considered eligible voters when determining threshold requirements.
        """
        embed.add_field(name="\u200b", value=article_11b, inline=False)
        article_12 = """        
            a. Any project that needs DAO funds or support must be approved through a DAO vote. 
            b. A project cannot have recurring expenses automatically pulled from the DAO Treasury. 
            c. A project cannot continue past the timeline initially voted upon without a petition for an extension that requires a simple majority vote. This only is required if the project is using DAO funds or support. 
            d. Any funded project must demonstrate how it will provide value to the entire community prior to vote. This can be achieved by feeding revenue generated by the project into the DAO fund.
                """
        embed.add_field(name="📜 Article 12 - Projects", value=article_12, inline=False)

        embed.set_footer(text=f"Humans of the Metaverse - DAO Constitution")
        await message.channel.send(embed=embed)

    # GAS PRICE FEATURE
    if message.content.lower() == "!gwei":

        await message.add_reaction("⛽")
        response = requests.get("https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=" + etherscan_api_key)
        data = response.json()

        last_block = data['result']['LastBlock']
        safe_gas_price = data['result']['SafeGasPrice']
        proposed_gas_price = data['result']['ProposeGasPrice']
        fast_gas_price = data['result']['FastGasPrice']
        currentgwei = int(safe_gas_price)

        response2 = requests.get("https://api.etherscan.io/api?module=stats&action=ethprice&apikey=" + etherscan_api_key)
        data2 = response2.json()
        ethusd = data2['result']['ethusd']
        gweiusdprice = float((10 ** -9) * float(currentgwei) * float(ethusd))

        # EMBED
        embed = discord.Embed()
        embed.add_field(name="Last block", value=str(last_block), inline=True)
        embed.add_field(name="Safe gas price", value=str(safe_gas_price) + " GWEI", inline=False)
        embed.add_field(name="Proposed gas price", value=str(proposed_gas_price) + " GWEI", inline=False)
        embed.add_field(name="Fast gas price", value=str(fast_gas_price) + " GWEI", inline=False)
        embed.add_field(name="ETH price", value=str(ethusd) + " USD", inline=True)
        embed.add_field(name="GWEI price", value=str(gweiusdprice) + " USD", inline=True)

        await message.channel.send(embed=embed)
        print("!gwei")

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
    if message.content.lower() == "!random":

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
            await message.add_reaction(value)

    # REACTIONS DICT FEATURE
    for key, value in reactions_dict.items():
        if key in message.content.lower():
            await message.channel.send(value)

    # COINGECKO TRENDING COINS
    if message.content.lower() == "!gecko":
        print("!gecko")
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

    # TOP10 OPENSEA COLLECTIONS IN THE LAST 5 MINUTES FEATURE
    if message.content.lower() == "!hot":

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
