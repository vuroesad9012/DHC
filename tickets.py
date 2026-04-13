import discord
from discord import app_commands
from discord.ext import commands
from views.ticket_views import TicketPanelView
import os


class TicketsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_staff_role(self) -> app_commands.check:
        """Check if user has staff role"""
        async def predicate(interaction: discord.Interaction) -> bool:
            staff_role_id = int(os.getenv("STAFF_ROLE_ID", "0"))
            owner_role_id = int(os.getenv("OWNER_ROLE_ID", "0"))
            
            if staff_role_id == 0:
                return True  # If no role ID set, allow everyone (development mode)
            
            if interaction.user.guild_permissions.administrator:
                return True  # Admins can use it
            
            staff_role = discord.utils.get(interaction.guild.roles, id=staff_role_id)
            owner_role = discord.utils.get(interaction.guild.roles, id=owner_role_id)
            
            if (staff_role and staff_role in interaction.user.roles) or (owner_role and owner_role in interaction.user.roles):
                return True
            
            await interaction.response.send_message("❌ No role", ephemeral=True)
            return False
        
        return predicate

    def has_owner_role(self) -> app_commands.check:
        """Check if user has owner role"""
        async def predicate(interaction: discord.Interaction) -> bool:
            owner_role_id = int(os.getenv("OWNER_ROLE_ID", "0"))
            if owner_role_id == 0:
                return True  # If no role ID set, allow everyone (development mode)
            
            if interaction.user.guild_permissions.administrator:
                return True  # Admins can use it
            
            owner_role = discord.utils.get(interaction.guild.roles, id=owner_role_id)
            if owner_role and owner_role in interaction.user.roles:
                return True
            
            await interaction.response.send_message("❌ No role", ephemeral=True)
            return False
        
        return predicate

    @app_commands.command(name="panel", description="Create a ticket panel")
    @app_commands.check(lambda interaction: TicketsCog(None).has_owner_role()(interaction))
    async def panel(self, interaction: discord.Interaction):
        """Create a ticket panel - Owner only"""
        # Verify owner role
        owner_role_id = int(os.getenv("OWNER_ROLE_ID", "0"))
        if owner_role_id != 0:
            owner_role = discord.utils.get(interaction.guild.roles, id=owner_role_id)
            if owner_role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ No role", ephemeral=True)
                return
        
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(
            title="Support Tickets",
            description="Click the button below to create a support ticket.",
            color=discord.Color.blue()
        )
        await interaction.channel.send(embed=embed, view=TicketPanelView())
        await interaction.followup.send("Successfully created panel", ephemeral=True)


async def setup(bot):
    await bot.add_cog(TicketsCog(bot))
