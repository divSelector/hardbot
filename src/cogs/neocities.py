import discord
from constants import channel_names
from discord.ext import commands
from mixins import CommonCogMixin
import requests
from bs4 import BeautifulSoup
import time
import re

class Neocities(commands.Cog, CommonCogMixin):
    """
    Neocities related commands
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="neocities", invoke_without_command=True)
    async def neocities(self, ctx):
        """Base command: shows help if no subcommand is used."""
        await ctx.send("Available subcommands: '!neocities get <username>'")

    @neocities.command(name="get")
    async def neocities_get(self, ctx, username: str):
        base_url = "https://neocities.org"
        cache_bust = f"?t={int(time.time())}"
        url = base_url + '/site/' + username + cache_bust
        
        try:
            response = requests.get(url, allow_redirects=False, timeout=5)
        except requests.RequestException as e:
            print(f"❌ Error fetching site: {e}")
            return
        
        if response.status_code == 404:
            await ctx.send(f"User: '{username}' not found.")

        elif response.status_code == 302:
            await ctx.send(f"User: '{username}' has site profile disabled.")

        elif response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            news_item = soup.find(class_="news-item update")
            if not news_item:
                await ctx.send(f"No news updates found for {username}.")
                return

            files_container = news_item.find(class_="files")
            if not files_container:
                await ctx.send(f"No files found in latest update for {username}.")
                return

            first_file = files_container.find(class_="file")
            if not first_file:
                await ctx.send(f"No files found in latest update for {username}.")
                return
            
            link_tag = first_file.find("a")
            img_tag = first_file.find("img")

            if not link_tag or not img_tag:
                await ctx.send(f"Unable to extract link or thumbnail for {username}.")
                return
            
            file_url = link_tag.get("href")
            img_url = base_url + img_tag.get("src")

            embed = discord.Embed(
                title=f"Latest update for {username} on Neocities",
                description=f"[Open {username}'s page on Neocities]({file_url})",
                color=discord.Color.blue()
            )
            embed.set_image(url=img_url)

            await ctx.send(embed=embed)

        else:
            await ctx.send(f"⚠️ Unexpected status {response.status_code} for {username}")


    @neocities.command(name="random")
    async def neocities_random(self, ctx, optional_tag: str = ""):
        base_url = "https://neocities.org/browse?sort_by=random&tag="
        alphanumeric_tag = re.sub(r'[^a-zA-Z0-9]', '', optional_tag)
        cache_bust = f"&t={int(time.time())}"
        url = base_url + alphanumeric_tag + cache_bust

        try:
            response = requests.get(url, allow_redirects=False, timeout=5)
        except requests.RequestException as e:
            print(f"❌ Error fetching site: {e}")
            return
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            website_gallery = soup.find(class_="website-Gallery")
            if not website_gallery:
                await ctx.send(f"❌ Failed to locate website-Gallery element on page.")

        first_li = website_gallery.find("li")
        if not first_li:
            await ctx.send("❌ No website found.")
            return
        
        a_tag = first_li.find("a", class_="neo-Screen-Shot")
        href = a_tag["href"]
        title = a_tag["title"]

        style = first_li.find("span", class_="img-Holder")["style"]
        screenshot_url = "https://neocities.org" + re.search(r'url\((.*?)\)', style).group(1)

        tags = [t.get_text(strip=True) for t in first_li.select(".site-tags a")]
        tags_str = ", ".join(tags)

        print(href, title, screenshot_url, tags_str)
        embed = discord.Embed(
            title=f"Found a random site on neocities{f" in #{optional_tag}!" if optional_tag else "!"}",
            description=(
                f"**Title:** [{title}]({href})\n"
                f"**URL:** {href}\n"
                f"**Tags:** {tags_str if tags_str else 'None'}"
            ),
            color=discord.Color.blue()
        )
        embed.set_image(url=screenshot_url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Neocities(bot))
