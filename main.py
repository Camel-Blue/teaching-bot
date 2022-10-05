import disnake
from disnake import Status
from disnake.ext import commands, tasks
import asyncio
import requests
import json

intents = disnake.Intents.all()

bot = commands.Bot(command_prefix='.', intents=intents,)

#todo Note that this code is not persistent if we want that then we need to use a csv handler or a database
#Disnake Docs: https://docs.disnake.dev/en/latest/api.html
#Disnake Guid: https://guide.disnake.dev/
#Discord dev aplications: https://discord.com/developers/applications
#Binance api docs: https://binance-docs.github.io/apidocs/spot/en/#symbol-price-ticker

@bot.event
async def on_ready():
	print(f"Logged in as {bot.user} (ID: {bot.user.id})")
	print("------")
	activity = disnake.Activity(type=disnake.ActivityType.watching, name='Coding happen')#Playing, Listening
	await bot.change_presence(activity=activity, status=Status.idle)
	presence_updator.start()
	price_checker.start()

#basic reply command
@bot.command()
async def ping(ctx):#ctx is context aka the channel on witch this command was called and other info: Message author, Guild, etc.
	await ctx.message.delete()#if we don't want to spam the chanel with user sent commands
	await ctx.send(f'Pong!')

#Command with a variable
@bot.command()
async def echo(ctx,* mess):#The * character says that evry input after the previus var is in var mess
	print(type(mess))
	joint_message = " ".join(mess)#We join it here since we get a tuple back
	await ctx.send(f'Echo: {joint_message}')

#Multiple variable command
@bot.command()
async def multi(ctx, num, * mess):
	try:
		int(num)
	except:
		await ctx.send('The second variable has to be a number using base 10.')
		return
	for i in range(int(num)):
		joint_message = " ".join(mess)
		await ctx.send(joint_message)

#Text command group
@bot.group(alias= ['e'])
async def cmd(ctx):
	if ctx.invoked_subcommand is None:
		await ctx.send("This is a group command: `cmd say 'Message'`", delete_after=5)

#Command in the group - cmd
@cmd.command()
async def say(ctx,  * mess):
	joint_message = " ".join(mess)
	sent_message = await ctx.send(f"{ctx.author.mention} made me say: `{joint_message}`")
	await ctx.send(sent_message.id)

#Command in the group - cmd
@cmd.command()
async def edit(ctx, m_id, * mess):
	joint_message = " ".join(mess)
	message = await ctx.channel.fetch_message(int(m_id))#get_message() is for messages in a cache but fetch is for ever!!!
	await message.edit(joint_message)

#Command in the group - cmd
@cmd.command()
async def dell(ctx, m_id):
	message = await ctx.channel.fetch_message(int(m_id))#get_message() is for messages in a cache but fetch is for ever!!!
	await message.delete()

#Slash commands
@bot.slash_command()
async def ping(inter: disnake.AppCmdInter, message):
	"""Test slash command with a simple reply
	Parameters
	----------
	message: The message you want the bot to say
	"""
	await inter.response.send_message(message)#, ephemeral=True
	await asyncio.sleep(3)
	#await inter.delete_original_response()#or you can add a delay here

#Slash commands with multiple responses
@bot.slash_command()
async def adder(inter: disnake.AppCmdInter, num1: int, num2: int):
	"""Test slash command with a simple reply
	Parameters
	----------
	num1: number to have added
	num2: number to be added
	"""
	await inter.response.send_message('Starting calculation', ephemeral=True)
	await asyncio.sleep(3)#Regular time.sleep(3) would block the execution of all other code for the duration
	num3 = num1 + num2#The ^sleep thing symbolizes a long request or execution
	#await inter.response.send_message(f'The result is {num3}', ephemeral=True)#wont work becaus responded to before
	await inter.followup.send(f'The result is **{num3}**', ephemeral=True)

@bot.command()
async def embed(ctx, name):
	embed = disnake.Embed(
		colour=0x42d7f5,
		title=name,
		description="This is a description",
	)
	embed.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar.url)
	embed.add_field(name="Field name", value="Field value", inline=False)
	embed.add_field(name="Empty value", value="** **", inline=False)
	embed.add_field(name="Multi line value", value="Line1\nLine2\nLine3", inline=False)
	#embed.add_field(name="** **", value="Empty name", inline=False)#This will be ugly since you can't realy have a empty name
	embed.set_footer(text='This is a footer')
	embed.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/2011_Trampeltier_1528.JPG/1200px-2011_Trampeltier_1528.JPG')
	embed.set_image(url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/07._Camel_Profile%2C_near_Silverton%2C_NSW%2C_07.07.2007.jpg/1200px-07._Camel_Profile%2C_near_Silverton%2C_NSW%2C_07.07.2007.jpg")
	await ctx.send(embed=embed)

"""
===Crypto_track===
"""
#Global vars for the price tracking
presence_symbol = 'None'
crypto_prices = {}

@tasks.loop(seconds=30)
async def price_checker():
	global crypto_prices
	for symbol in crypto_prices.keys():
		binance = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT')
		price = json.loads(binance.text)['price']
		rounded_price = str(round(float(price), 2))
		crypto_prices[symbol] = rounded_price
		await asyncio.sleep(1) #best practice to not run in to API rate limit

@tasks.loop(seconds=10)
async def presence_updator():
	global crypto_prices, presence_symbol
	if presence_symbol != 'None':
		price = crypto_prices[presence_symbol]
		activity = disnake.Activity(type=disnake.ActivityType.watching, name=f'{presence_symbol}: {price}')#Playing, Listening
		await bot.change_presence(activity=activity)

#Code disregarding api rate limits
'''
@bot.slash_command()
async def price(inter: disnake.AppCmdInter, symbol):
	"""Get the price of a certen crypto
	Parameters
	----------
	symbol: Crypto symbol: BTC, eth
	"""
	global crypto_prices
	await inter.response.defer(ephemeral=True)
	upp_symbol = symbol.upper()
	binance = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={upp_symbol}USDT')
	if "code" not in json.loads(binance.text).keys():
		price = json.loads(binance.text)['price']
		rounded_price = str(round(float(price), 2))
		crypto_prices[upp_symbol] = rounded_price
		await inter.followup.send(f'Price of {upp_symbol} is **{rounded_price}**', ephemeral=True)
	else:
		await inter.followup.send(json.loads(binance.text)['msg'], ephemeral=True)
'''
#command with API limits in mind
@bot.slash_command()
async def price(inter: disnake.AppCmdInter, symbol):
	"""Get the price of a certen crypto
	Parameters
	----------
	symbol: Crypto symbol: BTC, eth
	"""
	global crypto_prices
	await inter.response.defer(ephemeral=True)
	upp_symbol = symbol.upper()
	if upp_symbol not in crypto_prices:
		binance = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={upp_symbol}USDT')
		if "code" not in json.loads(binance.text).keys():
			price = json.loads(binance.text)['price']
			rounded_price = str(round(float(price), 2))
			crypto_prices[upp_symbol] = rounded_price
			await inter.followup.send(f'Price of {upp_symbol} is **{rounded_price}**', ephemeral=True)
		else:
			await inter.followup.send(json.loads(binance.text)['msg'], ephemeral=True)
	else:
		await inter.followup.send(f'Price of {upp_symbol} is **{crypto_prices[upp_symbol]}**', ephemeral=True)

@bot.slash_command()
async def watch(inter: disnake.AppCmdInter, symbol):
	"""Change the crypto the bot is watching
	Parameters
	----------
	symbol: Crypto symbol: BTC, eth
	"""
	global crypto_prices, presence_symbol
	await inter.response.defer(ephemeral=True)
	upp_symbol = symbol.upper()
	binance = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={upp_symbol}USDT')
	if "code" not in json.loads(binance.text).keys():
		price = json.loads(binance.text)['price']
		rounded_price = str(round(float(price), 2))
		crypto_prices[upp_symbol] = rounded_price
		presence_symbol = upp_symbol
		await inter.followup.send('Tracking started', ephemeral=True)
	else:
		await inter.followup.send(json.loads(binance.text)['msg'], ephemeral=True)

"""
===HomeWork? or more like ideas===
1.Update a embed or a message with the prices
2.Read the docs and update a channel with the price
"""

bot.run('Token')