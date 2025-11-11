from pyrogram.types import CallbackQuery
from bot import bot
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import editMessage


@bot.on_callback_query(CustomFilters.authorized & (lambda _, q: q.data and q.data.startswith("runvtool|")))
async def run_video_tool(_, query: CallbackQuery):
    """
    Handles callback presses from the /vtools menu.
    Guides the user to use /mvid or /lvid with their chosen tool.
    """
    try:
        await query.answer()
        tool = query.data.split("|", 1)[1].strip()

        # Safety check: ensure valid tool name
        if not tool:
            await query.answer("Invalid selection!", show_alert=True)
            return

        # Instruction message
        msg_text = (
            f"⚙️ **{tool.title()} Mode Selected**\n\n"
            f"Now send your video link or reply to a message containing the video.\n\n"
            f"To start processing, use one of these commands:\n"
            f"➤ `/mvid <link>`  → Mirror Mode\n"
            f"➤ `/lvid <link>`  → Leech Mode\n\n"
            f"💡 *Example:*\n`/mvid https://example.com/video.mp4`\n\n"
            f"After sending, I’ll automatically apply your selected tool (**{tool}**) 🎬"
        )

        await editMessage(msg_text, query.message)

    except Exception as e:
        await query.answer("⚠️ Something went wrong!", show_alert=True)
        print(f"[VideoTools Callback Error]: {e}")
