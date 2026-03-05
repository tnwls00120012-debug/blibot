import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio

# ===== 설정 =====
# Render의 '변수(Variables)' 탭에 등록한 이름과 똑같아야 합니다.
TOKEN = os.getenv("DISCORD_TOKEN")

# 채널명에 특수문자가 있다면 똑같이 적어주세요 (예: "📢ㅣ블리-공지사항")
ANNOUNCE_CHANNEL = "블리-공지사항" 

# 사용자님이 깃허브에 올린 음성 파일 이름과 토씨 하나 안 틀리고 똑같아야 합니다.
AUDIO_FILE = "KakaoTalk_Audio_20260305_1207_15_385.m4a"

# 온오프 상태
join_alert_enabled = True

# 등급별 입장 메시지
ROLE_MESSAGES = {
    "매니저": "💎 **{name}** 매니저님이 입장하셨습니다! 환영합니다 👑",
    "서든파티원": "🎮 **{name}** 파티원이 입장! 같이 달려봐요 🔥",
    "찐팬": "💕 **{name}** 찐팬이 들어왔어요~ 반가워요!",
}
DEFAULT_MESSAGE = "👋 **{name}** 님이 음성채널에 입장했습니다!"

# ===== 봇 설정 =====
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ===== 이벤트: 준비 완료 =====
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ 블리봇 온라인! 로그인: {bot.user}")

# ===== 이벤트: 음성채널 입장 알림 (채팅 + 음성파일 재생) =====
@bot.event
async def on_voice_state_update(member, before, after):
    global join_alert_enabled
    if not join_alert_enabled:
        return

    # 누군가 음성 채널에 새로 들어왔을 때만 실행
    if before.channel is None and after.channel is not None:
        # 1. 채팅 알림 보내기
        guild = member.guild
        channel = discord.utils.get(guild.text_channels, name=ANNOUNCE_CHANNEL)
        
        if channel:
            role_names = [r.name for r in member.roles]
            message = DEFAULT_MESSAGE
            for role, msg in ROLE_MESSAGES.items():
                if role in role_names:
                    message = msg
                    break
            await channel.send(message.format(name=member.display_name))

        # 2. 음성 파일 재생하기
        try:
            # 봇이 멤버가 있는 음성 채널로 접속
            vc = await after.channel.connect()
            
            # 깃허브에 올린 파일 재생
            vc.play(discord.FFmpegPCMAudio(AUDIO_FILE))
            
            # 재생이 끝날 때까지 기다림
            while vc.is_playing():
                await asyncio.sleep(1)
            
            # 재생 완료 후 퇴장
            await vc.disconnect()
        except Exception as e:
            print(f"❌ 음성 재생 중 오류 발생: {e}")
            # 에러 발생 시 봇이 채널에 남아있다면 강제 퇴장
            if member.guild.voice_client:
                await member.guild.voice_client.disconnect()

# ===== 슬래시 명령어: /온, /오프, /추방, /차단 =====
@tree.command(name="온", description="음성채널 입장 알림을 켭니다")
@app_commands.checks.has_permissions(manage_guild=True)
async def turn_on(interaction: discord.Interaction):
    global join_alert_enabled
    join_alert_enabled = True
    await interaction.response.send_message("✅ 입장 알림이 **켜졌습니다**!", ephemeral=True)

@tree.command(name="오프", description="음성채널 입장 알림을 끕니다")
@app_commands.checks.has_permissions(manage_guild=True)
async def turn_off(interaction: discord.Interaction):
    global join_alert_enabled
    join_alert_enabled = False
    await interaction.response.send_message("🔕 입장 알림이 **꺼졌습니다**!", ephemeral=True)

@tree.command(name="추방", description="멤버를 서버에서 추방합니다")
@app_commands.describe(member="추방할 멤버", reason="추방 이유")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "이유 없음"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 **{member.display_name}** 님을 추방했습니다. (이유: {reason})")

@tree.command(name="차단", description="멤버를 서버에서 차단(밴)합니다")
@app_commands.describe(member="차단할 멤버", reason="차단 이유")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "이유 없음"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 **{member.display_name}** 님을 차단했습니다. (이유: {reason})")

# ===== 일반 채팅 자동 응답 =====
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    content = message.content.lower()
    if "안녕" in content:
        await message.channel.send(f"안녕하세요 {message.author.display_name}님! 💕")
    elif "블리" in content and "최고" in content:
        await message.channel.send("블리 최고 맞아요!! 🎉")
    await bot.process_commands(message)

# ===== 권한 오류 처리 =====
@turn_on.error
@turn_off.error
@kick.error
@ban.error
async def permission_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ 권한이 없습니다!", ephemeral=True)

# ===== 실행 =====
bot.run(TOKEN
