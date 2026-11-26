from enum import member

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
    @commands.has_any_role(role_names.owner, role_names.admin)
    async def delete_messages(self, ctx, number_of_messages: int):
        """
        Can delete a large volume of messages at once.
        Example: !delete 100
        """
        deleted = await ctx.channel.purge(limit=number_of_messages + 1)
        await ctx.send(f"Deleted {len(deleted)-1} messages", delete_after=5)

    @commands.command(name="nottalkingabout")
    @commands.has_any_role(role_names.can_embed)
    async def not_talking_about(self, ctx, *, text: str):
        """
        chxshire macro
        Example: !nottalkingabout a stupid example about blah blah
        """
        msg = f"i am obviously not talking about **{text}**, you retard. to you, i wish stage 4 cock cancer."
        await ctx.send(msg)

    @commands.command(name="embed")
    @commands.has_any_role(role_names.owner, role_names.admin, role_names.mod)
    async def toggle_embed(self, ctx, member: discord.Member = None):
        """
        Toggle the can-embed role for a user.
        Example: !embed @Username
        """

        if not member:
            await ctx.send("❌ Usage: `!embed @User`")
            return

        role = discord.utils.get(ctx.guild.roles, name="can-embed")

        if not role:
            await ctx.send("❌ 'can-embed' role does not exist.")
            return

        try:
            if role in member.roles:
                await member.remove_roles(
                    role,
                    reason=f"Embed permission removed by {ctx.author}"
                )
                await ctx.send(
                    f"{member.mention} has been stripped of the right to embed."
                )

            else:
                await member.add_roles(
                    role,
                    reason=f"Embed permission granted by {ctx.author}"
                )
                await ctx.send(
                    f"{member.mention} has been bestowed with the right to embed."
                )

        except discord.Forbidden:
            await ctx.send(
                "❌ No permission to modify this role. "
                "Move the bot role above the can-embed role."
            )


    @commands.command(name="retard")
    @commands.has_any_role(role_names.owner, role_names.admin, role_names.mod)
    async def toggle_retard(self, ctx, target: str = None):
        """
        Toggle the retard role for a user.

        Examples:
        !retard @User
        !retard all
        !retard none
        """

        role = discord.utils.get(ctx.guild.roles, name="retard")

        if role is None:
            await ctx.send("❌ 'retard' role does not exist.")
            return

        if target is None:
            await ctx.send("❌ Usage: `!retard @User`, `!retard all`, or `!retard none`")
            return

        target = target.lower()

        # Give everyone the role
        if target == "all":
            count = 0


            len(ctx.guild.members)
            for member in ctx.guild.members:
                if member.bot:
                    continue

                if role not in member.roles:
                    try:
                        await member.add_roles(
                            role,
                            reason=f"Mass assignment by {ctx.author}"
                        )
                        count += 1
                    except discord.Forbidden:
                        pass

            await ctx.send(f"Declared {count} users to be retards.")
            return

        # Remove the role from everyone
        if target == "none":
            count = 0

            for member in ctx.guild.members:
                if role in member.roles:
                    try:
                        await member.remove_roles(
                            role,
                            reason=f"Mass removal by {ctx.author}"
                        )
                        count += 1
                    except discord.Forbidden:
                        pass

            await ctx.send(f"Expunged retard status from {count} users.")
            return

        # Otherwise expect a user mention/ID/name
        try:
            member = await commands.MemberConverter().convert(ctx, target)
        except commands.BadArgument:
            await ctx.send("❌ Usage: `!retard @User`, `!retard all`, or `!retard none`")
            return

        try:
            if role in member.roles:
                await member.remove_roles(
                    role,
                    reason=f"Removed by {ctx.author}"
                )
                await ctx.send(
                    f"{member.mention} has had his retard status expunged."
                )
            else:
                await member.add_roles(
                    role,
                    reason=f"Granted by {ctx.author}"
                )
                await ctx.send(
                    f"{member.mention} has been removed from polite society and declared a retard."
                )

        except discord.Forbidden:
            await ctx.send(
                "❌ No permission to modify this role. "
                "Move the bot role above the retard role."
            )



    @commands.command(name="test")
    @commands.has_any_role(role_names.admin)
    async def toggle_test(self, ctx, target: str = None):
        for member in ctx.guild.members:
            print(member.name)


    @commands.command(name="clone_category")
    @commands.has_any_role(role_names.admin)
    async def clone_category(
        self,
        ctx,
        source_category: discord.CategoryChannel,
        *,
        new_category_name: str
    ):
        print("\n========== CLONE CATEGORY DEBUG ==========")

        overwrites = {}

        for role, overwrite in source_category.overwrites.items():
            if isinstance(role, discord.Role):
                allow, deny = overwrite.pair()

                overwrites[role] = discord.PermissionOverwrite.from_pair(
                    allow,
                    deny
                )

                print(f"[DEBUG] Rebuilt overwrite for {role.name}")

        print(f"[DEBUG] Total overwrites: {len(overwrites)}")

        try:
            new_category = await ctx.guild.create_category(
                name=new_category_name,
                overwrites=overwrites,
                position=source_category.position + 1
            )

            print(f"[SUCCESS] Created category: {new_category.name}")

        except Exception as e:
            print("[FAILED] Category creation")
            print(type(e).__name__)
            print(e)
            return

        for channel in source_category.channels:
            try:
                await channel.clone(category=new_category)
                print(f"[SUCCESS] Cloned channel: {channel.name}")

            except Exception as e:
                print(f"[FAILED] Channel: {channel.name}")
                print(type(e).__name__)
                print(e)

        print("========== DONE ==========")

    
async def setup(bot):
    await bot.add_cog(Administration(bot))