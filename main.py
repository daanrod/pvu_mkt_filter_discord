import asyncio
import os
from datetime import datetime

import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
os.system(f"title PVU - MARKET FILTER DISCORD")
os.system('cls')

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False
bot = commands.Bot(command_prefix='!', intents=intents)

# YOUR BOT TOKEN
TOKEN = os.getenv('TOKEN')

# SPECIF A CHANNEL AND SET THE CHANNEL ID, IT COULD BE ONE OR MORE
CHANNEL_IDS = [os.getenv('CHANNEL_ID_1'), os.getenv('CHANNEL_ID_2')]

# AN AUTH TOKEN FROM PVU WEBSITE
AUTH = os.getenv('AUTH')

# CHOOSE THE EXPECTED PROFIT
EXP_PROFIT = 100

# CHOOSE THE AMOUNT OF PLANT TO BE ANALYZED ON THE MARKETPLACE
FILTER_LIMIT = 100

# SKILL IDS AND BONUS IN $LE WHAT THEY GIVE
skills_points = {
    # id: LE
    '03': 7,
    '13': 6,
    '14': 8,
    '15': 10,
    '26': 7,
    '27': 8,
    '28': 8,
    '47': 11,
    '48': 13,
    '49': 15,
    '51': 10,
    '53': 14,
    '60': 16,
    '61': 18,
    '62': 20,
    '65': 12,
    '68': 12,
    '70': 10,
}

# ZONE SKILL IDS AND THE MULTIPLIERS
zone_skills_points = {
    # id: multpluer
    '03': 2,
    '05': 2,
    '06': 2,
    '07': 4,
    '08': 4,
    '09': 4,
    '10': 4,
    '11': 26,
    '12': 26,
    '13': 8
}

# FUSED ABILITYS AND THEIR BONUS
fused_ability_points = {
    '103': 4,
    '104': 8,
    '105': 4,
    '204': 15,
    '205': 8,
    '203': 8,
    '303': 12,
    '304': 20,
    '305': 12,
    '403': 16,
    '404': 25,
    '405': 16,

}

faction_data = {
    # id: name
    0: "Omega",
    1: "Light",
    2: "Water",
    3: "Electro",
    4: "Wind",
    5: "Fire",
    6: "Metal",
    7: "Dark",
    8: "Parasite",
    9: "Ice",
}

tier_data = {
    'tier1': 'Tier 1',
    'tier2': 'Tier 2',
    'tier3': 'Tier 3',
    'Mythic': 'Mythic'
}


def clock():
    c_time = datetime.now()
    time_readable = c_time.strftime('%H:%M:%S')

    return time_readable


async def market_filter(auth, exp_profit, filter_limit, channel):

    url = f'https://api.plantvsundead.com/plants/on-sale?offset=0&limit={filter_limit}&type=1'

    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Authorization': auth,
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://marketplace.plantvsundead.com',
        'Referer': 'https://marketplace.plantvsundead.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 OPR/98.0.0.0 (Edition std-1)',
        'x-u-a-check': 'Android-Unity-Farm',
    }

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(url, headers=headers) as response:
                    r = await response.json()
                    # print(response.status)
                    # print(r)

            except Exception as e:
                print(F'{clock()} Erro na requisição')
                print(e)
                print(' ')
                continue

            try:
                data = r['data']

                for plant in data:

                    origin = plant['origin']

                    if origin == "fused":
                        fused_ability_id = plant['fusedAbility']['abilityId']
                        fused_ability_desc = plant['fusedAbility']['description']

                    skill_desc = plant['plantSkill']['description']
                    skill_id = plant['plantSkill']['skillId']
                    skill_tier = tier_data[plant['plantSkill']['skillTier']]

                    skill_zone_desc = plant['plantSkillZone']['description']
                    skill_zone_id = plant['plantSkillZone']['skillZoneId']
                    skill_zone_tier = tier_data[plant['plantSkillZone']
                                                ['skillZoneTier']]

                    faction_name = faction_data[plant['plantConfig']['faction']]

                    if skill_id in skills_points and skill_zone_id in zone_skills_points:

                        # MATH
                        plant_stage_1 = plant['plantConfig']['leStage'][0]
                        plant_stage_2 = plant['plantConfig']['leStage'][1]
                        if origin == 'fused' and fused_ability_id in fused_ability_points:
                            plant_stage_1 += fused_ability_points[fused_ability_id]
                            plant_stage_2 += fused_ability_points[fused_ability_id]

                        plant_farm = ((plant_stage_1+plant_stage_2) * 18)/10

                        skill_farm = skills_points[skill_id]
                        zone_skill_farm = zone_skills_points[skill_zone_id]
                        skills_farm = (
                            ((skill_farm * zone_skill_farm*3)*12)/10) * (1 - 0.1)

                        waste_year = 2076/10

                        plant_price = plant['endingPrice']

                        price_filter = ((plant_farm+skills_farm) -
                                        waste_year) - plant_price

                        paid_in = plant_price / \
                            (((plant_farm+skills_farm) - waste_year)/12)

                        if price_filter > exp_profit:
                            msg = (
                                f"**{'='*60}**\n"
                                f"**{clock()} | Plant FOUND!!!**\n"
                                f" \n"
                                f"LINK: https://marketplace.plantvsundead.com/#/plant/{plant['uniqueId']}\n"
                                f"PRICE: **{plant_price}** PVU\n"
                                f"FACTION: **{faction_name}**\n"
                                f"ORIGIN: **{origin.capitalize()}**\n"
                                f"RARITY: **{plant['plantConfig']['rarity'].upper()}**\n"
                                f"\n"
                                F"STAGE 1: **{plant_stage_1}** / STAGE 2: **{plant_stage_2}**\n"
                                f"SKILL TIER: **{skill_tier}** | ZONE SKILL TIER: **{skill_zone_tier}**\n"
                                f"SKILL: **{skill_desc}**\n"
                                f"SKILL ZONE: **{skill_zone_desc}**\n"
                                f"FUSED ABILITY: **{fused_ability_desc}**\n"
                                f"\n"
                                f"PVU PER DAY: **{((plant_farm+skills_farm)-waste_year)/12:.1f}** PVU (with costs)\n"
                                f"PROFIT: **{price_filter:.1f}** PVU profit after 12 days (with costs)\n"
                                f"PAID IN: **{paid_in:.0f}** days\n"
                                '\n'
                                f"**{'='*60}**"
                            )

                            await channel.send(msg)
                            await asyncio.sleep(5)
            except Exception as e:
                print(
                    f"{clock()} | An error occurred:\n{e}")
                await asyncio.sleep(3)
            await asyncio.sleep(1)


@bot.event
async def on_ready():
    print('Bot is ready!')

    for channel_id in CHANNEL_IDS:
        channel = bot.get_channel(int(channel_id))
        bot.loop.create_task(market_filter(
            AUTH, EXP_PROFIT, FILTER_LIMIT, channel))

        start_txt = (
            f"{'='*60}\n"
            f'Time: {clock()}\n'
            f'Starting bot.\n'
            f'Configuration with **{EXP_PROFIT} PVU** profit.\n'
            f"{'='*60}"
        )

        await channel.send(start_txt, delete_after=10)

if __name__ == "__main__":

    bot.run(TOKEN)
