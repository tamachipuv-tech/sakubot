import discord
from discord.ext import commands
import os
import random

TOKEN = os.environ['DISCORD_TOKEN']  # Railway の Variables に設定する

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ==============================
# ✅ 募集システム
# ==============================
class RecruitmentView(discord.ui.View):
    def __init__(self, author, game, max_participants, timeout=300):
        super().__init__(timeout=timeout)
        self.author = author
        self.game = game
        self.max_participants = max_participants
        self.participants = []

    @discord.ui.button(label="✅ 参加", style=discord.ButtonStyle.success)
    async def join(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        if user in self.participants:
            await interaction.response.send_message("すでに参加しています！", ephemeral=True)
        elif len(self.participants) >= self.max_participants:
            await interaction.response.send_message("定員に達しています。", ephemeral=True)
        else:
            self.participants.append(user)
            await interaction.response.send_message(f"{user.mention} が参加！（{len(self.participants)}/{self.max_participants}）")

    @discord.ui.button(label="👥 参加者一覧", style=discord.ButtonStyle.secondary)
    async def show_list(self, button: discord.ui.Button, interaction: discord.Interaction):
        if len(self.participants) == 0:
            await interaction.response.send_message("まだ誰も参加していません！", ephemeral=True)
        else:
            members = "\n".join([f"- {user.mention}" for user in self.participants])
            await interaction.response.send_message(
                f"**現在の参加者（{len(self.participants)}/{self.max_participants}）**\n{members}",
                ephemeral=True
            )

    @discord.ui.button(label="🛑 取り消し", style=discord.ButtonStyle.danger)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.author:
            await interaction.response.send_message("この募集を取り消せるのは作成者だけです。", ephemeral=True)
        else:
            await interaction.message.edit(content="❌ 募集は取り消されました。", embed=None, view=None)
            self.stop()

@bot.slash_command(name="募集", description="ゲームの募集を開始します")
async def 募集(ctx, ゲーム: str, 時間: str, 募集人数: int):
    embed = discord.Embed(
        title=f"{ゲーム} の募集",
        description=(
            f"{ctx.author.mention} が {時間} に {ゲーム} を一緒に遊ぶ人を募集しています！\n"
            f"定員: {募集人数}人\n\n下のボタンで参加できます。"
        ),
        color=discord.Color.green()
    )
    await ctx.respond(embed=embed, view=RecruitmentView(ctx.author, ゲーム, 募集人数))


# ==============================
# ✅ BOT 再起動通知コマンド
# ==============================
BOT_ADMIN_IDS = [1398653546563375167]  # 自分のID

@bot.slash_command(name="botrestart", description="BOTを再起動（通知あり）")
async def botrestart(ctx):
    if ctx.author.id not in BOT_ADMIN_IDS:
        await ctx.respond("❌ 管理者専用コマンドです。", ephemeral=True)
        return

    await ctx.respond("🛰️ 再起動通知を送信します…")

    message = "🔁 このBOTはまもなく再起動されます。しばらくお待ちください。"

    for guild in bot.guilds:
        channel = (
            guild.system_channel
            or next((ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages), None)
        )
        if channel:
            await channel.send(message)


# ==============================
# ✅ 通報機能
# ==============================
@bot.slash_command(name="report", description="ユーザーを通報します")
async def report(ctx, 通報対象: discord.Member, 理由: str):
    await ctx.respond("📨 通報を受け付けました。", ephemeral=True)

    REPORT_CHANNEL_ID = 1427605885747724339  # 通報先
    report_channel = bot.get_channel(REPORT_CHANNEL_ID)

    if report_channel:
        embed = discord.Embed(
            title="🚨 通報",
            description=f"**通報者:** {ctx.author.mention}\n**対象:** {通報対象.mention}\n**理由:** {理由}",
            color=discord.Color.red()
        )
        await report_channel.send(embed=embed)


# ==============================
# ✅ 大喜利
# ==============================
OGIRI_PROMPTS = [
    "こんなマイクラの実績は嫌だ。どんな実績？",
    "クリーパーの意外な悩みとは？",
    "エンダードラゴンが実は○○だった！？"
]

@bot.slash_command(name="大喜利", description="大喜利のお題を出します")
async def ogiri(ctx):
    await ctx.respond(f"🗯️ お題：{random.choice(OGIRI_PROMPTS)}")


# ==============================
# ✅ サーバー情報
# ==============================
@bot.slash_command(name="サーバー情報", description="サーバーの情報表示")
async def サーバー情報(ctx):
    guild = ctx.guild
    embed = discord.Embed(title="📊 サーバー情報", color=discord.Color.blurple())
    embed.add_field(name="サーバー名", value=guild.name, inline=False)
    embed.add_field(name="参加人数", value=f"{guild.member_count} 人", inline=False)
    await ctx.respond(embed=embed)


# ==============================
# ✅ 今日のミッション
# ==============================
DAILY_MISSIONS = [
    "クリーパーを爆発させずに倒せ",
    "原木を64個集めよ",
]

@bot.slash_command(name="ミッション", description="今日のミッション")
async def ミッション(ctx):
    await ctx.respond(f"🎯 今日のミッション：**{random.choice(DAILY_MISSIONS)}**")


# ==============================
# ✅ 起動
# ==============================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

bot.run(TOKEN)
