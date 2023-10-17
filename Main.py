# Import required libraries
import discord
from discord.ext import commands
import csv
import os

# Load your bot token from environment variables
my_secret = os.environ['Token']

# Set up Discord intents
intents = discord.Intents.default()
intents.message_content = True

# Define a function to check if a user has a specific role
def is_allowed_role(role_name):
    def predicate(ctx):
        role = discord.utils.get(ctx.author.roles, name=role_name)
        return role is not None
    return commands.check(predicate)

# Create a Discord bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to store user shares
shares = {}

# Dictionary to store user cash balance
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

# Event handler for bot's "on_ready" event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Command to open a new account for a user
@bot.command()
async def open_account(ctx):
    user_id = str(ctx.author.id)
    if user_id not in accounts:
        accounts[user_id] = 0
        save_accounts()  # Save the updated account data to the CSV file
        await ctx.send(embed=discord.Embed(
            title='**Account opened successfully**',
            description="Your account was opened successfully, $100 was deposited into your account automatically",
            color=discord.Color.green())
        )
    else:
        await ctx.send(embed=discord.Embed(
            title='**Error!**',
            description="You already have an account! Use '!balance' to see your account balance.",
            colour=discord.Colour.red())
        )

# Command to provide users with a list of available commands
@bot.command()
async def assistance(ctx):
    embed = discord.Embed(
        title="**Commands:**",
        description="""
        !open_account - *Opens a new account for you.*
        !balance - *Displays your current balance.*
        !withdraw - *Withdraws money from your account.*
        !deposit - *Deposits money into your account.*
        !add_shares - *Bank employees can add your shares you buy into your account.*
        """,
        color=discord.Color.dark_blue()
    )
    await ctx.send(embed=embed)

# Command to withdraw money from user's account
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
                await ctx.send(embed=discord.Embed(
                    title="**Withdrawn**",
                    description=f"Withdrew ${amount} successfully!",
                    color=discord.Color.green()
                ))
            else:
                await ctx.send(embed=discord.Embed(
                    title="**Error!**",
                    description=f"Insufficient funds!",
                    color=discord.Color.red()
                ))
        else:
            await ctx.send(embed=discord.Embed(
                title="**Error!**",
                description=f"Withdrawal must be between $1 and $50,000",
                color=discord.Color.red()
            ))
    else:
        await ctx.send(embed=discord.Embed(
            title="**Error!**",
            description=f"You do not have an account! Use '!open_account' to create an account!",
            color=discord.Color.red()
        ))

# Command to deposit money into user's account
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
            await ctx.send(embed=discord.Embed(
                title="**Success!**",
                description=f"Deposited ${amount} successfully!",
                color=discord.Color.green()
            ))
        else:
            await ctx.send(embed=discord.Embed(
                title="**Error!**",
                description=f"Deposit must be between $1 and $50,000",
                color=discord.Color.red()
            ))
    else:
        await ctx.send(embed=discord.Embed(
            title="**Error!**",
            description=f"You do not have an account! Use '!open_account' to create an account!",
            color=discord.Color.red()
        ))

# Command to display information about available shares
@bot.command()
async def shares(ctx):
    total_shares = 5000  # Total shares available
    taken_shares = 95000

    price_per_share = 6  # Set the price per share

    available_shares = total_shares - taken_shares

    embed = discord.Embed(
        title="Shares Information",
        color=discord.Color.blue()
    )
    embed.add_field(name="Total Shares", value=total_shares, inline=True)
    embed.add_field(name="Taken Shares", value=taken_shares, inline=True)
    embed.add_field(name="Available Shares", value=available_shares, inline=True)
    embed.add_field(name="Price Per Share", value=f"${price_per_share}", inline=True)

    await ctx.send(embed=embed)

# Command to modify share data, accessible only by certain roles
@bot.command()
@is_allowed_role("--C Suite--")
async def sharesmodify(ctx, field: str, value: int):
    if field.lower() == "total":
        total_shares = value
        await ctx.send(embed=discord.Embed(title="**Updated!**", description=f"Total Shares updated to {total_shares}", color=discord.Color.green()))
    elif field.lower() == "taken":
        taken_shares = value
        await ctx.send(embed=discord.Embed(title="**Updated!**", description=f"Taken Shares updated to {taken_shares}", color=discord.Color.green()))
    elif field.lower() == "price":
        price_per_share = value
        await ctx.send(embed=discord.Embed(title="**Updated!**", description=f"Price Per Share updated to {price_per_share}", color=discord.Color.green()))
    else:
        await ctx.send(embed=discord.Embed(title="**Error!**", description="Invalid field. Use 'total', 'taken', or 'price'", color=discord.Color.red()))

# Error handling for sharesmodify command
@sharesmodify.error
async def sharesmodify_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: !sharesmodify [field] [value]")

# Command to add shares to a user's account, accessible only by certain roles
@bot.command()
@is_allowed_role("--C Suite--")
async def add_shares(ctx, user: discord.Member, amount: int):
    user_id = str(user.id)
    if user_id in accounts:
        if user_id in shares:
            shares[user_id] += amount
        else:
            shares[user_id] = amount
        await ctx.send(embed=discord.Embed(
            title="**Added Shares**",
            description=f"Added {amount} shares to {user.mention}'s account.",
            color=discord.Color.green()))
    else:
        await ctx.send(embed=discord.Embed(
            title="**Error!**",
            description=f"{user.mention} does not have an account, they need to use `!open_account` to create one.",
            color=discord.Color.red()))

# Error handling for add_shares command
@add_shares.error
async def add_shares_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(embed=discord.Embed(
            title="**Error!**",
            description="You do not have the required role to use this command.",
            color=discord.Color.red()))

# Command to close a user's account, accessible only by certain roles
@bot.command()
@is_allowed_role("--C Suite--")
async def close_account(ctx):
    user_id = str(ctx.author.id)
    if user_id in accounts:
        del accounts[user_id]
        save_accounts()
        await ctx.send(embed=discord.Embed(
            title="**Account Closed**",
            description=f"Closing {ctx.author.mention}'s account, all information will be deleted.",
            color=discord.Color.green()))

# Command to check user's account balance
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
        await ctx.send(embed=discord.Embed(
            title="**Error!**",
            description="You do not have an account! Use '!open_account' to create an account!",
            color=discord.Color.red()))

# Run the bot using the provided token
bot.run(my_secret)

