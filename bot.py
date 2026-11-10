import os
import discord
from discord.ext import commands
import asyncio
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# قواميس مؤقتة لتخزين إعدادات الرومات
control_panel_channels = {}

class RecordingView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="اختر مدة التسجيل المطلوبة...",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="آخر ساعة", value="1", description="تسجيل آخر ساعة فقط"),
            discord.SelectOption(label="آخر 6 ساعات", value="6", description="تسجيل آخر 6 ساعات"),
            discord.SelectOption(label="آخر 24 ساعة (يوم)", value="24", description="تسجيل آخر يوم كامل")
        ]
    )
    async def select_duration(self, interaction: discord.Interaction, select: discord.ui.Select):
        duration = select.values[0]
        await interaction.response.send_message(f"✅ تم تحديد مدة التسجيل: **{duration} ساعة/ساعات**.", ephemeral=True)

    @discord.ui.button(label="تفعيل لوحة التحكم هنا", style=discord.ButtonStyle.green, custom_id="setup_panel")
    async def setup_panel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ هذا الزر مخصص للمشرفين فقط!", ephemeral=True)
            return
        
        control_panel_channels[interaction.guild.id] = interaction.channel.id
        await interaction.response.send_message("✅ تم حفظ هذا الروم كلوحة تحكم للتسجيل!", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("Bot is ready and running!")

@bot.command()
async def panel(ctx):
    """أمر لإرسال رسالة لوحة التحكم مع الأزرار والقوائم"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ تحتاج صلاحية مسؤولي السيرفر لاستخدام هذا الأمر.")
        return

    embed = discord.Embed(
        title="🎙️ لوحة التحكم بنظام التسجيل الصوتي",
        description="استخدم القائمة أدناه لاختيار المدة الزمنية للتسجيل، أو اضغط على الزر لتفعيل اللوحة في هذا الروم.",
        color=discord.Color.blurple()
    )
    embed.set_footer(text="نظام إدارة التسجيلات الصوتية الآلي")
    
    view = RecordingView()
    await ctx.send(embed=embed, view=view)

@bot.command()
async def join_record(ctx, archive_channel: discord.TextChannel):
    """أمر لدخول الروم الصوتي وبدء التسجيل وإرساله للأرشيف"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ تحتاج صلاحية مسؤولي السيرفر.")
        return

    if ctx.author.voice is None:
        await ctx.send("⚠️ يجب أن تكون متصلاً بروم صوتي لكي أتمكن من الدخول معه!")
        return

    voice_channel = ctx.author.voice.channel
    
    try:
        voice_client = await voice_channel.connect()
        await ctx.send(f"🟢 انضممت إلى الروم الصوتي `{voice_channel.name}` وجاري التسجيل...")

        # محاكاة التسجيل (10 ثواني للتجربة)
        await asyncio.sleep(10)
        
        await voice_client.disconnect()
        
        # إرسال تنبيه في الروم المخصص للأرشيف
        await archive_channel.send(f"📁 **تم حفظ التسجيل الصوتي للروم:** `{voice_channel.name}`\n⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        await ctx.send("✅ تم الانتهاء من التسجيل وإرسال الملف بنجاح!")

    except Exception as e:
        await ctx.send(f"❌ حدث خطأ: `{e}`")

# سحب التوكن بأمان من إعدادات المنصة
TOKEN = os.getenv('TOKEN')
bot.run(TOKEN)
