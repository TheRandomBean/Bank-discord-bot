import discord
from discord import commands

bot = commands.Bot(command_prefix='!')

accounts = {}
shares = {}

transaction_log = []

@bot.event
async def on_ready():
  print(f'Logged in as {bot.user.name}')

@bot.command()
async def open_account(ctx):
  user_id = str(ctx.author.id)
  if user_id not in accounts:
    accounts[user_id] = 0
    await ctx.send("Account opened successfully!")
  else:
    await ctx.send("You already have an account!")

@bot.command()
async def withdraw(ctx, amount: int):
  user_id = str(ctx.author.id)
  if user_id in accounts:
    if 0 < amount <= 50000:
      if accounts[user_id] >= amount:
        accounts[user_id] -= amount
        transaction_log.append(f"{ctx.author.name} withdrew {amount} cash.")
        await ctx.send(f"Withdrew {amount} cash successfully!")
      else:
        await ctx.send("Insufficient funds.Use `!open_account`")
    else:
      await ctx.send("Withdrawal amount must be between 1 and 50,000.")
  else:
    await ctx.send("You dont have an account. Use `!open_account` to create one. ")

bot.run("TOKENID")
