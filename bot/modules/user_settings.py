from aiofiles.os import path as aiopath, makedirs
from ast import literal_eval
from asyncio import sleep, gather, Event, wait_for, wrap_future
from datetime import datetime
from functools import partial
from html import escape
from os import path as ospath, getcwd
from pyrogram import Client
try:
    from langcodes import Language
except ImportError:
    Language = None
from pyrogram.filters import command, regex, create, user
from pyrogram.handlers import CallbackQueryHandler, MessageHandler
from pyrogram.types import CallbackQuery, Message
from time import time

from bot import bot, bot_loop, bot_dict, bot_lock, user_data, config_dict, DATABASE_URL, GLOBAL_EXTENSION_FILTER, OWNER_ID
from bot.helper.ext_utils.bot_utils import update_user_ldata, UserDaily, new_thread, new_task, is_premium_user
from bot.helper.ext_utils.commons_check import UseCheck
from bot.helper.ext_utils.conf_loads import intialize_savebot
from bot.helper.ext_utils.db_handler import DbManager
from bot.helper.ext_utils.files_utils import clean_target
from bot.helper.ext_utils.help_messages import UsetString
from bot.helper.ext_utils.media_utils import createThumb
from bot.helper.ext_utils.status_utils import get_readable_time, get_readable_file_size
from bot.helper.ext_utils.telegram_helper import TeleContent
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import sendMessage, auto_delete_message, sendPhoto, editPhoto, deleteMessage, editMessage, sendCustom
from bot.helper.themes import BotTheme


handler_dict = {}

# Description dictionary for each setting
desp_dict = {
    "rcc": ["RClone config for uploading to cloud storage", "Send rclone.conf file.\n<b>Timeout:</b> 60 sec"],
    "lprefix": ["Leech Filename Prefix", 'Send Leech Filename Prefix.\n<b>Timeout:</b> 60 sec'],
    "lsuffix": ["Leech Filename Suffix", 'Send Leech Filename Suffix.\n<b>Timeout:</b> 60 sec'],
    "lremname": ["Leech Filename Remname (Regex)", 'Send Leech Filename Remname.\n<b>Timeout:</b> 60 sec'],
    "lcaption": ["Leech Caption", 'Send Leech Caption (HTML tags supported).\n<b>Timeout:</b> 60 sec'],
    "ldump": ["Leech Dump Channel", "Send Channel ID or @username.\n<b>Timeout:</b> 60 sec"],
    "mprefix": ["Mirror Filename Prefix", "Send Mirror Filename Prefix.\n<b>Timeout:</b> 60 sec"],
    "msuffix": ["Mirror Filename Suffix", "Send Mirror Filename Suffix.\n<b>Timeout:</b> 60 sec"],
    "mremname": ["Mirror Filename Remname (Regex)", "Send Mirror Filename Remname.\n<b>Timeout:</b> 60 sec"],
    "thumb": ["Custom Thumbnail", "Send a photo to save as thumbnail.\n<b>Timeout:</b> 60 sec"],
    "yt_opt": ["YT-DLP Options", "Send YT-DLP options in format: key:value|key:value.\n<b>Timeout:</b> 60 sec"],
    "usess": ["User Session", "Send Pyrogram session string.\n<b>Timeout:</b> 60 sec"],
    "split_size": ["Leech Split Size", "Send split size (e.g., 2GB, 500MB).\n<b>Timeout:</b> 60 sec"],
    "metadata": ["Video Metadata", "Send metadata title text.\n<b>Timeout:</b> 60 sec"],
}

fname_dict = {
    "rcc": "RClone",
    "lprefix": "Leech Prefix",
    "lsuffix": "Leech Suffix",
    "lremname": "Leech Remname",
    "mprefix": "Mirror Prefix",
    "msuffix": "Mirror Suffix",
    "mremname": "Mirror Remname",
    "ldump": "Dump Channel",
    "lcaption": "Caption",
    "thumb": "Thumbnail",
    "yt_opt": "YT-DLP",
    "usess": "User Session",
    "split_size": "Split Size",
    "metadata": "Metadata",
}


async def getdailytasks(user_id, check_mirror=False, check_leech=False):
    """Get daily task usage"""
    if config_dict.get('DAILY_MODE'):
        user_dict = user_data.get(user_id, {})
        if check_mirror:
            return user_dict.get('daily_mirror', 0)
        elif check_leech:
            return user_dict.get('daily_leech', 0)
        else:
            dly_tasks = user_dict.get('dly_tasks', [datetime.now(), 0])
            return dly_tasks[1] if dly_tasks else 0
    return 0


async def get_user_settings(from_user, key=None, edit_type=None, edit_mode=None):
    user_id = from_user.id
    name = from_user.mention(style="html")
    buttons = ButtonMaker()
    thumbpath = f"thumbnails/{user_id}.jpg"
    rclone_path = f"rclone/{user_id}.conf"
    token_pickle = f"tokens/{user_id}.pickle"
    user_dict = user_data.get(user_id, {})
    
    if key is None:
        # Main menu with three sections
        buttons.button_data("🌐 Universal Settings", f"userset {user_id} universal")
        buttons.button_data("☁️ Mirror Settings", f"userset {user_id} mirror")
        buttons.button_data("⬇️ Leech Settings", f"userset {user_id} leech")
        
        if user_dict and any(k in user_dict for k in list(fname_dict.keys())):
            buttons.button_data("🔄 Reset Settings", f"userset {user_id} reset_all")
        
        buttons.button_data("❌ Close", f"userset {user_id} close")
        
        # Get language name if langcodes is available
        if Language and (lc := from_user.language_code):
            try:
                lang_name = Language.get(lc).display_name()
            except:
                lang_name = lc or "N/A"
        else:
            lang_name = from_user.language_code or "N/A"
        
        text = BotTheme.USER_SETTING(
            NAME=name,
            ID=user_id,
            USERNAME=f"@{from_user.username}" if from_user.username else "Not Set",
            LANG=lang_name,
            DC=from_user.dc_id or "N/A"
        )
        
        button = buttons.build_menu(1)
        
    elif key == "universal":
        # Universal Settings Section
        ytopt = user_dict.get("yt_opt", config_dict.get("YT_DLP_OPTIONS", "")) or "Not Exists"
        buttons.button_data(
            f"{'✅' if ytopt != 'Not Exists' else ''} YT-DLP Options",
            f"userset {user_id} yt_opt"
        )
        
        u_sess = "Exists" if user_dict.get("session_string") else "Not Exists"
        buttons.button_data(
            f"{'✅' if u_sess != 'Not Exists' else ''} User Session",
            f"userset {user_id} usess"
        )
        
        bot_pm = "Enabled" if user_dict.get("enable_pm", config_dict.get("BOT_PM", False)) else "Disabled"
        buttons.button_data(
            "Disable Bot PM" if bot_pm == "Enabled" else "Enable Bot PM",
            f"userset {user_id} bot_pm"
        )
        
        mediainfo = "Enabled" if user_dict.get("show_mediainfo", config_dict.get("SHOW_MEDIAINFO", False)) else "Disabled"
        buttons.button_data(
            "Disable MediaInfo" if mediainfo == "Enabled" else "Enable MediaInfo",
            f"userset {user_id} mediainfo"
        )
        
        save_mode = "Save As Dump" if user_dict.get("save_mode") else "Save As BotPM"
        buttons.button_data(
            "Save As BotPM" if save_mode == "Save As Dump" else "Save As Dump",
            f"userset {user_id} save_mode"
        )
        
        # Daily task limits
        dailytl = config_dict.get("DAILY_TASK_LIMIT") or "∞"
        dailytas = await getdailytasks(user_id) if user_id != OWNER_ID else "∞"
        
        if user_dict.get("dly_tasks"):
            t = str(datetime.now() - user_dict["dly_tasks"][0]).split(":")
            lastused = f"{t[0]}h {t[1]}m {t[2].split('.')[0]}s ago"
        else:
            lastused = "Bot Not Used yet.."
        
        text = BotTheme.UNIVERSAL(
            NAME=name,
            YT=escape(ytopt),
            DT=f"{dailytas} / {dailytl}",
            LAST_USED=lastused,
            BOT_PM=bot_pm,
            MEDIAINFO=mediainfo,
            SAVE_MODE=save_mode,
            USESS=u_sess
        )
        
        buttons.button_data("🔙 Back", f"userset {user_id} back", "footer")
        buttons.button_data("❌ Close", f"userset {user_id} close", "footer")
        button = buttons.build_menu(2)
        
    elif key == "mirror":
        # Mirror Settings Section
        rccmsg = "Exists" if await aiopath.exists(rclone_path) else "Not Exists"
        buttons.button_data("RClone Config", f"userset {user_id} rcc")
        
        dailytlup = get_readable_file_size(config_dict.get("DAILY_MIRROR_LIMIT", 0) * 1024**3) if config_dict.get("DAILY_MIRROR_LIMIT") else "∞"
        dailyup = get_readable_file_size(await getdailytasks(user_id, check_mirror=True)) if config_dict.get("DAILY_MIRROR_LIMIT") and user_id != OWNER_ID else "∞"
        
        mprefix = user_dict.get("mprefix", config_dict.get("MIRROR_FILENAME_PREFIX", "")) or "Not Exists"
        buttons.button_data("Mirror Prefix", f"userset {user_id} mprefix")
        
        msuffix = user_dict.get("msuffix", config_dict.get("MIRROR_FILENAME_SUFFIX", "")) or "Not Exists"
        buttons.button_data("Mirror Suffix", f"userset {user_id} msuffix")
        
        mremname = user_dict.get("mremname", config_dict.get("MIRROR_FILENAME_REMNAME", "")) or "Not Exists"
        buttons.button_data("Mirror Remname", f"userset {user_id} mremname")
        
        ddl_serv = len(val) if (val := user_dict.get("ddl_servers", False)) else 0
        buttons.button_data("DDL Servers", f"userset {user_id} ddl_servers")
        
        tds_mode = "Enabled" if user_dict.get("td_mode", False) else "Disabled"
        if not config_dict.get("USER_TD_MODE"):
            tds_mode = "Force Disabled"
        
        user_tds = len(val) if (val := user_dict.get("user_tds", False)) else 0
        buttons.button_data("User TDs", f"userset {user_id} user_tds")
        
        text = BotTheme.MIRROR(
            NAME=name,
            RCLONE=rccmsg,
            DDL_SERVER=ddl_serv,
            DM=f"{dailyup} / {dailytlup}",
            MREMNAME=escape(mremname),
            MPREFIX=escape(mprefix),
            MSUFFIX=escape(msuffix),
            TMODE=tds_mode,
            USERTD=user_tds
        )
        
        buttons.button_data("🔙 Back", f"userset {user_id} back", "footer")
        buttons.button_data("❌ Close", f"userset {user_id} close", "footer")
        button = buttons.build_menu(2)
        
    elif key == "leech":
        # Leech Settings Section
        lprefix = user_dict.get("lprefix", config_dict.get("LEECH_FILENAME_PREFIX", "")) or "Not Exists"
        buttons.button_data("Leech Prefix", f"userset {user_id} lprefix")
        
        lsuffix = user_dict.get("lsuffix", config_dict.get("LEECH_FILENAME_SUFFIX", "")) or "Not Exists"
        buttons.button_data("Leech Suffix", f"userset {user_id} lsuffix")
        
        lremname = user_dict.get("lremname", config_dict.get("LEECH_FILENAME_REMNAME", "")) or "Not Exists"
        buttons.button_data("Leech Remname", f"userset {user_id} lremname")
        
        lcaption = user_dict.get("captions") or "Not Exists"
        buttons.button_data("Caption", f"userset {user_id} capmode")
        
        ldump = f"<code>{user_dict['dump_ch']}</code>" if user_dict.get("dump_ch") else "Not Set"
        buttons.button_data("Dump Channel", f"userset {user_id} setdata dump_ch")
        
        thumb = "Exists" if await aiopath.exists(thumbpath) else "Not Exists"
        buttons.button_data("Thumbnail", f"userset {user_id} setdata thumb")
        
        split_size = get_readable_file_size(config_dict.get("LEECH_SPLIT_SIZE", 2097151000))
        
        lmeta = user_dict.get("metadata") or "Not Set"
        buttons.button_data("Metadata", f"userset {user_id} setdata metadata")
        
        dailytl_leech = get_readable_file_size(config_dict.get("DAILY_LEECH_LIMIT", 0) * 1024**3) if config_dict.get("DAILY_LEECH_LIMIT") else "∞"
        daily_leech = get_readable_file_size(await getdailytasks(user_id, check_leech=True)) if config_dict.get("DAILY_LEECH_LIMIT") and user_id != OWNER_ID else "∞"
        
        ltype = "DOCUMENT" if user_dict.get("as_doc", config_dict.get("AS_DOCUMENT", False)) else "MEDIA"
        media_group = "Enabled" if user_dict.get("media_group", config_dict.get("MEDIA_GROUP", False)) else "Disabled"
        
        text = BotTheme.LEECH(
            NAME=name,
            LPREFIX=escape(lprefix),
            LSUFFIX=escape(lsuffix),
            LREMNAME=escape(lremname),
            LCAPTION=lcaption,
            LDUMP=ldump,
            THUMB=thumb,
            SPLIT_SIZE=split_size,
            LMETA=lmeta,
            DL=f"{daily_leech} / {dailytl_leech}",
            LTYPE=ltype,
            MEDIA_GROUP=media_group
        )
        
        buttons.button_data("🔙 Back", f"userset {user_id} back", "footer")
        buttons.button_data("❌ Close", f"userset {user_id} close", "footer")
        button = buttons.build_menu(2)
    
    elif key == "rcc":
        # RClone Configuration
        rccmsg = "Exists" if await aiopath.exists(rclone_path) else "Not Exists"
        buttons.button_data(
            "🔥 RClone Config" if rccmsg == "Exists" else "RClone Config",
            f"userset {user_id} setdata rclone_config"
        )
        
        rcpath = user_dict.get("rclone_path") or "Not Set"
        buttons.button_data(
            "🔥 RClone Path" if rcpath != "Not Set" else "RClone Path",
            f"userset {user_id} setdata rclone_path"
        )
        
        buttons.button_data("🔙 Back", f"userset {user_id} mirror")
        
        text = BotTheme.RCLONE_TOOLS(
            NAME=name,
            RCLONE=rccmsg,
            RCLONE_PATH=rcpath
        )
        
        button = buttons.build_menu(2)
    
    elif key == "capmode":
        # Caption Settings
        ex_cap = 'Thor: Love and Thunder (2022) 1080p.mkv'
        if user_dict.get('prename'):
            ex_cap = f'{user_dict.get("prename")} {ex_cap}'
        if user_dict.get('sufname'):
            fname, ext = ex_cap.rsplit('.', maxsplit=1)
            ex_cap = f'{fname} {user_dict.get("sufname")}.{ext}'

        user_cap = user_dict.get('caption_style', 'mono')
        user_capmode = user_cap.upper()
        
        if user_cap == 'italic':
            image, ex_cap = config_dict.get('IMAGE_ITALIC'), f'<i>{ex_cap}</i>'
        elif user_cap == 'bold':
            image, ex_cap = config_dict.get('IMAGE_BOLD'), f'<b>{ex_cap}</b>'
        elif user_cap == 'normal':
            image = config_dict.get('IMAGE_NORMAL')
        else:
            image, ex_cap = config_dict.get('IMAGE_MONO'), f'<code>{ex_cap}</code>'

        cap_modes = ['mono', 'italic', 'bold', 'normal']
        cap_modes.remove(user_cap)
        caption, fnamecap = user_dict.get('captions'), user_dict.get('fnamecap', True)
        
        if not user_dict or fnamecap:
            [buttons.button_data(mode.title(), f'userset {user_id} cap{mode}') for mode in cap_modes]
        
        buttons.button_data('🔥 Custom Caption' if caption else 'Custom Caption', f'userset {user_id} setdata setcap')
        buttons.button_data('🔙 Back', f'userset {user_id} leech')
        
        if caption:
            buttons.button_data('🔥 FCaption' if fnamecap else 'FCaption', f'userset {user_id} fnamecap')
            custom_cap = f'\n<code>{escape(caption)}</code>'
            fname_cup = '<b>ENABLE</b>' if fnamecap else '<b>DISABLE</b>'
        else:
            custom_cap, fname_cup = '<b>DISABLE</b>', 'NOT SET'
        
        text = BotTheme.CAPTION_SETTINGS(
            NAME=name,
            CAPTION_MODE=user_capmode,
            CUSTOM_CAP=custom_cap,
            FNAME_CAP=fname_cup,
            EXAMPLE=ex_cap
        )
        
        button = buttons.build_menu(2)
    
    elif key == "zipmode":
        # Zip Mode Settings  
        but_dict = {
            'zfolder': ['Folders', f'userset {user_id} zipmode zfolder'],
            'zfpart': ['Cloud Part', f'userset {user_id} zipmode zfpart'],
            'zeach': ['Each Files', f'userset {user_id} zipmode zeach'],
            'zpart': ['Part Mode', f'userset {user_id} zipmode zpart'],
            'auto': ['Auto Mode', f'userset {user_id} zipmode auto']
        }
        
        current_mode = edit_mode or user_dict.get('zipmode', 'zfolder')
        def_data = but_dict[current_mode][0]
        but_dict[current_mode][0] = f'🔥 {def_data}'
        
        [buttons.button_data(key, value) for key, value in but_dict.values()]
        buttons.button_data('🔙 Back', f'userset {user_id} leech')
        
        part_size = get_readable_file_size(config_dict.get('LEECH_SPLIT_SIZE', 2097151000))
        
        text = BotTheme.ZIP_MODE_SETTINGS(
            NAME=name,
            CURRENT_MODE=def_data,
            PART_SIZE=part_size
        )
        
        button = buttons.build_menu(2)
    
    elif key == "ddl_servers":
        # DDL Servers Configuration
        gofile = "Configured" if user_dict.get("gofile_token") else "Not Set"
        buttons.button_data("GoFile", f"userset {user_id} gofile")
        
        streamtape = "Configured" if user_dict.get("streamtape") else "Not Set"
        buttons.button_data("StreamTape", f"userset {user_id} streamtape")
        
        buttons.button_data("🔙 Back", f"userset {user_id} mirror")
        
        text = BotTheme.DDL_SERVERS(
            NAME=name,
            GOFILE=gofile,
            STREAMTAPE=streamtape
        )
        
        button = buttons.build_menu(2)
    
    else:
        # Default/other settings
        text = f"<b>Setting: {key}</b>\n\nConfiguration page"
        button = None
    
    # Default image if not set
    if 'image' not in locals():
        if await aiopath.exists(thumbpath):
            image = thumbpath
        else:
            image = config_dict.get('IMAGE_USETIINGS')
    
    return text, image, button


async def update_user_settings(query: CallbackQuery, data: str=None, uset_data: str=None):
    text, image, button = await get_user_settings(query.from_user, data, uset_data)
    if image:
        await editPhoto(text, query.message, image, button)
    else:
        await editMessage(text, query.message, button)


async def set_user_settings(_, message: Message, query: CallbackQuery, key: str):
    user_id = message.from_user.id
    handler_dict[user_id] = False
    value: str = message.text
    
    if key == 'dump_ch' and (value.isdigit() or value.startswith('-100')):
        value = int(value)
    elif key == 'excluded_extensions':
        fx = value.split()
        value = ['aria2', '!qB']
        for x in fx:
            x = x.lstrip('.')
            value.append(x.strip().lower())
    
    await gather(update_user_ldata(user_id, key, value), deleteMessage(message))
    
    # Navigate back to appropriate section
    if key in ['mprefix', 'msuffix', 'mremname']:
        data = 'mirror'
    elif key in ['lprefix', 'lsuffix', 'lremname', 'lcaption']:
        data = 'leech'
    elif key in ['yt_opt', 'session_string']:
        data = 'universal'
    else:
        data = ''
    
    if key == 'session_string':
        # Initialize savebot with user session
        await intialize_savebot(value, True, user_id)
        async with bot_lock:
            save_bot = bot_dict.get(user_id, {}).get('SAVEBOT')
        if not save_bot:
            msg = await sendMessage('Invalid session string!', message)
            await update_user_ldata(user_id, key, '')
            bot_loop.create_task(auto_delete_message(message, msg, stime=5))
    
    await update_user_settings(query, data)


async def set_thumb(_, message: Message, query: CallbackQuery):
    user_id = query.from_user.id
    handler_dict[user_id] = False
    msg = await sendMessage('<i>Processing thumbnail...</i>', message)
    des_dir = await createThumb(message, user_id)
    await gather(
        update_user_ldata(user_id, 'thumb', des_dir),
        deleteMessage(message, msg),
        update_user_settings(query, 'leech')
    )
    if DATABASE_URL:
        await DbManager().update_user_doc(user_id, 'thumb', des_dir)


async def add_rclone_pickle(_, message: Message, query: CallbackQuery, key: str):
    user_id = message.from_user.id
    handler_dict[user_id] = False
    file_path, ext_file = ('rclone', '.conf') if key == 'rclone_config' else ('tokens', '.pickle')
    fpath = ospath.join(getcwd(), file_path)
    await makedirs(fpath, exist_ok=True)
    
    if message.document.file_name.endswith(ext_file):
        des_dir = ospath.join(fpath, f'{user_id}{ext_file}')
        msg = await sendMessage('<i>Processing file...</i>', message)
        await message.download(file_name=des_dir)
        qdata = 'mirror' if key == 'rclone_config' else 'mirror'
        await gather(
            update_user_ldata(user_id, file_path, ospath.join(file_path, f'{user_id}{ext_file}')),
            deleteMessage(message, msg),
            update_user_settings(query, qdata)
        )
        if DATABASE_URL:
            await DbManager().update_user_doc(user_id, key, des_dir)
    else:
        msg = await sendMessage(f'Invalid {ext_file} file!', message)
        await gather(
            update_user_settings(query, 'setdata', key),
            auto_delete_message(message, msg, stime=5)
        )


@new_task
async def edit_user_settings(_, query: CallbackQuery):
    message = query.message
    user_id = query.from_user.id
    data = query.data.split()
    
    if user_id != int(data[1]):
        await query.answer('Not your settings!', True)
        return
    
    handler = handler_dict.get(user_id, False)
    if handler:
        handler.set()
        await sleep(0.5)
    
    if data[2] == 'close':
        handler_dict[user_id] = False
        await query.answer()
        await deleteMessage(message.reply_to_message, message)
    
    elif data[2] == 'back':
        await query.answer()
        await update_user_settings(query)
    
    elif data[2] in ['universal', 'mirror', 'leech']:
        await query.answer()
        await update_user_settings(query, data[2])
    
    elif data[2] == 'reset_all':
        await query.answer('Resetting all settings...', True)
        user_data[user_id] = {}
        if DATABASE_URL:
            await DbManager().delete_user(user_id)
        await update_user_settings(query)
    
    elif data[2] == 'bot_pm':
        await query.answer()
        current = user_data.get(user_id, {}).get('enable_pm', False)
        await update_user_ldata(user_id, 'enable_pm', not current)
        await update_user_settings(query, 'universal')
    
    elif data[2] == 'mediainfo':
        await query.answer()
        current = user_data.get(user_id, {}).get('show_mediainfo', False)
        await update_user_ldata(user_id, 'show_mediainfo', not current)
        await update_user_settings(query, 'universal')
    
    elif data[2] == 'save_mode':
        await query.answer()
        current = user_data.get(user_id, {}).get('save_mode', False)
        await update_user_ldata(user_id, 'save_mode', not current)
        await update_user_settings(query, 'universal')
    
    elif data[2] == 'as_doc':
        await query.answer()
        current = user_data.get(user_id, {}).get('as_doc', config_dict.get('AS_DOCUMENT', False))
        await update_user_ldata(user_id, 'as_doc', not current)
        await update_user_settings(query, 'leech')
    
    elif data[2] == 'media_group':
        await query.answer()
        current = user_data.get(user_id, {}).get('media_group', config_dict.get('MEDIA_GROUP', False))
        await update_user_ldata(user_id, 'media_group', not current)
        await update_user_settings(query, 'leech')
    
    elif data[2].startswith('cap'):
        await query.answer()
        cap_style = data[2][3:]  # Remove 'cap' prefix
        await update_user_ldata(user_id, 'caption_style', cap_style)
        await update_user_settings(query, 'capmode')
    
    elif data[2] == 'fnamecap':
        await query.answer()
        current = user_data.get(user_id, {}).get('fnamecap', True)
        await update_user_ldata(user_id, 'fnamecap', not current)
        await update_user_settings(query, 'capmode')
    
    elif data[2] in fname_dict:
        await query.answer()
        await update_user_settings(query, data[2])
    
    elif data[2] == 'zipmode':
        await query.answer()
        mode = data[3] if len(data) > 3 else 'zfolder'
        await update_user_ldata(user_id, 'zipmode', mode)
        await update_user_settings(query, 'zipmode', mode)
    
    elif data[2] == 'setdata' or data[2] == 'prepare':
        await query.answer()
        key = data[3] if len(data) > 3 else 'unknown'
        
        if key in ['thumb', 'rclone_config', 'token_pickle']:
            # File upload handling
            mesg = await sendMessage(desp_dict.get(key, ["", "Send the file"])[1], message)
            
            if key == 'thumb':
                pfunc = partial(set_thumb, query=query)
                pfilt = create(lambda _, __, m: m.photo)
            else:
                pfunc = partial(add_rclone_pickle, query=query, key=key)
                pfilt = create(lambda _, __, m: m.document)
            
            handler_dict[user_id] = Event()
            handler = bot.add_handler(MessageHandler(pfunc, filters=pfilt & user(user_id)), group=-1)
            
            try:
                await wait_for(handler_dict[user_id].wait(), timeout=60)
            except:
                await deleteMessage(mesg)
                await update_user_settings(query, 'mirror' if 'rclone' in key else 'leech')
            finally:
                bot.remove_handler(*handler)
        else:
            # Text input handling
            mesg = await sendMessage(desp_dict.get(key, ["", "Send the value"])[1], message)
            
            pfunc = partial(set_user_settings, query=query, key=key)
            handler_dict[user_id] = Event()
            handler = bot.add_handler(MessageHandler(pfunc, filters=regex(r'^(?!\/userset)') & user(user_id)), group=-1)
            
            try:
                await wait_for(handler_dict[user_id].wait(), timeout=60)
            except:
                await deleteMessage(mesg)
                # Navigate to appropriate section
                if key in ['mprefix', 'msuffix', 'mremname']:
                    await update_user_settings(query, 'mirror')
                elif key in ['lprefix', 'lsuffix', 'lremname']:
                    await update_user_settings(query, 'leech')
                elif key in ['yt_opt', 'usess']:
                    await update_user_settings(query, 'universal')
            finally:
                bot.remove_handler(*handler)
    
    elif data[2].startswith('rem_'):
        # Remove setting
        key = data[2][4:]  # Remove 'rem_' prefix
        await query.answer(f'Removing {key}...', True)
        await update_user_ldata(user_id, key, '')
        
        if key in ['thumb', 'rclone_config', 'token_pickle']:
            file_path = f"thumbnails/{user_id}.jpg" if key == 'thumb' else \
                       f"rclone/{user_id}.conf" if key == 'rclone_config' else \
                       f"tokens/{user_id}.pickle"
            if await aiopath.exists(file_path):
                await clean_target(file_path)
        
        # Navigate back
        if 'rclone' in key:
            await update_user_settings(query, 'mirror')
        elif key == 'thumb':
            await update_user_settings(query, 'leech')
        else:
            await update_user_settings(query)


@new_task
async def send_user_settings(_, message: Message):
    if await UseCheck().run(message):
        return
    
    msg, button = await get_user_settings(message.from_user)
    thumbpath = f"thumbnails/{message.from_user.id}.jpg"
    
    if await aiopath.exists(thumbpath):
        image = thumbpath
    else:
        image = config_dict.get('IMAGE_USETIINGS')
    
    if image:
        await sendPhoto(msg, message, image, button)
    else:
        await sendMessage(msg, message, button)


# Register handlers
bot.add_handler(MessageHandler(send_user_settings, filters=command(BotCommands.UserSetCommand) & CustomFilters.authorized))
bot.add_handler(CallbackQueryHandler(edit_user_settings, filters=regex('^userset')))
