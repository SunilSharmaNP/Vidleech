# Overview

This is a Telegram bot application built with Python that provides comprehensive file management, download, upload, and manipulation capabilities. The bot serves as a multi-purpose utility for handling various types of content including torrents, direct downloads, Google Drive operations, video processing, and RSS feeds. It integrates with multiple external services and provides both mirroring (cloud storage) and leaching (direct upload to Telegram) functionality.

The application uses Pyrogram as the Telegram client library and supports advanced features like qBittorrent, Aria2c, JDownloader integration, video tools, web scraping, and automated task management.

# User Preferences

Preferred communication style: Simple, everyday language.

# Recent Changes

## November 11, 2025 - User Settings UI Bug Fixes

### Fixed All Settings Menus (WZML-X Style)
- **Universal Settings Menu**: Fixed YT-DLP Options, Session String, Bot PM, MediaInfo, Save Mode handlers
- **Mirror Settings Menu**: Fixed RClone, Prefix, Suffix, Rename, DDL Servers, User TD functionality
- **Leech Settings Menu**: Fixed Thumbnail, Split Size, Caption, Metadata, Attachment URL, Dump options

### Resolved Issues
1. **Status Indicators**: All "Not Exists ❌" indicators now properly read from user_data/config_dict
2. **Callback Query Errors**: Fixed all callback handlers to route to functional handlers or honest placeholders
3. **Navigation Flow**: Fixed back button routing and menu navigation throughout all settings
4. **Split Size Menu**: Added proper split_size_menu handler with Set Split Size and Toggle Equal Splits
5. **Attachment URL**: Added support for attachment_url configuration in Leech Settings
6. **DDL Servers**: Implemented placeholder panel (feature under development)
7. **Removed Auto Poster**: Removed non-functional placeholder button

### UI Improvements
- Implemented WZML-X master branch inspired design style
- Added proper emoji status indicators (✅ ❌)
- Consistent button layouts across all settings menus
- Proper text formatting with bold/italic HTML markup
- Informative status displays for all user configurations

### Files Modified
- `bot/modules/user_settings.py`: Complete refactor of settings menu system
- `.gitignore`: Added Python, MongoDB, and bot-specific ignore patterns
- `config.env`: Created template for required environment variables

### Configuration Required
The bot requires the following environment variables to run (copy from config.env to .env):
- `BOT_TOKEN`: Telegram bot token from @BotFather
- `API_ID`: Telegram API ID from my.telegram.org
- `API_HASH`: Telegram API hash from my.telegram.org
- `DATABASE_URL`: MongoDB connection string
- `OWNER_ID`: Telegram user ID of the bot owner

# System Architecture

## Core Framework
- **Backend Framework**: Flask (minimal web server for health checks)
- **Telegram Client**: Pyrogram/Pyrofork v2.2.11 for bot interactions
- **Async Runtime**: uvloop for optimized asyncio event loop
- **Task Scheduling**: APScheduler for cron jobs and RSS monitoring
- **Database**: MongoDB via PyMongo for persistent storage of user settings, configurations, and task data

## Download & Transfer Architecture
- **Torrent Downloads**: 
  - qBittorrent API client for torrent management
  - Aria2c RPC client for direct downloads and torrents
  - JDownloader (MyJDownloader API) for premium host downloads
- **Cloud Storage**:
  - Google Drive API integration for cloning, uploading, and file management
  - Rclone for multi-cloud support (configured via user-specific rclone.conf files)
  - Telegram as both source and destination for file transfers
- **Direct Downloads**: Custom link generator supporting multiple file hosting sites with bypass capabilities

## Video Processing Pipeline
- **FFmpeg Integration**: Video compression, trimming, audio extraction, format conversion
- **Metadata Handling**: MoviePy and mutagen for media file manipulation
- **Thumbnail Generation**: PIL/Pillow for image processing
- **Sample Video Creation**: Automated sample generation from larger videos

## Authentication & Authorization
- **Multi-tier Access Control**:
  - Owner privileges (full system access)
  - Sudo users (elevated permissions)
  - Authorized users (standard access)
  - Premium user mode (optional gated features)
- **Session Management**: User-specific Pyrogram sessions for custom Telegram operations
- **Token-based Authentication**: Google OAuth tokens stored per-user in database

## File Management System
- **Download Directory Structure**: Organized by task ID (`/downloads/{message_id}/`)
- **Archive Handling**: Support for ZIP, RAR, 7Z with extraction capabilities
- **Split File Management**: Automatic detection and handling of split archives
- **Cleanup System**: Automated cleanup of temporary files and completed tasks

## External Service Integrations
- **Telegraph**: For creating web pages with search results and file listings
- **Heroku**: Optional deployment and management via Heroku API
- **URL Shorteners**: Configurable shortener services for generated links
- **Search Engines**: qBittorrent search plugins and custom API-based torrent search
- **Wayback Machine**: Web page archiving functionality
- **gTTS**: Text-to-speech conversion
- **IMDb/AniList**: Media information scraping via cinemagoer and GraphQL APIs

## Task Management & Queueing
- **Concurrent Task Handling**: AsyncIO-based task dictionary with locking mechanisms
- **Queue System**: Separate download and upload queues with configurable limits
- **Status Tracking**: Real-time status updates for active downloads/uploads
- **Task Resumption**: Incomplete task recovery and resumption capabilities
- **Multi-instance Support**: Bulk operations and batch processing

## Configuration Management
- **Environment Variables**: Primary configuration via `.env` file
- **Database-backed Settings**: Dynamic configuration stored in MongoDB
- **User-level Customization**: Per-user settings for upload destinations, leech preferences, filters
- **Runtime Updates**: Settings can be modified without restart via bot commands

## Message Handling & User Interface
- **Inline Keyboards**: Extensive use of callback queries for interactive menus
- **Auto-deletion**: Configurable auto-delete for command messages and responses
- **Progress Updates**: Real-time progress bars and status messages
- **Multi-language Support**: gTTS integration for multiple languages
- **Markdown/HTML Formatting**: Rich text formatting for all bot responses

## Monitoring & Logging
- **File-based Logging**: Centralized logging to `log.txt` with rotation
- **Keep-alive Service**: `alive.py` script for health monitoring (pings BASE_URL)
- **RSS Monitoring**: Scheduled RSS feed checks with configurable intervals
- **System Stats**: CPU, RAM, disk usage tracking via psutil

## Data Persistence Strategy
- **MongoDB Collections**:
  - User data (settings, tokens, sessions)
  - RSS subscriptions
  - Bot configuration
  - Task history
- **File-based Storage**:
  - User thumbnails (`thumbnails/{user_id}.jpg`)
  - Google tokens (`tokens/{user_id}.pickle`)
  - Rclone configs (`rclone/{user_id}.conf`)
  - User sessions (stored in database as strings)

## Security Considerations
- **Credential Encryption**: AES encryption for MyJDownloader credentials
- **Token Isolation**: Per-user token storage prevents cross-user access
- **Blacklist Filtering**: Global and user-level file extension/keyword filters
- **Rate Limiting**: Premium mode gating and daily limits per user
- **Session Validation**: Regular session checks and re-authentication flows

# External Dependencies

## Third-party APIs
- **Google Drive API**: File operations, search, cloning (requires OAuth2 credentials)
- **MyJDownloader API**: Premium host downloads (requires JD account)
- **Telegram Bot API**: Core bot functionality via Pyrogram
- **Telegraph API**: Creating web pages for listings
- **URL Shortener APIs**: Configurable shortening services
- **AniList GraphQL API**: Anime/manga information
- **Torrent Search APIs**: Custom search API endpoints

## Cloud Services
- **MongoDB Atlas/Self-hosted**: Primary database (connection via DATABASE_URL)
- **Heroku** (Optional): Deployment platform with API integration
- **Rclone Cloud Backends**: Supports 40+ cloud storage providers

## Download Tools
- **qBittorrent**: Torrent client (expects local instance on default port)
- **Aria2c**: Download manager (expects local instance on port 6800)
- **yt-dlp**: Video downloads from streaming sites
- **JDownloader**: Premium link downloads via MyJD API

## Processing Libraries
- **FFmpeg**: Video/audio processing (system dependency)
- **ImageMagick** (implied): Image manipulation capabilities
- **Rclone**: Cloud transfer utility (system dependency)

## Database
- **MongoDB**: Document database for all persistent storage
  - Connection string via `DATABASE_URL` environment variable
  - Uses PyMongo driver with motor for async operations
  - Collections: users, settings, rss, bot_config

## External Hosts & Services
- **File Hosting Sites**: Direct download link generation for 50+ sites
- **Stream Services**: Optional video streaming via web server
- **Index Scrapers**: Directory listing extraction from open directories