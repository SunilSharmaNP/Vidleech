#!/bin/bash

# Export Replit secrets to environment variables
export OWNER_ID="${OWNER_ID:-$REPL_OWNER_ID}"

echo "Starting Aria2c RPC server..."
aria2c --enable-rpc --rpc-listen-all=false --rpc-listen-port=6800 \
  --max-connection-per-server=10 --rpc-max-request-size=1024M \
  --seed-time=0.01 --min-split-size=10M --follow-torrent=mem \
  --split=10 --daemon=true --allow-overwrite=true --max-overall-download-limit=0 \
  --max-overall-upload-limit=1K --max-concurrent-downloads=15 \
  --continue=true --peer-id-prefix=-qB4500- --user-agent=qBittorrent/4.5.0 \
  --peer-agent=qBittorrent/4.5.0 --disk-cache=64M --bt-stop-timeout=1200 \
  --conf-path=a2c.conf

echo "Waiting for Aria2c to start..."
sleep 2

echo "Starting Telegram bot..."
python3 update.py
exec python3 -m bot
