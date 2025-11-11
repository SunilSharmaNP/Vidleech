# bot/helper/telegram_helper/status_buttons.py

from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.mirror_utils.status_utils import MirrorStatus

# Group task categories for better filtering in UI
TASK_CATEGORIES = {
    "📂 Download": [
        MirrorStatus.STATUS_DOWNLOADING, MirrorStatus.STATUS_CLONING,
        MirrorStatus.STATUS_QUEUEDL
    ],
    "⬆ Upload": [
        MirrorStatus.STATUS_UPLOADING, MirrorStatus.STATUS_QUEUEUP,
        MirrorStatus.STATUS_SEEDING
    ],
    "🎞 Video Tools": [
        MirrorStatus.STATUS_TRIM, MirrorStatus.STATUS_CONVERT,
        MirrorStatus.STATUS_WATERMARK, MirrorStatus.STATUS_MERGING,
        MirrorStatus.STATUS_SUBSYNC, MirrorStatus.STATUS_SAMVID
    ],
    "📦 Archive/Extract": [
        MirrorStatus.STATUS_COMPRESS, MirrorStatus.STATUS_ARCHIVING,
        MirrorStatus.STATUS_EXTRACTING, MirrorStatus.STATUS_SPLITTING
    ],
    "⚙ Others": [
        MirrorStatus.STATUS_METADATA, MirrorStatus.STATUS_WAIT,
        MirrorStatus.STATUS_RMSTREAM, MirrorStatus.STATUS_CHECKING
    ]
}


def build_status_filter_buttons(user_id: int, current_status: str = 'All'):
    """
    Build a structured inline keyboard for task filters.
    """
    buttons = ButtonMaker()

    # Main Header Buttons
    buttons.button_data('♻ Refresh', f'status {user_id} ref', 'header')
    buttons.button_data('❌ Close', f'status {user_id} cls', 'header')

    # “All Tasks” Button
    buttons.button_data('🧩 All Tasks', f'status {user_id} st All')

    # Add category groups dynamically
    for label, statuses in TASK_CATEGORIES.items():
        data = '|'.join(statuses)
        selected = '✅' if current_status in statuses else ''
        buttons.button_data(f'{label} {selected}',
                            f'status {user_id} cat {data}')

    return buttons.build_menu(2)
