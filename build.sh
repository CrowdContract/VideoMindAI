#!/usr/bin/env bash
set -e

# Install ffmpeg (available on Render's Ubuntu environment)
apt-get install -y ffmpeg 2>/dev/null || true

# Install Python dependencies
pip install -r requirements.txt
