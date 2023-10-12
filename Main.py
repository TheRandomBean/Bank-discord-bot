import discord
from discord.ext import commands
import csv  # Import CSV library
import os
my_secret = os.environ['Token']
intents = discord.Intents.default()
intents.message_content = True

# Allows certain users to use commands
def is_allowed_role(role_name):
    def predicate(ctx):
        role = discord.utils.get(ctx.author.roles, name=role_name)
        return role is not None
    return commands.check(predicate)

bot = commands.Bot(command_prefix='!', intents=intents)

shares = {}

# cash balance dictionary
cash_balance = {}

# Load existing account data from a CSV file
accounts = {}
with open('accounts.csv', mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        accounts[row[0]] = int(row[1])

# Function to save account data to a CSV file
def save_accounts():
    with open('accounts.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for user_id, balance in accounts.items():
            writer.writerow([user_id, balance])

# Load transaction log from a CSV file
transaction_log = []
with open('transaction_logs.csv', mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        transaction_log.append(row)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def open_account(ctx):
    user_id = str(ctx.author.id)
    if user_id not in accounts:
        accounts[user_id] = 0
        save_accounts()  # Save the updated account data to the CSV file
        await ctx.send(embed = discord.Embed(
            title='**Account opened successfully',
            description="Your account was opened successfully, $100 was deposited  into your account automaticly",
            color=discord.Color.green())
)
    else:
        await ctx.send(embed = discord.Embed(
            title='**Error!**',
            description="You already have an account! Use '!balance' to see your account balance.",
            colour=discord.Colour.red())
)

@bot.command()
async def assistance(ctx):
  embed = discord.Embed(
    title="**Commands:**",
    description="""
    !open_account - *Opens a new account for you.*
    !balance - *Displays your current balance.*
    !withdraw - *Withdraws money from your account.*
    !deposit - *Deposits money into your account.*
    !add_shares - *So bank employees can add your shares you buy into your account*
    
    """,
    color=discord.Color.dark_blue()
  )
  await ctx.send(embed=embed)

@bot.command()
async def withdraw(ctx, amount: int):
    user_id = str(ctx.author.id)
    if user_id in accounts:
        if 0 < amount <= 50000:
            if accounts[user_id] >= amount:
                accounts[user_id] -= amount
                save_accounts()  # Save the updated account data to the CSV file
                # Add this transaction to the log
                transaction_log.append(f"{ctx.author.id} has withdrawn ${amount}")
                with open('transaction_logs.csv', mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([f"{ctx.author.id} has withdrawn ${amount}"])
                await ctx.send(embed = discord.Embed(
                    title = "**Withdrawn**",
                    description=f"Withdrew ${amount} successfully!",
                    color=discord.Color.green()
                ))
            else:
                await ctx.send(embed = discord.Embed(
                    title = "**Error!**",
                    description=f"Insufficient funds!",
                    color=discord.Color.red()
                ))
        else:
            await ctx.send(embed = discord.Embed(
                title = "**Error!**",
                description=f"Withdrawal must be between $1 and $50,000",
                color=discord.Color.red()
            ))
    else:
        await ctx.send(embed = discord.Embed(
            title = "**Error!**",
            description=f"You do not have an account! Use '!open_account' to create an account!",
            color=discord.Color.red()
        ))

@bot.command()
async def deposit(ctx, amount: int):
    user_id = str(ctx.author.id)
    if user_id in accounts:
        if 0 < amount <= 50000:
            accounts[user_id] += amount
            save_accounts()  # Save the updated account data to the CSV file
            # Add this transaction to the log
            transaction_log.append(f"{ctx.author.id} has deposited ${amount}")
            with open('transaction_logs.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([f"{ctx.author.id} has deposited ${amount}"])
            await ctx.send(embed = discord.Embed(
                title = "**Success!**",
                description=f"Deposited ${amount} successfully!",
                color=discord.Color.green()
            ))
        else:
            await ctx.send(embed = discord.Embed(
                title = "**Error!**",
                description=f"Deposit must be between $1 and $50,000",
                color=discord.Color.red()
            ))
    else:
        await ctx.send(embed = discord.Embed(
            title = "**Error!**",
            description=f"You do not have an account! Use '!open_account' to create an account!",
            color=discord.Color.red()
        ))
@bot.command()
@is_allowed_role("--C Suite--")
async def add_shares(ctx, user: discord.Member, amount: int):
    user_id = str(user.id)
    if user_id in accounts:
        if user_id in shares:
            shares[user_id] += amount
        else:
            shares[user_id] = amount
        await ctx.send(embed= discord.Embed(
            title="**Added Shares**",
            description=f"Added {amount} shares to {user.mention}'s account.",
            color=discord.Color.green()))
    else:
        await ctx.send(embed= dscord.Embed(
            title="**Error!**",
            description=f"*{user.mention} does not have an account, they need to use `!open_account` to create oe.*",
            color=discord.Color.red()))
else:
    await ctx.send(embed= discord.Embed(
        title="**Error!**",
        description="*You do not have the required role to use this command.",
        color=discord.Color.red()))




@bot.command()
async def balance(ctx):
    user_id = str(ctx.author.id)
    if user_id in accounts:
        total_balance = accounts[user_id]
        if user_id in shares:
            shares_balance = shares[user_id]
        else:
            shares_balance = 0
        
        embed = discord.Embed(
            title="**Balance!**",
            description=f"""
            Your Balance: ${accounts[user_id]}
            Your Shares: {shares_balance} shares.
            """,
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send(embed = discord.Embed(


            title = "**Error!**",
            description=f"You do not have an account! Use '!open_account' to create an account!",
            color=discord.Color.red()))

bot.run(my_secret)
