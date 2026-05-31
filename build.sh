#!/usr/bin/env bash
set -e

echo "==> Installing ffmpeg..."
apt-get install -y ffmpeg 2>/dev/null || true

echo "==> Upgrading pip + setuptools..."
pip install --upgrade pip setuptools wheel

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Build complete."
