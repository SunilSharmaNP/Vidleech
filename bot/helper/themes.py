from html import escape

class BotTheme:
    @staticmethod
    def USER_SETTING(NAME, ID, USERNAME, LANG, DC):
        return (f'<b>⚙️ USER SETTINGS</b>\n\n'
                f'<b>👤 Name:</b> {NAME}\n'
                f'<b>🆔 User ID:</b> <code>{ID}</code>\n'
                f'<b>📝 Username:</b> {USERNAME}\n'
                f'<b>🌐 Language:</b> {LANG}\n'
                f'<b>📡 DC ID:</b> {DC}\n\n'
                f'<i>Select a category to configure your settings</i>')
    
    @staticmethod
    def UNIVERSAL(NAME, YT, DT, LAST_USED, BOT_PM, MEDIAINFO, SAVE_MODE, USESS):
        return (f'<b>🌐 UNIVERSAL SETTINGS</b>\n\n'
                f'<b>👤 User:</b> {NAME}\n\n'
                f'<b>📊 Settings Overview:</b>\n'
                f'<b>├ 📹 YT-DLP Options:</b> {YT}\n'
                f'<b>├ 📅 Daily Tasks:</b> {DT}\n'
                f'<b>├ ⏰ Last Used:</b> {LAST_USED}\n'
                f'<b>├ 💬 Bot PM:</b> {BOT_PM}\n'
                f'<b>├ 📺 MediaInfo:</b> {MEDIAINFO}\n'
                f'<b>├ 💾 Save Mode:</b> {SAVE_MODE}\n'
                f'<b>└ 🔐 User Session:</b> {USESS}\n\n'
                f'<i>Configure universal bot behavior and preferences</i>')
    
    @staticmethod
    def MIRROR(NAME, RCLONE, DDL_SERVER, DM, MREMNAME, MPREFIX, MSUFFIX, TMODE, USERTD):
        return (f'<b>☁️ MIRROR SETTINGS</b>\n\n'
                f'<b>👤 User:</b> {NAME}\n\n'
                f'<b>📤 Upload Configuration:</b>\n'
                f'<b>├ 📁 RClone:</b> {RCLONE}\n'
                f'<b>├ 🌐 DDL Servers:</b> {DDL_SERVER}\n'
                f'<b>├ 📊 Daily Mirror:</b> {DM}\n'
                f'<b>├ ✏️ Remname:</b> {MREMNAME}\n'
                f'<b>├ ⏮ Prefix:</b> {MPREFIX}\n'
                f'<b>├ ⏭ Suffix:</b> {MSUFFIX}\n'
                f'<b>├ 🗂 TD Mode:</b> {TMODE}\n'
                f'<b>└ 📂 User TDs:</b> {USERTD}\n\n'
                f'<i>Configure cloud upload destinations and formatting</i>')
    
    @staticmethod
    def LEECH(NAME, LPREFIX, LSUFFIX, LREMNAME, LCAPTION, LDUMP, THUMB, SPLIT_SIZE, LMETA, DL, LTYPE, MEDIA_GROUP):
        return (f'<b>⬇️ LEECH SETTINGS</b>\n\n'
                f'<b>👤 User:</b> {NAME}\n\n'
                f'<b>📥 Download Configuration:</b>\n'
                f'<b>├ ⏮ Prefix:</b> {LPREFIX}\n'
                f'<b>├ ⏭ Suffix:</b> {LSUFFIX}\n'
                f'<b>├ ✏️ Remname:</b> {LREMNAME}\n'
                f'<b>├ 💬 Caption:</b> {LCAPTION}\n'
                f'<b>├ 📤 Dump Channel:</b> {LDUMP}\n'
                f'<b>├ 🖼 Thumbnail:</b> {THUMB}\n'
                f'<b>├ ✂️ Split Size:</b> {SPLIT_SIZE}\n'
                f'<b>├ 📝 Metadata:</b> {LMETA}\n'
                f'<b>├ 📊 Daily Leech:</b> {DL}\n'
                f'<b>├ 📄 Leech Type:</b> {LTYPE}\n'
                f'<b>└ 📦 Media Group:</b> {MEDIA_GROUP}\n\n'
                f'<i>Configure Telegram upload settings and file formatting</i>')
    
    @staticmethod
    def RCLONE_TOOLS(NAME, RCLONE, RCLONE_PATH):
        return (f'<b>☁️ RCLONE CONFIGURATION</b>\n\n'
                f'<b>👤 User:</b> {NAME}\n\n'
                f'<b>📁 RClone Settings:</b>\n'
                f'<b>├ ⚙️ Config File:</b> {RCLONE}\n'
                f'<b>└ 📂 Upload Path:</b> {RCLONE_PATH}\n\n'
                f'<i>Configure RClone for cloud storage uploads</i>')
    
    @staticmethod
    def GDRIVE_TOOLS(NAME, GDRIVE_ID, INDEX_URL, TOKEN, USE_SA, STOP_DUP):
        return (f'<b>📁 GOOGLE DRIVE SETTINGS</b>\n\n'
                f'<b>👤 User:</b> {NAME}\n\n'
                f'<b>☁️ Drive Configuration:</b>\n'
                f'<b>├ 🆔 Drive ID:</b> {GDRIVE_ID}\n'
                f'<b>├ 🔗 Index URL:</b> {INDEX_URL}\n'
                f'<b>├ 🔑 Token Pickle:</b> {TOKEN}\n'
                f'<b>├ 🤖 Use SA:</b> {USE_SA}\n'
                f'<b>└ 🚫 Stop Duplicate:</b> {STOP_DUP}\n\n'
                f'<i>Configure Google Drive upload destination</i>')
    
    @staticmethod
    def CAPTION_SETTINGS(NAME, CAPTION_MODE, CUSTOM_CAP, FNAME_CAP, EXAMPLE):
        fname_text = f'<b>├ 📝 FName Caption:</b> {FNAME_CAP}\n' if FNAME_CAP != 'NOT SET' else ''
        return (f'<b>💬 CAPTION SETTINGS</b>\n\n'
                f'<b>👤 User:</b> {NAME}\n\n'
                f'<b>✍️ Caption Configuration:</b>\n'
                f'<b>├ 🎨 Caption Mode:</b> {CAPTION_MODE}\n'
                f'{fname_text}'
                f'<b>└ 📄 Custom Caption:</b> {CUSTOM_CAP}\n\n'
                f'<b>📋 Preview:</b> {EXAMPLE}\n\n'
                f'<i>Customize file caption appearance</i>')
    
    @staticmethod
    def ZIP_MODE_SETTINGS(NAME, CURRENT_MODE, PART_SIZE):
        return (f'<b>🗜 ZIP MODE SETTINGS</b>\n\n'
                f'<b>👤 User:</b> {NAME}\n\n'
                f'<b>📦 Available Modes:</b>\n'
                f'<b>├ 📁 Folders/Default:</b> Zip file/folder\n'
                f'<b>├ ☁️ Cloud Part:</b> Zip as {PART_SIZE} parts (Mirror)\n'
                f'<b>├ 📄 Each Files:</b> Zip each file separately\n'
                f'<b>├ ✂️ Part Mode:</b> Zip each file as parts if &gt; {PART_SIZE}\n'
                f'<b>└ 🤖 Auto Mode:</b> Auto-zip if file &gt; {PART_SIZE}\n\n'
                f'<b>⚡ Current Mode:</b> <code>{CURRENT_MODE}</code>\n\n'
                f'<i>*Seeding only works in Default Mode</i>')
    
    @staticmethod
    def DDL_SERVERS(NAME, GOFILE, STREAMTAPE):
        return (f'<b>🌐 DDL SERVER SETTINGS</b>\n\n'
                f'<b>👤 User:</b> {NAME}\n\n'
                f'<b>🔗 Available Servers:</b>\n'
                f'<b>├ 📂 GoFile:</b> {GOFILE}\n'
                f'<b>└ 🎬 StreamTape:</b> {STREAMTAPE}\n\n'
                f'<i>Configure direct download link servers</i>')
    
    @staticmethod
    def USER_TD_SETTINGS(NAME, SA_MAIL, USER_TDS_COUNT):
        return (f'<b>📂 USER TEAM DRIVE SETTINGS</b>\n\n'
                f'<b>👤 User:</b> {NAME}\n\n'
                f'<b>🗂 Team Drive Configuration:</b>\n'
                f'<b>├ 📧 SA Mail:</b> {SA_MAIL}\n'
                f'<b>└ 📊 Configured TDs:</b> {USER_TDS_COUNT}\n\n'
                f'<i>Manage personal Team Drive destinations</i>')
