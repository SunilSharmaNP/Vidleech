from html import escape
from psutil import virtual_memory, cpu_percent, disk_usage, net_io_counters
from pyrogram.types import Message
from time import time
from pytz import timezone

from bot import bot_name, task_dict, task_dict_lock, botStartTime, config_dict
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.button_build import ButtonMaker

SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']


# ============================================================
# 🎬 Mirror / Video Tools Task Status Definitions
# ============================================================
class MirrorStatus:
    STATUS_ARCHIVING = 'Archiving'
    STATUS_CHECKING = 'CheckingUp'
    STATUS_CLONING = 'Cloning'
    STATUS_COMPRESS = 'Compressing'
    STATUS_CONVERT = 'Converting'
    STATUS_SUBSYNC = 'SubSyncing'
    STATUS_DOWNLOADING = 'Downloading'
    STATUS_EXTRACTING = 'Extracting'
    STATUS_MERGING = 'Merging'
    STATUS_PAUSED = 'Paused'
    STATUS_QUEUEDL = 'QueueDl'
    STATUS_QUEUEUP = 'QueueUl'
    STATUS_RMSTREAM = 'Removing'
    STATUS_SAMVID = 'SamVid'
    STATUS_METADATA = 'Metadata'
    STATUS_SEEDING = 'Seeding'
    STATUS_SPLITTING = 'Splitting'
    STATUS_TRIM = 'Trimming'
    STATUS_UPLOADING = 'Uploading'
    STATUS_UPLOADINGTOGO = 'Uploading'
    STATUS_WAIT = 'Waiting'
    STATUS_WATERMARK = 'Watermarking'


STATUS_VALUES = [
    ('ALL', 'All'),
    ('DL', MirrorStatus.STATUS_DOWNLOADING),
    ('UP', MirrorStatus.STATUS_UPLOADING),
    ('QD', MirrorStatus.STATUS_QUEUEDL),
    ('QU', MirrorStatus.STATUS_QUEUEUP),
    ('AR', MirrorStatus.STATUS_ARCHIVING),
    ('EX', MirrorStatus.STATUS_EXTRACTING),
    ('CL', MirrorStatus.STATUS_CLONING),
    ('MG', MirrorStatus.STATUS_MERGING),
    ('CP', MirrorStatus.STATUS_COMPRESS),
    ('CV', MirrorStatus.STATUS_CONVERT),
    ('WM', MirrorStatus.STATUS_WATERMARK),
    ('TR', MirrorStatus.STATUS_TRIM),
    ('SS', MirrorStatus.STATUS_SUBSYNC),
    ('SD', MirrorStatus.STATUS_SEEDING)
]


# ============================================================
# 🧩 Utility Functions
# ============================================================
async def getTaskByGid(gid: str):
    async with task_dict_lock:
        return next((tk for tk in task_dict.values() if tk.gid() == gid), None)


async def getAllTasks(req_status: str):
    async with task_dict_lock:
        if req_status == 'all':
            return list(task_dict.values())
        return [tk for tk in task_dict.values() if tk.status() == req_status]


def get_readable_file_size(size_in_bytes: int | str):
    if isinstance(size_in_bytes, str):
        size_in_bytes = int(size_in_bytes)
    if not size_in_bytes:
        return '0B'
    index = 0
    while size_in_bytes >= 1024 and index < len(SIZE_UNITS) - 1:
        size_in_bytes /= 1024
        index += 1
    return f'{size_in_bytes:.2f}{SIZE_UNITS[index]}' if index > 0 else f'{size_in_bytes:.2f}B'


def get_date_time(message: Message):
    dt = message.date.astimezone(timezone(config_dict['TIME_ZONE']))
    return dt.strftime('%B %d, %Y'), dt.strftime('%H:%M:%S')


def get_readable_time(seconds):
    periods = [('d', 86400), ('h', 3600), ('m', 60), ('s', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)}{period_name} '
    return result.strip()


def speed_string_to_bytes(size_text: str):
    size = 0
    size_text = size_text.lower()
    if 'k' in size_text:
        size += float(size_text.split('k')[0]) * 1024
    elif 'm' in size_text:
        size += float(size_text.split('m')[0]) * 1048576
    elif 'g' in size_text:
        size += float(size_text.split('g')[0]) * 1073741824
    elif 't' in size_text:
        size += float(size_text.split('t')[0]) * 1099511627776
    elif 'b' in size_text:
        size += float(size_text.split('b')[0])
    return size


def get_progress_bar_string(pct: str):
    pct = float(pct.strip('%'))
    p = min(max(pct, 0), 100)
    cFull = int(p // 8)
    cPart = int(p % 8 - 1)
    p_str = '⬤' * cFull
    if cPart >= 0:
        p_str += ['○', '○', '◔', '◔', '◑', '◑', '◕', '◕'][cPart]
    p_str += '○' * (12 - cFull)
    return f"[{p_str}]"


def action(message: Message):
    acts = message.text.split(maxsplit=1)[0]
    return acts.replace('/', '#').replace(f'@{bot_name}', '').replace(str(config_dict['CMD_SUFFIX']), '').lower()


# ============================================================
# 🪄 Enhanced Status Formatter (Premium UI)
# ============================================================
def get_readable_message(sid: int, is_user: bool, page_no: int = 1, status: str = 'All', page_step: int = 1):
    dl_speed = up_speed = 0
    msg = ''

    # Collect matching tasks
    if status == 'All':
        tasks = [tk for tk in task_dict.values() if tk.listener.user_id == sid] if is_user else list(task_dict.values())
    elif is_user:
        tasks = [tk for tk in task_dict.values() if tk.status() == status and tk.listener.user_id == sid]
    else:
        tasks = [tk for tk in task_dict.values() if tk.status() == status]

    STATUS_LIMIT = config_dict['STATUS_LIMIT']
    tasks_no = len(tasks)
    pages = (max(tasks_no, 1) + STATUS_LIMIT - 1) // STATUS_LIMIT
    if page_no > pages:
        page_no = (page_no - 1) % pages + 1
    elif page_no < 1:
        page_no = pages - (abs(page_no) % pages)
    start_position = (page_no - 1) * STATUS_LIMIT

    # Build Task List
    for index, task in enumerate(tasks[start_position:STATUS_LIMIT + start_position], start=1):
        tstatus = task.status()
        emoji = {
            MirrorStatus.STATUS_DOWNLOADING: "⬇️",
            MirrorStatus.STATUS_UPLOADING: "⬆️",
            MirrorStatus.STATUS_COMPRESS: "🗜",
            MirrorStatus.STATUS_EXTRACTING: "📂",
            MirrorStatus.STATUS_TRIM: "✂️",
            MirrorStatus.STATUS_WATERMARK: "💧",
            MirrorStatus.STATUS_MERGING: "🎞",
            MirrorStatus.STATUS_CONVERT: "🔄",
            MirrorStatus.STATUS_ARCHIVING: "📦",
            MirrorStatus.STATUS_CLONING: "🧬",
            MirrorStatus.STATUS_SEEDING: "🌱"
        }.get(tstatus, "⚙️")

        msg += f'<b>{index + start_position}. {emoji} Title:</b> <code>{escape(str(task.name())) or "N/A"}</code>'
        msg += f'\n<b>Status:</b> {tstatus}'

        # Core progress
        if tstatus not in [MirrorStatus.STATUS_SEEDING, MirrorStatus.STATUS_METADATA]:
            msg += f'\n{get_progress_bar_string(task.progress())} {task.progress()}'
            msg += (
                f'\n<b>Processed:</b> {task.processed_bytes()} of {task.size()}'
                f'\n<b>Speed:</b> {task.speed()}'
                f'\n<b>ETA:</b> {task.eta() or "~"}'
                f'\n<b>Elapsed:</b> {task.elapsed() or "~"}'
            )

        # Seed info
        elif tstatus == MirrorStatus.STATUS_SEEDING:
            msg += (
                f'\n<b>Speed:</b> {task.upload_speed()}'
                f'\n<b>Uploaded:</b> {task.uploaded_bytes()}'
                f'\n<b>Ratio:</b> {task.ratio()}'
            )

        # Engine + user details
        msg += (
            f'\n<b>Engine:</b> {task.engine()}'
            f'\n<b>User:</b> <a href="https://t.me/{task.listener.message.from_user.username}">'
            f'{task.listener.message.from_user.first_name}</a>'
        )

        msg += f'\n<b>Action:</b> {action(task.listener.message)}'
        msg += f'\n<b>Cancel:</b> /{BotCommands.CancelTaskCommand} {task.gid()}\n\n'

    # No tasks fallback
    if not msg:
        msg = f'No Active {status} Tasks!'

    # Speed calculations
    for task in tasks:
        tstatus = task.status()
        if tstatus == MirrorStatus.STATUS_DOWNLOADING or task.engine() == 'JDownloader':
            dl_speed += speed_string_to_bytes(task.speed())
        elif tstatus == MirrorStatus.STATUS_UPLOADING:
            up_speed += speed_string_to_bytes(task.speed())
        elif tstatus == MirrorStatus.STATUS_SEEDING:
            up_speed += speed_string_to_bytes(task.upload_speed())

    # Buttons
    buttons = ButtonMaker()
    if len(tasks) > STATUS_LIMIT:
        msg += f'\n<b>Page:</b> {page_no}/{pages} | <b>Tasks:</b> {tasks_no}'
        buttons.button_data('⬅️ Prev', f'status {sid} pre', 'header')
        buttons.button_data('Next ➡️', f'status {sid} nex', 'header')
        if tasks_no > 30:
            for i in [1, 2, 4, 6, 8, 10, 15, 20]:
                buttons.button_data(str(i), f'status {sid} ps {i}', 'footer')

    if len(task_dict) > STATUS_LIMIT or status != 'All':
        for label, status_value in STATUS_VALUES:
            if status_value != status:
                buttons.button_data(label, f'status {sid} st {status_value}')

    buttons.button_data('♻️ Refresh', f'status {sid} ref', 'header')
    if is_user:
        buttons.button_data('✖ Close', f'status {sid} cls', 'header')

    # System Stats Footer
    msg += (
        '\n\n<b>📊 SS Bots System Stats</b>\n'
        f'├ ⚙ CPU: {cpu_percent()}% | 💾 Free: {get_readable_file_size(disk_usage(config_dict["DOWNLOAD_DIR"]).free)}\n'
        f'├ 🧠 RAM: {virtual_memory().percent}% | ⏱ Uptime: {get_readable_time(time() - botStartTime)}\n'
        f'├ 🔻 DL: {get_readable_file_size(dl_speed)} | 🔺 UL: {get_readable_file_size(up_speed)}/s\n'
        '└─── <a href="https://t.me/SSBotsUpdates">★彡 SS Bots 彡★</a>'
    )

    return msg, buttons.build_menu(6)
