from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import bot
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands


@bot.on_message(CustomFilters.authorized & filters.command(BotCommands.VideoToolsCommand))
async def show_video_tools_menu(_, message: Message):
    buttons = [
        [
            InlineKeyboardButton("🎞 Compress", "runvtool|compress"),
            InlineKeyboardButton("✂ Trim", "runvtool|trim")
        ],
        [
            InlineKeyboardButton("🔇 Mute", "runvtool|mute"),
            InlineKeyboardButton("💧 Watermark", "runvtool|watermark")
        ],
        [
            InlineKeyboardButton("🎵 Add Audio", "runvtool|addaudio"),
            InlineKeyboardButton("🎬 Merge", "runvtool|merge")
        ],
        [InlineKeyboardButton("🔄 Convert", "runvtool|convert")]
    ]

    await message.reply_text(
        "🎬 **Select a Video Tool**\nChoose what you want to do with your video:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
