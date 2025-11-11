from aiofiles.os import path as aiopath, makedirs
from ast import literal_eval
from asyncio import sleep, gather, Event, wait_for, wrap_future
from functools import partial
from html import escape
from os import path as ospath, getcwd
from pyrogram import Client
from pyrogram.filters import command, regex, create, user
from pyrogram.handlers import CallbackQueryHandler, MessageHandler
from pyrogram.types import CallbackQuery, Message
from time import time

from bot import bot, bot_loop, bot_dict, bot_lock, user_data, config_dict, DATABASE_URL, GLOBAL_EXTENSION_FILTER
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

handler_dict = {}


async def get_user_settings(from_user, data: str, uset_data: str):
    """
    Returns (text, image, inline_buttons) for the user's settings.
    Modified to present a simplified main menu (Universal/Mirror/Leech/Video Tools)
    and retains the original detailed branches for specific settings.
    """
    buttons = ButtonMaker()
    user_id = from_user.id
    thumbpath = ospath.join('thumbnails', f'{user_id}.jpg')
    rclone_path = ospath.join('rclone', f'{user_id}.conf')
    token_pickle = ospath.join('tokens', f'{user_id}.pickle')
    user_dict = user_data.get(user_id, {})
    premium_left = status_user = daily_limit = ''
    image = None

    # ----------------- Simplified main menu -----------------
    if not data:
        # Main simplified home menu - only the required buttons
        buttons.button_data('Universal Settings',
                            f'userset {user_id} universal')
        buttons.button_data('Mirror Settings', f'userset {user_id} mirror')
        buttons.button_data('Leech Settings', f'userset {user_id} leech')
        buttons.button_data('Video Tools', f'userset {user_id} video_tools')
        buttons.button_data('Close', f'userset {user_id} close')
        text = ('<b>USER SETTINGS</b>\n'
                f'Settings For: <b>{from_user.mention}</b>\n\n'
                f'Choose a category to configure your preferences.')
        image = config_dict.get('IMAGE_USETIINGS')
        return text, image, buttons.build_menu(2)

    # ----------------- Video Tools submenu -----------------
    elif data == 'video_tools':
        # Video Tools submenu - placeholder actions (can be wired later)
        buttons.button_data('🎞️ Merge Videos',
                            f'userset {user_id} video_merge')
        buttons.button_data('🗜️ Compress Video',
                            f'userset {user_id} video_compress')
        buttons.button_data('🔁 Convert Format',
                            f'userset {user_id} video_convert')
        buttons.button_data('🔇 Mute Video', f'userset {user_id} video_mute')
        buttons.button_data('➕ Add Audio',
                            f'userset {user_id} video_add_audio')
        buttons.button_data('✂️ Trim / Cut', f'userset {user_id} video_trim')
        buttons.button_data('💧 Watermark',
                            f'userset {user_id} video_watermark')
        buttons.button_data('Back', f'userset {user_id} back')
        buttons.button_data('Close', f'userset {user_id} close')
        image = config_dict.get('IMAGE_VIDTOOLS',
                                config_dict.get('IMAGE_VIDTOOLS', None))
        text = (
            '<b>VIDEO TOOLS</b>\n'
            'Select a video operation. (Placeholders — implement processing as needed)'
        )
        return text, image, buttons.build_menu(2)

    # ----------------- Universal Settings submenu -----------------
    elif data == 'universal':
        # Build a simplified universal submenu using existing config keys where appropriate
        # We keep deeper actions routed to existing setdata / prepare flows for consistency.
        # Buttons chosen based on your requirement summary.
        buttons.button_data('YT-DLP Options',
                            f'userset {user_id} setdata yt_opt')
        buttons.button_data('Session String',
                            f'userset {user_id} setdata session_string')
        buttons.button_data('Disable Bot PM', f'userset {user_id} enable_pm')
        buttons.button_data('Media Group', f'userset {user_id} media_group')
        buttons.button_data('Save As Dump',
                            f'userset {user_id} setdata dump_ch')
        buttons.button_data(
            'Default Upload', f'userset {user_id} gd' if user_dict.get(
                'default_upload', '') != 'gd' else f'userset {user_id} rc',
            'header')
        buttons.button_data('Back', f'userset {user_id} back')
        buttons.button_data('Close', f'userset {user_id} close')

        # Compose text summary using existing logic where possible
        default_upload = user_dict.get('default_upload',
                                       '') or config_dict['DEFAULT_UPLOAD']
        du = 'GDrive API' if default_upload == 'gd' else 'RClone'
        text = (
            '<b>UNIVERSAL SETTINGS</b>\n'
            f'<b>┃ </b>Default Upload: <b>{du}</b>\n'
            f'<b>┃ </b>YT-DLP Options: <b>{"SET" if user_dict.get("yt_opt") or config_dict.get("YT_DLP_OPTIONS") else "NOT SET"}</b>\n\n'
            'Choose an option to configure.')
        image = config_dict.get('IMAGE_USETIINGS')
        return text, image, buttons.build_menu(2)

    # ----------------- Mirror Settings submenu -----------------
    elif data == 'mirror':
        # Simplified mirror menu (keeps routing to existing handlers)
        buttons.button_data('RClone Config', f'userset {user_id} rctool')
        buttons.button_data('Mirror Prefix',
                            f'userset {user_id} setdata prename')
        buttons.button_data('Mirror Suffix',
                            f'userset {user_id} setdata sufname')
        buttons.button_data('Remname', f'userset {user_id} setdata remname')
        buttons.button_data('DDL Servers',
                            f'userset {user_id} setdata excluded_extensions')
        buttons.button_data('User Dump/TDs',
                            f'userset {user_id} setdata dump_ch')
        buttons.button_data('Back', f'userset {user_id} back')
        buttons.button_data('Close', f'userset {user_id} close')

        text = ('<b>MIRROR SETTINGS</b>\n'
                'Configure mirror related options.')
        image = config_dict.get('IMAGE_RCLONE')
        return text, image, buttons.build_menu(2)

    # ----------------- Leech Settings submenu -----------------
    elif data == 'leech':
        # Simplified leech menu - maps to pre-existing setdata/prepare/rem flows
        buttons.button_data('Send As Document', f'userset {user_id} as_doc')
        buttons.button_data('Thumbnail', f'userset {user_id} setdata thumb')
        buttons.button_data('Leech Split Size', f'userset {user_id} setdata')
        buttons.button_data('Caption Style', f'userset {user_id} capmode')
        buttons.button_data('Leech Prefix',
                            f'userset {user_id} setdata prename')
        buttons.button_data('Leech Suffix',
                            f'userset {user_id} setdata sufname')
        buttons.button_data('Leech Remname',
                            f'userset {user_id} setdata remname')
        buttons.button_data('Leech Dump CH',
                            f'userset {user_id} setdata dump_ch')
        buttons.button_data('Metadata', f'userset {user_id} setdata metadata')
        buttons.button_data('Back', f'userset {user_id} back')
        buttons.button_data('Close', f'userset {user_id} close')

        text = ('<b>LEECH SETTINGS</b>\n'
                'Configure leech behaviour and message styles.')
        image = config_dict.get('IMAGE_USETIINGS')
        return text, image, buttons.build_menu(2)

    # ----------------- Existing branches (preserve original behaviour) -----------------
    # The following branches are kept from your original file to ensure existing logic is unchanged.
    elif data == 'capmode':
        ex_cap = 'Thor: Love and Thunder (2022) 1080p.mkv'
        if user_dict.get('prename'):
            ex_cap = f'{user_dict.get("prename")} {ex_cap}'
        if user_dict.get('sufname'):
            fname, ext = ex_cap.rsplit('.', maxsplit=1)
            ex_cap = f'{fname} {user_dict.get("sufname")}.{ext}'

        user_cap = user_dict.get('caption_style', 'mono')
        user_capmode = user_cap.upper()
        match user_cap:
            case 'italic':
                image, ex_cap = config_dict['IMAGE_ITALIC'], f'<i>{ex_cap}</i>'
            case 'bold':
                image, ex_cap = config_dict['IMAGE_BOLD'], f'<b>{ex_cap}</b>'
            case 'normal':
                image = config_dict['IMAGE_NORMAL']
            case 'mono':
                image, ex_cap = config_dict[
                    'IMAGE_MONO'], f'<code>{ex_cap}</code>'

        cap_modes = ['mono', 'italic', 'bold', 'normal']
        cap_modes.remove(user_cap)
        caption, fnamecap = user_dict.get('captions'), user_dict.get(
            'fnamecap', True)
        if not user_dict or fnamecap:
            [
                buttons.button_data(mode.title(),
                                    f'userset {user_id} cap{mode}')
                for mode in cap_modes
            ]
        buttons.button_data(
            '🔥 Custom Caption' if caption else 'Custom Caption',
            f'userset {user_id} setdata setcap')
        buttons.button_data('Back', f'userset {user_id} back')
        if caption:
            buttons.button_data('🔥 FCaption' if fnamecap else 'FCaption',
                                f'userset {user_id} fnamecap')
            custom_cap = f'\n<code>{escape(caption)}</code>'
            if fnamecap:
                fname_cup = '<b>┎ </b>FName Caption: <b>ENABLE</b>\n'
            else:
                fname_cup = '<b>┖ </b>FName Caption: <b>DISABLE</b>\n'
                user_capmode, image, ex_cap = ('DISABLE',
                                               config_dict['IMAGE_CAPTION'],
                                               '<b>DISABLE</b>')
        else:
            custom_cap, fname_cup = '<b>DISABLE</b>', ''
        text = ('<b>CAPTION SETTINGS</b>\n'
                f'<b>┎ </b>Caption Settings: <b>{from_user.mention}</b>\n'
                f'<b>┃ </b>Caption Mode: <b>{user_capmode}</b>\n'
                f'{fname_cup}'
                f'<b>┖ </b>Custom Caption: {custom_cap}\n\n'
                f'<b>Example:</b> {ex_cap}')

    elif data == 'rctool':
        rccmsg, buttonkey = (
            'EXISTS 🔥',
            '🔥 RClone Config') if await aiopath.exists(rclone_path) else (
                'NOT SET', 'RClone Config')
        buttons.button_data(buttonkey,
                            f'userset {user_id} setdata rclone_config')

        rcpathmsg, buttonkey = (f'<code>{rc_path}</code>',
                                '🔥 RClone Path') if (rc_path := user_dict.get(
                                    'rclone_path')) else ('<b>NOT SET</b>',
                                                          'RClone Path')
        buttons.button_data(buttonkey,
                            f'userset {user_id} setdata rclone_path')

        buttons.button_data('Back', f'userset {user_id} back')

        image = config_dict['IMAGE_RCLONE']
        text = ('<b>RCLONE SETTINGS</b>\n' +
                f'<b>┎ </b>RClone Config: <b>{rccmsg}</b>\n' +
                f'<b>┖ </b>Rclone Path: {rcpathmsg}\n')

    elif data == 'gdtool':
        gdrive_id, buttonkey = (f'<code>{gd_id}</code>', '🔥 Drive ID') if (
            gd_id := user_dict.get('gdrive_id')) else ('<b>DISABLE</b>',
                                                       'Drive ID')
        buttons.button_data(buttonkey, f'userset {user_id} setdata gdrive_id')

        index_url, buttonkey = (f'<code>{index}</code>', '🔥 Index URL') if (
            index := user_dict.get('index_url')) else ('<b>DISABLE</b>',
                                                       'Index URL')
        buttons.button_data(buttonkey, f'userset {user_id} setdata index_url')

        token_pickle, buttonkey = (
            'EXISTS 🔥',
            '🔥 Token Pickle') if await aiopath.exists(token_pickle) else (
                'NOT SET', 'Token Pickle')
        buttons.button_data(buttonkey,
                            f'userset {user_id} setdata token_pickle')

        stop_dup = user_dict.get(
            'stop_duplicate'
        ) or 'stop_duplicate' not in user_dict and config_dict['STOP_DUPLICATE']
        stop_dup_msg, buttonkey = (
            'ENABLE 🔥', '🔥 Stop Duplicate') if stop_dup else ('DISABLE',
                                                              'Stop Duplicate')
        buttons.button_data(buttonkey,
                            f'userset {user_id} stop_duplicate {stop_dup}',
                            'header')

        if await aiopath.exists('accounts'):
            use_sa, buttonkey = ('ENABLE 🔥',
                                 '🔥 Use SA') if user_dict.get('use_sa') else (
                                     'DISABLE', 'Use SA')
            buttons.button_data(buttonkey,
                                f'userset {user_id} use_sa {use_sa}', 'header')
        else:
            use_sa = 'NOT AVAILABLE'

        buttons.button_data('Back', f'userset {user_id} back')

        image = config_dict['IMAGE_GD']
        text = ('<b>User GDRIVE SETTING</b>\n'
                f'<b>┎ </b>GDrive ID: {gdrive_id}\n'
                f'<b>┃ </b>Index URL: {index_url}\n'
                f'<b>┃ </b>Use SA: <b>{use_sa}</b>\n'
                f'<b>┃/leech1 </b>Token Pickle: <b>{token_pickle}</b>\n'
                f'<b>┖ </b>Stop Duplicate: <b>{stop_dup_msg}</b>')

    elif data == 'zipmode':
        but_dict = {
            'zfolder': ['Folders', f'userset {user_id} zipmode zfolder'],
            'zfpart': ['Cloud Part', f'userset {user_id} zipmode zfpart'],
            'zeach': ['Each Files', f'userset {user_id} zipmode zeach'],
            'zpart': ['Part Mode', f'userset {user_id} zipmode zpart'],
            'auto': ['Auto Mode', f'userset {user_id} zipmode auto']
        }
        def_data = but_dict[uset_data][0]
        but_dict[uset_data][0] = f'🔥 {def_data}'
        [buttons.button_data(key, value) for key, value in but_dict.values()]
        buttons.button_data('Back', f'userset {user_id} back')
        part_size = get_readable_file_size(config_dict['LEECH_SPLIT_SIZE'])
        image = config_dict['IMAGE_ZIP']
        text = (
            '<b>ZIP MODE SETTINGS</b>\n⁍ <b>Folders/Default:</b> Zip file/folder\n'
            f'⁍ <b>Cloud Part:</b> Zip file/folder as part {part_size} (Mirror Cmds)\n'
            '⁍ <b>Each Files:</b> Zip each file in folder/subfolder\n'
            f'⁍ <b>Part Mode:</b> Zip each file in folder/subfolder as part if size more than {part_size} (Mirror Cmds)\n'
            f'⁍ <b>Auto Mode:</b> Zip only file in folder/subfolder if size more than {part_size}\n\n'
            f'<b>Current Mode:</b> {def_data}\n\n'
            '<i>*Seed torrent only working in <b>Deafult Mode</b></i>')

    elif data == 'setdata':
        if uset_data in {'thumb', 'rclone_config', 'token_pickle'}:
            file_dict = {
                'thumb':
                (thumbpath, 'Thumbnail',
                 'Send a photo to save it as custom thumbnail.', '', ''),
                'rclone_config':
                (rclone_path, 'RClone',
                 'Send a valid *.conf file for <b>config.conf</b>.',
                 config_dict['IMAGE_RCLONE'], 'rctool'),
                'token_pickle':
                (token_pickle, 'Token',
                 'Send a valid *.pickle file for <b>token.pickle</b>.',
                 config_dict['IMAGE_GD'], 'gdtool')
            }
            file_path, butkey, text, image, qdata = file_dict[uset_data]
            if await aiopath.exists(file_path):
                buttons.button_data(f'Change {butkey}',
                                    f'userset {user_id} prepare {uset_data}')
                buttons.button_data(f'Delete {butkey}',
                                    f'userset {user_id} rem_{uset_data}')
            else:
                buttons.button_data(f'Set {butkey}',
                                    f'userset {user_id} prepare {uset_data}')
        else:
            uset_dict = {
                'excluded_extensions':
                ('excluded_extensions', 'Extension', UsetString.EXT,
                 config_dict['IMAGE_EXTENSION'], ''),
                'setcap': ('captions', 'Caption', UsetString.CAP,
                           config_dict['IMAGE_CAPTION'], 'capmode'),
                'rctool': ('captions', 'Caption', UsetString.CAP,
                           config_dict['IMAGE_CAPTION'], 'rctool'),
                'rclone_path': ('rclone_path', 'RClone Path', UsetString.RCP,
                                config_dict['IMAGE_RCLONE'], 'rctool'),
                'dump_ch': ('dump_ch', 'Dump', UsetString.DUMP,
                            config_dict['IMAGE_DUMP'], ''),
                'gdrive_id': ('gdrive_id', 'ID', UsetString.GDID,
                              config_dict['IMAGE_GD'], 'gdtool'),
                'index_url': ('index_url', 'Index', UsetString.INDX,
                              config_dict['IMAGE_GD'], 'gdtool'),
                'prename': ('prename', 'Prename', UsetString.PRE,
                            config_dict['IMAGE_PRENAME'], ''),
                'sufname': ('sufname', 'Sufname', UsetString.SUF,
                            config_dict['IMAGE_SUFNAME'], ''),
                'remname':
                ('remname', 'Remname',
                 UsetString.REM.format(user_dict.get('remname') or '~'),
                 config_dict['IMAGE_REMNAME'], ''),
                'metadata':
                ('metadata', 'Metadata',
                 UsetString.META.format(user_dict.get('metadata') or '~'),
                 config_dict['IMAGE_METADATA'], ''),
                'session_string': ('session_string', 'Session', UsetString.SES,
                                   config_dict['IMAGE_USER'], ''),
                'yt_opt': ('yt_opt', 'YT-DLP', UsetString.YT,
                           config_dict['IMAGE_YT'], '')
            }
            if uset_data == 'dump_ch':
                log_title = user_dict.get('log_title')
                buttons.button_data(
                    '🔥 Log Title' if log_title else 'Log Title',
                    f'userset {user_id} setdata dump_ch {not log_title}')
            elif uset_data == 'metadata':
                clean_meta = user_dict.get('clean_metadata')
                buttons.button_data(
                    '🔥 Clean' if clean_meta else '🔥 Overwrite',
                    f'userset {user_id} setdata metadata {not clean_meta}')

            key, butkey, text, image, qdata = uset_dict[uset_data]
            if user_dict.get(
                    key) or key == 'yt_opt' and config_dict['YT_DLP_OPTIONS']:
                buttons.button_data(f'Change {butkey}',
                                    f'userset {user_id} prepare {key}')
                buttons.button_data(f'Remove {butkey}',
                                    f'userset {user_id} rem_{key}')
            else:
                buttons.button_data(f'Set {butkey}',
                                    f'userset {user_id} prepare {key}')
        if qdata:
            buttons.button_data('Back', f'userset {user_id} {qdata}')
        text = text.replace('Timeout: 60s.', '')
        if uset_data not in [
                'setcap', 'index_url', 'token_pickle', 'gdrive_id',
                'rclone_path', 'rclone_config'
        ]:
            buttons.button_data('Back', f'userset {user_id} back')

    elif data == 'prepare':
        msg_thumb = 'Send a photo to to change current thumbnail.\n\n<i>Timeout: 60s.</i>' if await aiopath.exists(thumbpath) else \
            'Send a photo to save it as custom thumbnail.\n\n<i>Timeout: 60s.</i>'
        msg_rclone = 'Send new valid *.conf file to change current <b>config.conf</b>.\n\n<i>Timeout: 60s.</i>' if await aiopath.exists(rclone_path) else \
            'Send a valid *.conf file for <b>config.conf</b>.\n\n<i>Timeout: 60s.</i>'
        msg_token = 'Send new valid *.pickle file to change current <b>token.pickle</b>.\n\n<i>Timeout: 60s.</i>' if await aiopath.exists(token_pickle) else \
            'Send a valid *.pickle file for <b>token.pickle</b>.\n\n<i>Timeout: 60s.</i>'
        prepare_dict = {
            'thumb': (msg_thumb, image),
            'rclone_config': (msg_rclone, config_dict['IMAGE_RCLONE']),
            'token_pickle': (msg_token, config_dict['IMAGE_GD']),
            'dump_ch': (UsetString.DUMP, config_dict['IMAGE_DUMP']),
            'rclone_path': (UsetString.RCP, config_dict['IMAGE_RCLONE']),
            'gdrive_id': (UsetString.GDID, config_dict['IMAGE_GD']),
            'index_url': (UsetString.INDX, config_dict['IMAGE_GD']),
            'excluded_extensions':
            (UsetString.EXT, config_dict['IMAGE_EXTENSION']),
            'captions': (UsetString.CAP, config_dict['IMAGE_CAPTION']),
            'prename': (UsetString.PRE, config_dict['IMAGE_PRENAME']),
            'sufname': (UsetString.SUF, config_dict['IMAGE_SUFNAME']),
            'remname':
            (UsetString.REM.format(user_dict.get('remname')
                                   or '~'), config_dict['IMAGE_REMNAME']),
            'metadata':
            (UsetString.META.format(user_dict.get('metadata')
                                    or '~'), config_dict['IMAGE_METADATA']),
            'session_string': (UsetString.SES, config_dict['IMAGE_USER']),
            'yt_opt': (UsetString.YT, config_dict['IMAGE_YT'])
        }
        text, image = prepare_dict[uset_data]
        buttons.button_data('Back', f'userset {user_id} setdata {uset_data}')

    # Add the Close button for all other branches (keeps original behaviour)
    buttons.button_data('Close', f'userset {user_id} close')
    return text, image, buttons.build_menu(2)


async def update_user_settings(query: CallbackQuery,
                               data: str = None,
                               uset_data: str = None):
    text, image, button = await get_user_settings(query.from_user, data,
                                                  uset_data)
    if not image:
        if await aiopath.exists(
                thumb := ospath.join('thumbnails', f'{query.from_user.id}.jpg')
        ):
            image = thumb
        else:
            image = config_dict['IMAGE_USETIINGS']
    await editPhoto(text, query.message, image, button)


async def set_user_settings(_, message: Message, query: CallbackQuery,
                            key: str):
    user_id = message.from_user.id
    handler_dict[user_id] = False
    value: str = message.text
    if (key == 'dump_ch' and value.isdigit() or value.startswith('-100')):
        value = int(value)
    elif key == 'excluded_extensions':
        fx = value.split()
        value = ['aria2', '!qB']
        for x in fx:
            x = x.lstrip('.')
            value.append(x.strip().lower())
    await gather(update_user_ldata(user_id, key, value),
                 deleteMessage(message))
    if key == 'dump_ch':
        await update_user_settings(query, 'setdata', 'dump_ch')
    else:
        match key:
            case 'index_url' | 'token_pickle' | 'gdrive_id':
                data = 'gdtool'
            case 'captions':
                data = 'capmode'
            case 'rclone_path':
                data = 'rctool'
            case _:
                data = ''
        if key == 'session_string':
            await intialize_savebot(value, True, user_id)
            async with bot_lock:
                save_bot = bot_dict[user_id]['SAVEBOT']
            if not save_bot:
                msg = await sendMessage(
                    'Something went wrong, or invalid string!', message)
                await update_user_ldata(user_id, key, '')
                bot_loop.create_task(auto_delete_message(message, msg,
                                                         stime=5))
        await update_user_settings(query, data)


async def set_thumb(_, message: Message, query: CallbackQuery):
    user_id = query.from_user.id
    handler_dict[user_id] = False
    msg = await sendMessage('<i>Processing, please wait...</i>', message)
    des_dir = await createThumb(message, user_id)
    await gather(update_user_ldata(user_id, 'thumb', des_dir),
                 deleteMessage(message, msg), update_user_settings(query))
    if DATABASE_URL:
        await DbManager().update_user_doc(user_id, 'thumb', des_dir)


async def add_rclone_pickle(_, message: Message, query: CallbackQuery,
                            key: str):
    user_id = message.from_user.id
    handler_dict[user_id] = False
    file_path, ext_file = ('rclone',
                           '.conf') if key == 'rclone_config' else ('tokens',
                                                                    '.pickle')
    fpath = ospath.join(getcwd(), file_path)
    await makedirs(fpath, exist_ok=True)
    if message.document.file_name.endswith(ext_file):
        des_dir = ospath.join(fpath, f'{user_id}{ext_file}')
        msg = await sendMessage('<i>Processing, please wait...</i>', message)
        await message.download(file_name=des_dir)
        qdata = 'rctool' if key == 'rclone_config' else 'gdtool'
        await gather(
            update_user_ldata(user_id, file_path,
                              ospath.join(file_path, f'{user_id}{ext_file}')),
            deleteMessage(message, msg), update_user_settings(query, qdata))
        if DATABASE_URL:
            await DbManager().update_user_doc(user_id, key, des_dir)
    else:
        msg = await sendMessage(f'Invalid *{ext_file} file!', message)
        await gather(update_user_settings(query, 'setdata', key),
                     auto_delete_message(message, msg, stime=5))


@new_thread
async def edit_user_settings(client: Client, query: CallbackQuery):
    message = query.message
    user_id = query.from_user.id
    data = query.data.split()
    user_dict = user_data.get(user_id, {})
    premi_features = [
        'caption', 'dump_ch', 'gdrive_id', 'media_group', 'prename', 'sufname',
        'remname', 'metadata', 'session_string', 'enable_pm', 'enable_ss'
    ]
    pre_data = data[3] if data[2] == 'setdata' else data[2]
    if config_dict['PREMIUM_MODE'] and not is_premium_user(
            user_id) and pre_data in premi_features:
        await query.answer('Upss, Premium User Required!', True)
        is_modified = False
        for key in premi_features:
            if user_dict.get(key):
                is_modified = True
                await update_user_ldata(user_id, key, False)
        if is_modified:
            await update_user_settings(query)
        return
    if user_id != int(data[1]):
        await query.answer('Not Yours!', True)
        return

    match data[2]:
        case 'setdata':
            handler_dict[user_id] = False
            await query.answer()
            if data[3] in ('dump_ch', 'metadata') and len(data) == 5:
                key = 'log_title' if data[3] == 'dump_ch' else 'clean_metadata'
                await update_user_ldata(user_id, key, literal_eval(data[4]))
            await update_user_settings(query, 'setdata', data[3])

        case 'gd' | 'rc' as value:
            du = 'rc' if value == 'gd' else 'gd'
            await gather(query.answer(),
                         update_user_ldata(user_id, 'default_upload', du))
            await update_user_settings(query)

        case 'back':
            handler_dict[user_id] = False
            await gather(query.answer(), update_user_settings(query))

        case 'rem_prename' | 'rem_sufname' | 'rem_dump_ch' | 'rem_remname' | 'rem_metadata' | 'rem_session_string' | 'rem_yt_opt' | 'rem_index_url' \
            | 'rem_gdrive_id' | 'rem_captions' | 'rem_excluded_extensions' | 'rem_rclone_path' as value:
            qdata = uset_data = ''
            match value:
                case 'rem_dump_ch':
                    await update_user_ldata(user_id, 'log_title', False)
                case 'rem_session_string':
                    if savebot := bot_dict[user_id]['SAVEBOT']:
                        await savebot.stop()
                case 'rem_captions':
                    qdata = 'capmode'
                    await update_user_ldata(user_id, 'fnamecap', True)
                case 'rem_rclone_path':
                    qdata = 'rctool'
                case 'rem_index_url' | 'rem_gdrive_id':
                    qdata = 'gdtool'
            if value in ('rem_rclone_path',
                         'rem_gdrive_id') and value in user_data.get(
                             user_id, {}):
                del user_data[user_id][value]
                if DATABASE_URL:
                    await DbManager().update_user_data(user_id)
            else:
                await update_user_ldata(user_id, value[4:], '')
            await gather(query.answer(),
                         update_user_settings(query, qdata, uset_data))

        case 'enable_pm' | 'enable_ss' | 'as_doc' | 'media_group' | 'fnamecap' | 'stop_duplicate' | 'use_sa' as value:
            qdata = uset_data = ''
            await update_user_ldata(user_id, value,
                                    not user_dict.get(value, False))
            if value == 'fnamecap':
                qdata = 'capmode'
            if value in ('stop_duplicate', 'use_sa'):
                qdata = 'gdtool'
            await gather(query.answer(),
                         update_user_settings(query, qdata, uset_data))

        case 'capmode' | 'gdtool' | 'rctool' as value:
            await gather(query.answer(), update_user_settings(query, value))

        case 'zipmode':
            try:
                zmode = data[3]
            except:
                zmode = user_dict.get('zipmode', 'zfolder')
            if zmode == user_dict.get('zipmode', '') and len(data) == 4:
                await query.answer('Already Selected!', True)
                return
            await gather(query.answer(),
                         update_user_ldata(user_id, 'zipmode', zmode))
            await update_user_settings(query, 'zipmode', zmode)

        case 'capmono' | 'capitalic' | 'capbold' | 'capnormal' as value:
            await update_user_ldata(user_id, 'caption_style',
                                    value.lstrip('cap'))
            await gather(query.answer(),
                         update_user_settings(query, 'capmode'))

        case 'close':
            handler_dict[user_id] = False
            await gather(query.answer(),
                         deleteMessage(message, message.reply_to_message))

        case 'rem_thumb' | 'rem_rclone_config' | 'rem_token_pickle' as value:
            match value:
                case 'rem_thumb':
                    path = ospath.join('thumbnails', f'{user_id}.jpg')
                case 'rem_rclone_config':
                    path = ospath.join('rclone', f'{user_id}.conf')
                case _:
                    path = ospath.join('tokens', f'{user_id}.pickle')
            key = value.lstrip('rem_')
            await update_user_ldata(user_id, key, '')
            if await aiopath.exists(path):
                await gather(query.answer(), clean_target(path))
                await update_user_settings(query)
                if DATABASE_URL:
                    await DbManager().update_user_doc(user_id, key)
            else:
                await gather(query.answer('Old Settings', True),
                             update_user_settings(query))

        case 'prepare':
            match data[3]:
                case 'rclone_config' | 'token_pickle':
                    await query.answer()
                    photo, document = False, True
                    pfunc = partial(add_rclone_pickle,
                                    query=query,
                                    key=data[3])
                case 'thumb':
                    await query.answer()
                    photo, document = True, False
                    pfunc = partial(set_thumb, query=query)
                case _:
                    handler_dict[user_id] = True
                    await query.answer(
                        'Don\'t forget add me to your chat!', True
                    ) if data[3] == 'dump_ch' else await query.answer()
                    photo = document = False
                    pfunc = partial(set_user_settings,
                                    query=query,
                                    key=data[3])
            await gather(update_user_settings(query, data[2], data[3]),
                         event_handler(client, query, pfunc, photo, document))

        # ----------------- New video tools handling: placeholders -----------------
        case 'video_tools':
            # Open the video tools menu (handled by get_user_settings branch 'video_tools')
            await gather(query.answer(),
                         update_user_settings(query, 'video_tools'))

        case 'video_merge' | 'video_compress' | 'video_convert' | 'video_mute' | 'video_add_audio' | 'video_trim' | 'video_watermark' as value:
            # Placeholder behaviour: inform user these are placeholder actions,
            # then return to the Video Tools menu.
            await query.answer()
            placeholder_text = ''
            match value:
                case 'video_merge':
                    placeholder_text = '<b>Merge Videos</b>\nThis is a placeholder. Implement merging logic here (combine multiple clips).'

                case 'video_compress':
                    placeholder_text = '<b>Compress Video</b>\nThis is a placeholder. Implement actual compress logic in video pipeline.'
                case 'video_convert':
                    placeholder_text = '<b>Convert Format</b>\nThis is a placeholder. Implement format conversion logic here.'
                case 'video_mute':
                    placeholder_text = '<b>Mute Video</b>\nThis is a placeholder. Implement audio removal logic here.'
                case 'video_add_audio':
                    placeholder_text = '<b>Add Audio</b>\nThis is a placeholder. Implement audio merging logic here.'
                case 'video_trim':
                    placeholder_text = '<b>Trim / Cut</b>\nThis is a placeholder. Implement trimming logic here.'
                case 'video_watermark':
                    placeholder_text = '<b>Add Watermark</b>\nThis is a placeholder. Implement watermark overlay logic here.'
            msg = await sendMessage(placeholder_text, message)
            # Auto delete the placeholder notification after a short while (non-blocking)
            bot_loop.create_task(auto_delete_message(message, msg, stime=6))
            # Return to the video tools menu
            await update_user_settings(query, 'video_tools')

        # -------------------------------------------------------------------------
        case _:
            # default fallback: answer and refresh
            await query.answer()
            await update_user_settings(query)

    # end match


async def event_handler(client: Client,
                        query: CallbackQuery,
                        pfunc: partial,
                        photo: bool = False,
                        document: bool = False):
    user_id = query.from_user.id
    handler_dict[user_id] = True
    start_time = time()

    async def event_filter(_, __, event):
        if photo:
            mtype = event.photo
        elif document:
            mtype = event.document
        else:
            mtype = event.text
        user = event.from_user or event.sender_chat
        return bool(user.id == user_id
                    and event.chat.id == query.message.chat.id and mtype)

    handler = client.add_handler(MessageHandler(pfunc,
                                                filters=create(event_filter)),
                                 group=-1)
    while handler_dict[user_id]:
        await sleep(0.5)
        if time() - start_time > 60:
            handler_dict[user_id] = False
            await update_user_settings(query)
    client.remove_handler(*handler)


@new_task
async def user_settings(_, message: Message):
    from_user = message.from_user
    handler_dict[from_user.id] = False
    if fmsg := await UseCheck(message).run():
        await auto_delete_message(message, fmsg)
        return
    msg, image, buttons = await get_user_settings(from_user, None, None)
    if await aiopath.exists(
            thumb := ospath.join('thumbnails', f'{message.from_user.id}.jpg')):
        image = thumb
    await sendPhoto(msg, message, image or config_dict['IMAGE_USETIINGS'],
                    buttons)


@new_task
async def set_premium_users(_, message: Message):
    if not config_dict['PREMIUM_MODE']:
        await sendMessage('<b>Premium Mode</b> is disable!', message)
        return
    reply_to = message.reply_to_message
    args = message.text.split()
    text = 'Reply to a user or send user ID with options (add/del) and duration time in day(s)'
    if not reply_to and len(args) == 1:
        await sendMessage(text, message)
        return
    if reply_to and len(args) > 1:
        premi_id = reply_to.from_user.id
        if args[1] == 'add':
            day = int(args[2])
    elif len(args) > 2:
        premi_id = int(args[2])
        if args[1] == 'add':
            day = int(args[3])
    elif len(args) == 2 and args[1] == 'list':
        text = 'Premium List:\n'
        i = 1
        for id_, value in user_data.items():
            if value.get('is_premium') and (
                    time_left := value['premium_left']) - time() > 1:
                text += f'{i}. @{value.get("user_name")} (<code>{id_}</code>) ~ {get_readable_time(time_left - time())}\n'
                i += 1
    else:
        await sendMessage(text, message)
        return

    user_text = ''
    if args[1] == 'add':
        duartion = int(time() + (86400 * day))
        text = f'🌚 Yeay, <b>{premi_id}</b> has been added as <b>Premium User</b> for {day} day(s).'
        user_text = f'Yeay 🌚, you have been added as <b>Premium User</b> for {day}(s).'
        await gather(update_user_ldata(premi_id, 'premium_left', duartion),
                     update_user_ldata(premi_id, 'is_premium', True))
    elif args[1] == 'del':
        text = f'🤡 Hmm, <b>{premi_id}</b> has been remove as <b>Premium User</b>!'
        user_text = 'Huhu 🤡, you have been deleted as <b>Premium User</b>!'
        await gather(update_user_ldata(premi_id, 'premium_left', 0),
                     update_user_ldata(premi_id, 'is_premium', False))
    msg = await sendMessage(text, message)
    if user_text:
        await sendCustom(user_text, premi_id)
    await auto_delete_message(message, msg)


@new_task
async def reset_daily_limit(_, message: Message):
    reply_to = message.reply_to_message
    args = message.text.split()
    if not reply_to and len(args) == 1:
        await sendMessage(
            'Reply to a user or send user ID to reset daily limit.', message)
        return
    if reply_to:
        user_id = reply_to.from_user.id
    elif len(args) > 1:
        user_id = int(args[1])
    await gather(update_user_ldata(user_id, 'daily_limit', 1),
                 update_user_ldata(user_id, 'reset_limit',
                                   time() + 86400))
    msg = await sendMessage('Daily limit has been reset.', message)
    await auto_delete_message(message, msg)


@new_task
async def send_users_settings(client: Client, message: Message):
    contents = []
    msg = ''
    if len(user_data) == 0:
        await sendMessage('No user data!', message)
        return
    for index, (uid, data) in enumerate(user_data.items(), start=1):
        if data.get(
                'is_sudo'
        ) and 'sudo_left' in data and data['sudo_left'] - time() <= 0:
            del user_data[uid]['sudo_left']
            await update_user_ldata(uid, 'is_sudo', False)
        uname = user_data[uid].get('user_name')
        msg += f'<b><a href="https://t.me/{uname}">{uname}</a></b>\n'
        msg += f'⁍ <b>User ID:</b> <code>{uid}</code>\n'
        for key, value in data.items():
            if key in ('session_token', 'session_time') or value == '':
                continue
            if key == 'reset_limit':
                value -= time()
                value = get_readable_time(0 if value <= 1 else value)
            elif key == 'daily_limit':
                value = f'{get_readable_file_size(value)}/{config_dict["DAILY_LIMIT_SIZE"]}GB'
            elif key in ('premium_left', 'sudo_left'):
                value = f'{get_readable_time(value - time())}'
            elif key in ('caption_style', 'zipmode'):
                value = str(value).title()
            elif key in ['thumb', 'rclone_config', 'token_pickle']:
                value = 'Exists' if value else 'Not Exists'
            elif key in [
                    'dump_ch', 'yt_opt', 'index_url', 'gdrive_id', 'prename',
                    'sufname', 'metadata'
            ]:
                value = f'<code>{value}</code>'
            elif str(value).lower() == 'true' or (
                    key in ['session_string', 'remname', 'captions']
                    and value):
                value = 'Yes'
            elif str(value).lower() == 'false':
                value = 'No'
            if key != 'user_name' and value != '':
                msg += f'⁍ <b>{key.replace("_", " ").title()}:</b> {value}\n'
        contents.append(f'{str(index).zfill(3)}. {msg}\n')
        msg = ''
    tele = TeleContent(message, max_page=5, direct=False)
    tele.set_data(contents,
                  f'<b>FOUND {len(contents)} USERS SETTINGS DATA</b>')
    text, buttons = await tele.get_content('usettings')
    msg = await sendMessage(text, message, buttons)
    event = Event()

    # ✅ Fixed block — replaced wrap_future() with create_task()
    @new_thread
    async def __event_handler():
        pfunc = partial(users_handler, event=event, tele=tele)
        handler = client.add_handler(CallbackQueryHandler(
            pfunc, filters=regex('^usettings') & user(message.from_user.id)),
                                     group=-1)
        try:
            await wait_for(event.wait(), timeout=180)
        except:
            pass
        finally:
            client.remove_handler(*handler)

    # Run in background correctly — no invalid await of Future
    bot_loop.create_task(__event_handler())
    await deleteMessage(msg, message)


async def users_handler(_,
                        query: CallbackQuery,
                        event=Event,
                        tele=TeleContent):
    message = query.message
    data = query.data.split()
    if data[2] == 'close':
        event.set()
        if tele:
            tele.cancel()
        await deleteMessage(message, message.reply_to_message)
    else:
        tdata = int(data[4]) if data[2] == 'foot' else int(data[3])
        text, buttons = await tele.get_content('usettings', data[2], tdata)
        if data[2] == 'page':
            await query.answer(f'Total Page ~ {tele.pages}', True)
            return
        if not buttons:
            await query.answer(text, True)
            return
        await gather(query.answer(), editMessage(text, message, buttons))


# Register bot command handlers
bot.add_handler(
    MessageHandler(set_premium_users,
                   filters=command(BotCommands.UserSetPremiCommand)
                   & CustomFilters.sudo))
bot.add_handler(
    MessageHandler(send_users_settings,
                   filters=command(BotCommands.UsersCommand)
                   & CustomFilters.sudo))
bot.add_handler(
    MessageHandler(reset_daily_limit,
                   filters=command(BotCommands.DailyResetCommand)
                   & CustomFilters.sudo))
bot.add_handler(
    MessageHandler(user_settings, filters=command(BotCommands.UserSetCommand)))
bot.add_handler(
    CallbackQueryHandler(edit_user_settings, filters=regex('^userset')))
