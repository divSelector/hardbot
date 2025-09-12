import discord
from discord.ext import commands
from constants import role_names
from mixins import CommonCogMixin


class Administration(commands.Cog, CommonCogMixin):
    """
    Commands to make admin lives easier and provision abilities to mods without
    giving sweeping permissions.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="delete")
    @commands.has_role(role_names.owner)
    async def delete_messages(self, ctx, number_of_messages: int):
        """
        Can delete a large volume of messages at once.
        Example: !delete 100
        """
        deleted = await ctx.channel.purge(limit=number_of_messages + 1)
        await ctx.send(f"Deleted {len(deleted)-1} messages", delete_after=5)

    @commands.command(name="accept")
    @commands.has_any_role(role_names.owner, role_names.admin)
    async def accept_member(self, ctx, member: discord.Member = None):
        """
        Provision the member role to a new user.
        Example !accept @Username
        """
        if not member:
            await ctx.send("❌ Usage: `!accept @User`")
            return

        role = discord.utils.get(ctx.guild.roles, name=role_names.member)
        if not role:
            await ctx.send(f"❌ '{role_names.member}' role does not exist.")
            return

        if role in member.roles:
            await ctx.send(f"⚠️ {member.mention} already has the {role.name} role.")
            return

        try:
            await member.add_roles(role, reason=f"Accepted by {ctx.author}")
            await ctx.send(f"✅ {member.mention} has been given the {role.name} role.")
        except discord.Forbidden:
            await ctx.send("❌ No permission to add this role. Try moving your HARDBOT role up in the role hierarchy")

    @commands.command(name="reject")
    @commands.has_any_role(role_names.owner, role_names.admin)
    async def reject_member(self, ctx, member: discord.Member = None):
        """
        Remove the member role from a user.
        Example: !reject @Username
        """
        if not member:
            await ctx.send("❌ Usage: `!reject @User`")
            return

        role = discord.utils.get(ctx.guild.roles, name=role_names.member)
        if not role:
            await ctx.send(f"❌ '{role_names.member}' role does not exist.")
            return

        if role not in member.roles:
            await ctx.send(f"⚠️ {member.mention} does not have the {role.name} role.")
            return

        try:
            await member.remove_roles(role, reason=f"Rejected by {ctx.author}")
            await ctx.send(f"✅ {member.mention} has had the {role.name} role removed.")
        except discord.Forbidden:
            await ctx.send("❌ No permission to remove this role. Try moving your HARDBOT role up in the role hierarchy.")


async def setup(bot):
    await bot.add_cog(Administration(bot))