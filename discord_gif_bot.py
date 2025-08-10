import discord
from discord.ext import commands
import json
import os
import random
import asyncio

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# تحميل الإعدادات
def load_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "token": "",
        "allowed_channels": [],
        "gif_urls": [
            "https://media.giphy.com/media/3o7aCSPqXE5C6T8tBC/giphy.gif",
            "https://media.giphy.com/media/l3q2K5jinAlChoCLS/giphy.gif",
            "https://media.giphy.com/media/26BRrSvJUa0crqw4E/giphy.gif",
            "https://media.giphy.com/media/3o6Zt4HU9uwXmXSAuI/giphy.gif",
            "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif"
        ],
        "delay_seconds": 1
    }

# حفظ الإعدادات
def save_config(config):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

config = load_config()

@bot.event
async def on_ready():
    print(f'🤖 البوت {bot.user} جاهز للعمل!')
    print(f'📊 متصل بـ {len(bot.guilds)} سيرفر')
    print(f'🎯 الغرف المفعلة: {len(config["allowed_channels"])}')
    
    # تغيير حالة البوت
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name="الرسائل 👀"
        )
    )

@bot.event
async def on_message(message):
    # تجاهل رسائل البوت نفسه
    if message.author == bot.user:
        return
    
    # التحقق من أن الرسالة في غرفة مسموحة
    if str(message.channel.id) in config["allowed_channels"]:
        # انتظار قليل قبل الرد
        await asyncio.sleep(config["delay_seconds"])
        
        # اختيار GIF عشوائي
        gif_url = random.choice(config["gif_urls"])
        
        # إرسال الـ GIF
        embed = discord.Embed(color=0x00ff88)
        embed.set_image(url=gif_url)
        embed.set_footer(text="🎭 GIF Bot")
        
        await message.channel.send(embed=embed)
    
    # معالجة الأوامر
    await bot.process_commands(message)

@bot.command(name='add_channel')
@commands.has_permissions(administrator=True)
async def add_channel(ctx, channel: discord.TextChannel = None):
    """إضافة غرفة للقائمة المسموحة"""
    if channel is None:
        channel = ctx.channel
    
    channel_id = str(channel.id)
    if channel_id not in config["allowed_channels"]:
        config["allowed_channels"].append(channel_id)
        save_config(config)
        
        embed = discord.Embed(
            title="✅ تم إضافة الغرفة",
            description=f"تم إضافة {channel.mention} للقائمة المسموحة",
            color=0x00ff88
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="⚠️ الغرفة موجودة مسبقاً",
            description=f"{channel.mention} موجودة في القائمة المسموحة",
            color=0xffaa00
        )
        await ctx.send(embed=embed)

@bot.command(name='remove_channel')
@commands.has_permissions(administrator=True)
async def remove_channel(ctx, channel: discord.TextChannel = None):
    """إزالة غرفة من القائمة المسموحة"""
    if channel is None:
        channel = ctx.channel
    
    channel_id = str(channel.id)
    if channel_id in config["allowed_channels"]:
        config["allowed_channels"].remove(channel_id)
        save_config(config)
        
        embed = discord.Embed(
            title="🗑️ تم إزالة الغرفة",
            description=f"تم إزالة {channel.mention} من القائمة المسموحة",
            color=0xff4444
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ الغرفة غير موجودة",
            description=f"{channel.mention} غير موجودة في القائمة المسموحة",
            color=0xff4444
        )
        await ctx.send(embed=embed)

@bot.command(name='list_channels')
@commands.has_permissions(administrator=True)
async def list_channels(ctx):
    """عرض قائمة الغرف المسموحة"""
    if not config["allowed_channels"]:
        embed = discord.Embed(
            title="📋 قائمة الغرف المسموحة",
            description="لا توجد غرف مسموحة حالياً",
            color=0x888888
        )
    else:
        channels_list = []
        for channel_id in config["allowed_channels"]:
            channel = bot.get_channel(int(channel_id))
            if channel:
                channels_list.append(f"• {channel.mention}")
            else:
                channels_list.append(f"• غرفة محذوفة (ID: {channel_id})")
        
        embed = discord.Embed(
            title="📋 قائمة الغرف المسموحة",
            description="\n".join(channels_list),
            color=0x00ff88
        )
    
    await ctx.send(embed=embed)

@bot.command(name='add_gif')
@commands.has_permissions(administrator=True)
async def add_gif(ctx, url: str):
    """إضافة رابط GIF جديد"""
    if url.startswith('http') and ('.gif' in url or 'giphy.com' in url):
        config["gif_urls"].append(url)
        save_config(config)
        
        embed = discord.Embed(
            title="🎭 تم إضافة GIF",
            description=f"تم إضافة الـ GIF الجديد\nالعدد الكلي: {len(config['gif_urls'])}",
            color=0x00ff88
        )
        embed.set_image(url=url)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ رابط غير صحيح",
            description="يرجى إدخال رابط GIF صحيح",
            color=0xff4444
        )
        await ctx.send(embed=embed)

@bot.command(name='set_delay')
@commands.has_permissions(administrator=True)
async def set_delay(ctx, seconds: float):
    """تعديل وقت التأخير قبل إرسال الـ GIF"""
    if 0 <= seconds <= 10:
        config["delay_seconds"] = seconds
        save_config(config)
        
        embed = discord.Embed(
            title="⏱️ تم تحديث التأخير",
            description=f"وقت التأخير الجديد: {seconds} ثانية",
            color=0x00ff88
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ قيمة غير صحيحة",
            description="يجب أن يكون التأخير بين 0 و 10 ثواني",
            color=0xff4444
        )
        await ctx.send(embed=embed)

@bot.command(name='bot_info')
async def bot_info(ctx):
    """معلومات البوت"""
    embed = discord.Embed(
        title="🤖 معلومات البوت",
        color=0x00ff88
    )
    embed.add_field(name="📊 السيرفرات", value=len(bot.guilds), inline=True)
    embed.add_field(name="🎯 الغرف المفعلة", value=len(config["allowed_channels"]), inline=True)
    embed.add_field(name="🎭 عدد الـ GIFs", value=len(config["gif_urls"]), inline=True)
    embed.add_field(name="⏱️ التأخير", value=f"{config['delay_seconds']} ثانية", inline=True)
    embed.set_footer(text="تم التطوير بواسطة Cascade AI")
    
    await ctx.send(embed=embed)

@bot.command(name='help_ar')
async def help_ar(ctx):
    """قائمة الأوامر باللغة العربية"""
    embed = discord.Embed(
        title="📚 قائمة الأوامر",
        description="جميع الأوامر المتاحة للبوت",
        color=0x00ff88
    )
    
    embed.add_field(
        name="🔧 أوامر الإدارة",
        value="""
        `!add_channel [#channel]` - إضافة غرفة للقائمة المسموحة
        `!remove_channel [#channel]` - إزالة غرفة من القائمة
        `!list_channels` - عرض الغرف المسموحة
        `!add_gif <url>` - إضافة GIF جديد
        `!set_delay <seconds>` - تعديل وقت التأخير
        """,
        inline=False
    )
    
    embed.add_field(
        name="📊 أوامر المعلومات",
        value="""
        `!bot_info` - معلومات البوت
        `!help_ar` - هذه القائمة
        """,
        inline=False
    )
    
    embed.set_footer(text="💡 ملاحظة: أوامر الإدارة تحتاج صلاحيات المدير")
    await ctx.send(embed=embed)

# معالجة الأخطاء
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ ليس لديك صلاحية",
            description="تحتاج صلاحيات المدير لاستخدام هذا الأمر",
            color=0xff4444
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CommandNotFound):
        pass  # تجاهل الأوامر غير الموجودة
    else:
        print(f"خطأ: {error}")

if __name__ == "__main__":
    if not config["token"]:
        print("⚠️ يرجى إضافة توكن البوت في ملف config.json")
    else:
        try:
            bot.run(config["token"])
        except discord.LoginFailure:
            print("❌ توكن البوت غير صحيح")
        except Exception as e:
            print(f"❌ خطأ في تشغيل البوت: {e}")
