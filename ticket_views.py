import discord
from discord.ui import Select, View, Button, button, Modal, TextInput
from utils.roblox_verify import get_user_id, owns_gamepass
from utils.crypto_verify import check_ltc_payment
import asyncio


class VerifyModal(discord.ui.Modal, title="Roblox Verification"):
    username_input = discord.ui.TextInput(label="Roblox Username", placeholder="Enter your username")

    def __init__(self, dhc_amount: str = None):
        super().__init__()
        self.dhc_amount = dhc_amount

    async def on_submit(self, interaction: discord.Interaction):
        username = self.username_input.value

        user_id = get_user_id(username)
        if not user_id:
            return await interaction.response.send_message("❌ Invalid username.", ephemeral=True)

        if owns_gamepass(user_id, self.dhc_amount):
            await interaction.response.send_message("✅ You are verified!", ephemeral=True)
            
            # Price mapping for conversion
            price_mapping = {
                "1 Million DHC": "$0.50",
                "2 Million DHC": "$1",
                "3 Million DHC": "$1.50",
                "4 Million DHC": "$2",
                "5 Million DHC": "$2.50",
                "6 Million DHC": "$3",
                "7 Million DHC": "$3.50",
                "8 Million DHC": "$4",
                "9 Million DHC": "$4.50",
                "10 Million DHC": "$5",
            }
            
            price = price_mapping.get(self.dhc_amount, "$0")
            
            # Post success message to the ticket channel
            embed = discord.Embed(
                title="Payment Confirmed",
                color=discord.Color.green()
            )
            embed.add_field(name="", value=f"{interaction.user.mention} has successfully paid {price}", inline=False)
            
            await interaction.channel.send(embed=embed)
            # Give role here
        else:
            await interaction.response.send_message("❌ You do NOT own the gamepass.", ephemeral=True)


class VerifyView(View):
    def __init__(self, gamepass_link="https://www.roblox.com", dhc_amount: str = None):
        super().__init__(timeout=None)
        self.gamepass_link = gamepass_link
        self.dhc_amount = dhc_amount
        # Add the link button
        self.add_item(discord.ui.Button(label="Link", style=discord.ButtonStyle.link, url=gamepass_link))

    @button(label="Verify", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(VerifyModal(self.dhc_amount))

    @button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_robux_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        # Delete the channel when close ticket is clicked
        await interaction.channel.delete()


class RobuxAmountSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="1 Million DHC"),
            discord.SelectOption(label="2 Million DHC"),
            discord.SelectOption(label="3 Million DHC"),
            discord.SelectOption(label="4 Million DHC"),
            discord.SelectOption(label="5 Million DHC"),
            discord.SelectOption(label="6 Million DHC"),
            discord.SelectOption(label="7 Million DHC"),
            discord.SelectOption(label="8 Million DHC"),
            discord.SelectOption(label="9 Million DHC"),
            discord.SelectOption(label="10 Million DHC"),
        ]
        super().__init__(placeholder="How Much DHC Would You Like To Buy?", options=options, custom_id="robux_amount")

    async def callback(self, interaction: discord.Interaction):
        selected_amount = self.values[0]
        
        # Gamepass links for each amount
        gamepass_links = {
            "1 Million DHC": "https://www.roblox.com/game-pass/1793235027/1m",
            "2 Million DHC": "https://www.roblox.com/game-pass/1793049674/2m",
            "3 Million DHC": "https://www.roblox.com/game-pass/1793236946/3m",
            "4 Million DHC": "https://www.roblox.com/game-pass/1793017654/4m",
            "5 Million DHC": "https://www.roblox.com/game-pass/1792789930/5m",
            "6 Million DHC": "https://www.roblox.com/game-pass/1793308434/6m",
            "7 Million DHC": "https://www.roblox.com/game-pass/1792871821/7m",
            "8 Million DHC": "https://www.roblox.com/game-pass/1793346367/8m",
            "9 Million DHC": "https://www.roblox.com/game-pass/1793151526/9m",
            "10 Million DHC": "https://www.roblox.com/game-pass/1792917700/10m",
        }
        
        gamepass_url = gamepass_links.get(selected_amount, "https://www.roblox.com")
        
        embed = discord.Embed(
            title="<:robux:1492945659328729149> Robux",
            description="",
            color=discord.Color.blue()
        )
        embed.add_field(name=selected_amount, value=f"Please buy the following gamepass:\n[Gamepass]({gamepass_url})\n\n", inline=False)
        
        view = VerifyView(gamepass_link=gamepass_url, dhc_amount=selected_amount)
        await interaction.response.defer()
        await interaction.message.edit(embed=embed, view=view)


class CryptoSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="LTC"),
        ]
        super().__init__(placeholder="Pick a Crypto", options=options, custom_id="crypto_select")

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="<:crypto:1492947188861636609> Crypto",
            description="Please follow the instructions below to proceed with your purchase.",
            color=discord.Color.blue()
        )
        embed.add_field(name="", value="Select the amount you would like to buy from the dropdown below.", inline=False)
        
        view = CryptoAmountSelectOnlyView()
        await interaction.response.defer()
        await interaction.message.edit(embed=embed, view=view)


class CryptoAmountSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="1 Million DHC"),
            discord.SelectOption(label="2 Million DHC"),
            discord.SelectOption(label="3 Million DHC"),
            discord.SelectOption(label="4 Million DHC"),
            discord.SelectOption(label="5 Million DHC"),
            discord.SelectOption(label="6 Million DHC"),
            discord.SelectOption(label="7 Million DHC"),
            discord.SelectOption(label="8 Million DHC"),
            discord.SelectOption(label="9 Million DHC"),
            discord.SelectOption(label="10 Million DHC"),
        ]
        super().__init__(placeholder="How Much DHC Would You Like To Buy?", options=options, custom_id="crypto_amount")

    async def callback(self, interaction: discord.Interaction):
        selected_amount = self.values[0]
        
        # Price mapping for each DHC amount
        price_mapping = {
            "1 Million DHC": "$0.50",
            "2 Million DHC": "$1",
            "3 Million DHC": "$1.50",
            "4 Million DHC": "$2",
            "5 Million DHC": "$2.50",
            "6 Million DHC": "$3",
            "7 Million DHC": "$3.50",
            "8 Million DHC": "$4",
            "9 Million DHC": "$4.50",
            "10 Million DHC": "$5",
        }
        
        price = price_mapping.get(selected_amount, "$0")
        
        embed = discord.Embed(
            title="<:crypto:1492947188861636609> Crypto",
            color=discord.Color.blue()
        )
        embed.add_field(name=selected_amount, value="", inline=False)
        embed.add_field(name="", value=f"Please send `{price}` to the Crypto address:", inline=False)
        embed.add_field(name="", value="```Lhn5q2eTHtWRi3jJymYZg7CQQeJWqXsXaG```", inline=False)
        
        view = CryptoAmountSelectedView(selected_amount)
        await interaction.response.defer()
        await interaction.message.edit(embed=embed, view=view)


class CryptoAmountView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CryptoAmountSelect())

    @button(label="Verify", style=discord.ButtonStyle.green, custom_id="crypto_verify")
    async def verify(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(VerifyModal())

    @button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_crypto_amount_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        # Delete the channel when close ticket is clicked
        await interaction.channel.delete()


class CryptoAmountSelectOnlyView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CryptoAmountSelect())

    @button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_crypto_select_only_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        # Delete the channel when close ticket is clicked
        await interaction.channel.delete()


class CryptoAmountSelectedView(View):
    def __init__(self, selected_amount: str = ""):
        super().__init__(timeout=None)
        self.selected_amount = selected_amount

    @button(label="Verify", style=discord.ButtonStyle.green, custom_id="crypto_verify")
    async def verify(self, interaction: discord.Interaction, button: Button):
        # Disable button and show waiting message
        await interaction.response.defer()
        
        # Get the selected amount from the embed if not set (for persistence after restart)
        selected_amount = self.selected_amount
        if not selected_amount and interaction.message.embeds:
            embed = interaction.message.embeds[0]
            if embed.fields:
                selected_amount = embed.fields[0].name
        
        embed = discord.Embed(
            title="Crypto",
            color=discord.Color.blue()
        )
        embed.add_field(name=selected_amount, value="", inline=False)
        embed.add_field(name="", value="⏳ Waiting for Blockchain...", inline=False)
        embed.add_field(name="", value="```Lhn5q2eTHtWRi3jJymYZg7CQQeJWqXsXaG```", inline=False)
        
        # Disable the verifybutton while checking
        button.disabled = True
        await interaction.message.edit(embed=embed, view=self)
        
        # Check for payment in background
        def check_payment():
            return check_ltc_payment(selected_amount, timeout=60)
        
        loop = asyncio.get_event_loop()
        payment_found, message = await loop.run_in_executor(None, check_payment)
        
        # Update embed with result
        if payment_found:
            embed = discord.Embed(
                title="Crypto",
                color=discord.Color.green()
            )
            embed.add_field(name=selected_amount, value="", inline=False)
            embed.add_field(name="", value="✅ Payment Detected!", inline=False)
            embed.add_field(name="", value="Thank you for your purchase!", inline=False)
            await interaction.message.edit(embed=embed, view=None)
            
            # Price mapping for conversion
            price_mapping = {
                "1 Million DHC": "$0.50",
                "2 Million DHC": "$1",
                "3 Million DHC": "$1.50",
                "4 Million DHC": "$2",
                "5 Million DHC": "$2.50",
                "6 Million DHC": "$3",
                "7 Million DHC": "$3.50",
                "8 Million DHC": "$4",
                "9 Million DHC": "$4.50",
                "10 Million DHC": "$5",
            }
            
            price = price_mapping.get(selected_amount, "$0")
            
            # Post success message to the ticket channel
            success_embed = discord.Embed(
                title="Payment Confirmed",
                color=discord.Color.green()
            )
            success_embed.add_field(name="", value=f"{interaction.user.mention} has successfully paid {price}", inline=False)
            
            await interaction.channel.send(embed=success_embed)
        else:
            embed = discord.Embed(
                title="Crypto",
                color=discord.Color.red()
            )
            embed.add_field(name=selected_amount, value="", inline=False)
            embed.add_field(name="", value=message, inline=False)
            embed.add_field(name="", value="```Lhn5q2eTHtWRi3jJymYZg7CQQeJWqXsXaG```", inline=False)
            button.disabled = False
            await interaction.message.edit(embed=embed, view=self)

    @button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_crypto_amount_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        # Delete the channel when close ticket is clicked
        await interaction.channel.delete()


class CryptoView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CryptoSelect())

    @button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_crypto_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        # Delete the channel when close ticket is clicked
        await interaction.channel.delete()


class CashAppAmountSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="1 Million DHC"),
            discord.SelectOption(label="2 Million DHC"),
            discord.SelectOption(label="3 Million DHC"),
            discord.SelectOption(label="4 Million DHC"),
            discord.SelectOption(label="5 Million DHC"),
            discord.SelectOption(label="6 Million DHC"),
            discord.SelectOption(label="7 Million DHC"),
            discord.SelectOption(label="8 Million DHC"),
            discord.SelectOption(label="9 Million DHC"),
            discord.SelectOption(label="10 Million DHC"),
        ]
        super().__init__(placeholder="How Much DHC Would You Like To Buy?", options=options, custom_id="cashapp_amount")

    async def callback(self, interaction: discord.Interaction):
        selected_amount = self.values[0]
        
        # Price mapping for each DHC amount
        price_mapping = {
            "1 Million DHC": "$0.50",
            "2 Million DHC": "$1",
            "3 Million DHC": "$1.50",
            "4 Million DHC": "$2",
            "5 Million DHC": "$2.50",
            "6 Million DHC": "$3",
            "7 Million DHC": "$3.50",
            "8 Million DHC": "$4",
            "9 Million DHC": "$4.50",
            "10 Million DHC": "$5",
        }
        
        price = price_mapping.get(selected_amount, "$0")
        
        # Get CashApp tag from environment
        import os
        cashapp_tag = os.getenv("CASHAPP_TAG", "$yourCashAppTag")
        
        embed = discord.Embed(
            title="<:cashapp:1492946600228552964> CashApp",
            color=discord.Color.green()
        )
        embed.add_field(name=selected_amount, value="", inline=False)
        embed.add_field(name="", value=f"Please send `{price}` to the CashApp:", inline=False)
        embed.add_field(name="", value=f"```{cashapp_tag}```", inline=False)
        
        view = CashAppAmountSelectedView(selected_amount)
        await interaction.response.defer()
        await interaction.message.edit(embed=embed, view=view)


class CashAppView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CashAppAmountSelect())

    @button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_cashapp_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        # Delete the channel when close ticket is clicked
        await interaction.channel.delete()


class CashAppAmountSelectedView(View):
    def __init__(self, selected_amount: str = ""):
        super().__init__(timeout=None)
        self.selected_amount = selected_amount
        self.user_verified = False

    @button(label="Verify", style=discord.ButtonStyle.green, custom_id="cashapp_verify")
    async def verify(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("⏳ Please wait for staff to verify your order.", ephemeral=True)
        
        # Update the embed to show waiting for verification
        import os
        cashapp_tag = os.getenv("CASHAPP_TAG", "$yourCashAppTag")
        
        selected_amount = self.selected_amount
        if not selected_amount and interaction.message.embeds:
            embed = interaction.message.embeds[0]
            if embed.fields:
                selected_amount = embed.fields[0].name
        
        embed = discord.Embed(
            title="<:cashapp:1492946600228552964> CashApp",
            color=discord.Color.yellow()
        )
        embed.add_field(name=selected_amount, value="", inline=False)
        embed.add_field(name="", value="⏳ Awaiting Staff Verification", inline=False)
        embed.add_field(name="", value="A staff member will verify your payment shortly.", inline=False)
        
        # Mark that user has verified, disable verify button and show approve button for staff
        button.disabled = True
        self.user_verified = True
        await interaction.message.edit(embed=embed, view=self)

    @button(label="Approve Payment", style=discord.ButtonStyle.success, custom_id="cashapp_approve")
    async def approve_payment(self, interaction: discord.Interaction, button: Button):
        import os
        # Check if user has staff role
        staff_role_id = int(os.getenv("STAFF_ROLE_ID", "0"))
        owner_role_id = int(os.getenv("OWNER_ROLE_ID", "0"))
        
        # Check permissions
        is_staff = False
        if interaction.user.guild_permissions.administrator:
            is_staff = True
        elif staff_role_id != 0:
            staff_role = discord.utils.get(interaction.guild.roles, id=staff_role_id)
            if staff_role and staff_role in interaction.user.roles:
                is_staff = True
        elif owner_role_id != 0:
            owner_role = discord.utils.get(interaction.guild.roles, id=owner_role_id)
            if owner_role and owner_role in interaction.user.roles:
                is_staff = True
        
        if not is_staff:
            await interaction.response.send_message("❌ Only staff can approve payments.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Get the selected amount from the embed
        selected_amount = self.selected_amount
        if not selected_amount and interaction.message.embeds:
            embed = interaction.message.embeds[0]
            if embed.fields:
                selected_amount = embed.fields[0].name
        
        # Price mapping for conversion
        price_mapping = {
            "1 Million DHC": "$0.50",
            "2 Million DHC": "$1",
            "3 Million DHC": "$1.50",
            "4 Million DHC": "$2",
            "5 Million DHC": "$2.50",
            "6 Million DHC": "$3",
            "7 Million DHC": "$3.50",
            "8 Million DHC": "$4",
            "9 Million DHC": "$4.50",
            "10 Million DHC": "$5",
        }
        
        price = price_mapping.get(selected_amount, "$0")
        
        # Update embed to show payment confirmed
        embed = discord.Embed(
            title="<:cashapp:1492946600228552964> CashApp",
            color=discord.Color.green()
        )
        embed.add_field(name=selected_amount, value="", inline=False)
        embed.add_field(name="", value="✅ Payment Verified!", inline=False)
        embed.add_field(name="", value="Thank you for your purchase!", inline=False)
        
        await interaction.message.edit(embed=embed, view=None)
        
        # Post success message to the ticket channel
        success_embed = discord.Embed(
            title="Payment Confirmed",
            color=discord.Color.green()
        )
        # Get the original user from the channel (first message should be from them)
        original_user = None
        async for msg in interaction.channel.history(limit=100, oldest_first=True):
            if msg.author != interaction.client.user:
                original_user = msg.author
                break
        
        if original_user:
            success_embed.add_field(name="", value=f"{original_user.mention} has successfully paid {price}", inline=False)
        else:
            success_embed.add_field(name="", value=f"Payment of {price} has been confirmed.", inline=False)
        
        await interaction.channel.send(embed=success_embed)

    @button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_cashapp_amount_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        # Delete the channel when close ticket is clicked
        await interaction.channel.delete()


class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RobuxAmountSelect())

    @button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        # Delete the channel when close ticket is clicked
        await interaction.channel.delete()


class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Robux", emoji="<:robux:1492945659328729149>"),
            discord.SelectOption(label="CashApp", emoji="<:cashapp:1492946600228552964>"),
            discord.SelectOption(label="Crypto", emoji="<:crypto:1492947188861636609>"),
        ]
        super().__init__(placeholder="Select an option", options=options, custom_id="ticket_select")

    async def callback(self, interaction: discord.Interaction):
        category_name = self.values[0]
        user_name = interaction.user.name
        guild = interaction.guild
        
        await interaction.response.defer()
        
        try:
            # Check if category already exists
            category = discord.utils.get(guild.categories, name=category_name)
            if not category:
                category = await guild.create_category(category_name)
            
            # Create a private channel with the user's name in this category
            # Set permissions so only the user can see it
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True)
            }
            channel = await guild.create_text_channel(user_name, category=category, overwrites=overwrites)
            
            if category_name == "Robux":
                # Send Robux-specific message
                embed = discord.Embed(
                    title="<:robux:1492945659328729149> Robux",
                    description="Please follow the instructions below to proceed with your purchase.",
                    color=discord.Color.blue()
                )
                embed.add_field(name="", value="Select the amount you would like to buy from the dropdown below.", inline=False)
                await channel.send(embed=embed, view=TicketView())
            
            elif category_name == "Crypto":
                # Send Crypto-specific message
                embed = discord.Embed(
                    title="<:crypto:1492947188861636609> Crypto",
                    description="Please follow the instructions below to proceed with your purchase.",
                    color=discord.Color.blue()
                )
                embed.add_field(name="", value="Select the crypto you would like to buy with the dropdown below.", inline=False)
                await channel.send(embed=embed, view=CryptoView())
            
            elif category_name == "CashApp":
                # Send CashApp-specific message
                embed = discord.Embed(
                    title="<:cashapp:1492946600228552964> CashApp",
                    description="Please follow the instructions below to proceed with your purchase.",
                    color=discord.Color.green()
                )
                embed.add_field(name="", value="Select the amount you would like to send from the dropdown below.", inline=False)
                await channel.send(embed=embed, view=CashAppView())
            
            # Send confirmation to user
            embed = discord.Embed(
                title="Ticket created.",
                description=f"Head over to {channel.mention}",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Reset the original message dropdown
            await interaction.message.edit(view=TicketPanelView())
        except Exception as e:
            await interaction.followup.send(f"Error creating ticket: {e}", ephemeral=True)


class TicketPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


class PersistentSelectView(View):
    """Container for persistent select menus"""
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())
        self.add_item(RobuxAmountSelect())
