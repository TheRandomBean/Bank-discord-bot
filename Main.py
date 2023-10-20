import discord
from discord import app_commands
from discord.ext import commands
import csv  # Import CSV library
import os

total_shares = 100000
taken_shares = 95000
price = 6

my_secret = os.environ['Token']
# setting up the bot
intents = discord.Intents.all() 
# if you don't want all intents you can do discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

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
      if len(row) >= 2:
          user_id = row[0]
          balance = int(row[1])
          accounts[user_id] = balance
      else:
          # Handle improperly formatted rows (for example, a header row)
          print(f"Skipping improperly formatted row: {row}")

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

@client.event
async def on_ready():
  await tree.sync(guild=discord.Object(id=1153729053321343089))
  print('ready')


@tree.command(name="open", description="Opens a bank account", guild=discord.Object(id=1153729053321343089))
async def open_account(interaction):
    user_id = str(interaction.user.id)  # Use interaction.user.id to get the user's ID

    if user_id not in accounts:
        accounts[user_id] = 100
        save_accounts()  # Save the updated account data to the CSV file
        await interaction.response.send_message(embed=discord.Embed(
            title='**Account opened successfully',
            description="Your account was opened successfully, $100 was deposited into your account automatically",
            color=discord.Color.green())
        )
    else:
        await interaction.response.send_message(embed=discord.Embed(
            title='**Error!**',
            description="You already have an account! Use '!balance' to see your account balance.",
            color=discord.Colour.red()))

@tree.command(name = "help", description = "Gives a list of commands", guild=discord.Object(id=1153729053321343089))
async def assistance(interaction):
  embed = discord.Embed(
    title="**Commands:**",
    description="""
    /open - *Opens a new account for you.*
    /balance - *Displays your current balance.*
    /withdraw - *Withdraws money from your account.*
    /deposit - *Deposits money into your account.*
    /add_shares - *So bank employees can add your shares you buy into your account*

    """,
    color=discord.Color.dark_blue()
  )
  await interaction.response.send_message(embed=embed)

@tree.command(name = "withdraw", description = "Withdraws money from your account", guild=discord.Object(id=1153729053321343089))
async def withdraw(interaction, amount: int):
    user_id = str(interaction.user.id)
    if user_id in accounts:
        if 0 < amount <= 50000:
            if accounts[user_id] >= amount:
                accounts[user_id] -= amount
                save_accounts()  # Save the updated account data to the CSV file
                # Add this transaction to the log
                transaction_log.append(f"{interaction.user.id} has withdrawn ${amount}")
                with open('transaction_logs.csv', mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([f"{interaction.user.id} has withdrawn ${amount}"])
                await interaction.response.send_message(embed = discord.Embed(
                    title = "**Withdrawn**",
                    description=f"Withdrew ${amount} successfully!",
                    color=discord.Color.green()
                ))
            else:
                await interaction.response.send_message(embed = discord.Embed(
                    title = "**Error!**",
                    description=f"Insufficient funds!",
                    color=discord.Color.red()
                ))
        else:
            await interaction.response.send_message(embed = discord.Embed(
                title = "**Error!**",
                description=f"Withdrawal must be between $1 and $50,000",
                color=discord.Color.red()
            ))
    else:
        await interaction.response.send_message(embed = discord.Embed(
            title = "**Error!**",
            description=f"You do not have an account! Use '!open_account' to create an account!",
            color=discord.Color.red()
        ))

@tree.command(name = "deposit", description = "Deposits money into your account", guild=discord.Object(id=1153729053321343089))
@is_allowed_role("--Bank Personnel--")
async def deposit(interaction, amount: int):
    user_id = str(interaction.user.id)
    if user_id in accounts:
        if 0 < amount <= 50000:
            accounts[user_id] += amount
            save_accounts()  # Save the updated account data to the CSV file
            # Add this transaction to the log
            transaction_log.append(f"{interaction.user.id} has deposited ${amount}")
            with open('transaction_logs.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([f"{interaction.user.id} has deposited ${amount}"])
            await interaction.response.send_message(embed = discord.Embed(
                title = "**Success!**",
                description=f"Deposited ${amount} successfully!",
                color=discord.Color.green()
            ))
        else:
            await interaction.response.send_message(embed = discord.Embed(
                title = "**Error!**",
                description=f"Deposit must be between $1 and $50,000",
                color=discord.Color.red()
            ))
    else:
        await interaction.response.send_message(embed = discord.Embed(
            title = "**Error!**",
            description=f"You do not have an account! Use 'open' to create an account!",
            color=discord.Color.red()
        ))
@tree.command(name = "shares", description = "gives information on company shares", guild=discord.Object(id=1153729053321343089))
async def shares(information):
    global total_shares, taken_shares, price

    available_shares = total_shares - taken_shares

    embed = discord.Embed(
        title="Shares Information",
        color=discord.Color.blue()
    )
    embed.add_field(name="Total Shares", value=total_shares, inline=True)
    embed.add_field(name="Taken Shares", value=taken_shares, inline=True)
    embed.add_field(name="Available Shares", value=available_shares, inline=True)
    embed.add_field(name="Price Per Share", value=f"${price}", inline=True)

    await information.response.send_message(embed=embed)

@tree.command(name = "update-shares", description = "Modifies the shares data for the company", guild=discord.Object(id=1153729053321343089))
@is_allowed_role("--C Suite--")
async def sharesmodify(information, field: str, value: int):
    global total_shares, taken_shares, price
  
    if field.lower() == "total":
        total_shares = value
        await information.response.send_message(embed = discord.Embed(title="**Updated!**", description=f"Total Shares updated to {total_shares}'", color=discord.Color.green()))
    elif field.lower() == "taken":
        taken_shares = value
        await information.response.send_message(embed = discord.Embed(title="**Updated!**", description=f"Taken Shares updated too: {taken_shares}'", color=discord.Color.green()))
    elif field.lower() == "price":
        price = value
        await information.response.send_message(embed = discord.Embed(title="**Updated!**", description=f"Price Per Shares updated to ${price}", color=discord.Color.green()))
    else:
        await information.response.send_message(embed = discord.Embed(title="**Error!**", description="Invalid field. Use 'total' 'taken' or 'price'", color=discord.Color.red()))
@sharesmodify.error
async def sharesmodify_error(information, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await information.response.send_message("Usage: /sharesmodify [field] [value]")




@tree.command(name = "balance", description = "shows the balance in your account, including shares", guild=discord.Object(id=1153729053321343089))
async def balance(interaction):
  user_id = str(interaction.user.id)
  if user_id in accounts:
      total_balance = accounts[user_id]
      embed = discord.Embed(
          title="**Balance!**",
          description=f"""
          Your Balance: ${accounts[user_id]}
          """,
          color=discord.Color.blue()
      )
      await interaction.response.send_message(embed=embed)
  else:
      await interaction.response.send_message(embed=discord.Embed(
          title="**Error!**",
          description="You do not have an account! Use '!open_account' to create an account!",
          color=discord.Color.red()
      ))

client.run(my_secret)
