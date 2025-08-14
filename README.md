# FFmpeg-HTTP-Streamer

A simple Python script that sets up an HTTP server for streaming local or remote videos using FFmpeg. It transcodes videos to HLS (HTTP Live Streaming) format (if necessary) and serves them over a local network (LAN) via Python's built-in HTTP server module.

It's perfect for watching your videos on other devices within the same network (like a Smart TV, tablet, or another computer) using any player that supports HLS streams (e.g., VLC, IINA, mpv). It supports both local video files and remote URLs, with automatic codec checking and transcoding for compatibility.

## Features

- 🎥 Streams local videos or remote URLs via HLS (HTTP Live Streaming on a specified port in the dynamic range 49152-65535)
- 🌐 Cross-platform support (Linux, macOS, Windows)
- 📱 Compatible with any HLS-capable player (VLC, IINA, mpv, QuickTime, M3U IPTV app for TV)
- 🔄 Automatic video/audio transcoding when needed (H.264/AAC)
- 🧹 Automatic cleanup of streaming files on exit
- 🔍 Automatic network interface detection (private IP)
- ⚡ Real-time streaming with FFmpeg

## Prerequisites

- **Python 3.6+**: Ensure Python is installed and in your PATH.
- **FFmpeg and FFprobe**: Must be installed and available in your PATH. This script relies on them for transcoding and probing.
- **psutil Python library**: Required for detecting the private IP address.
- A **video player** like VLC to open the stream URL.

**Note**: This script is primarily tested on macOS but is designed to be cross-platform. On Windows, some features may behave differently due to OS limitations.

### FFmpeg Installation

**FFmpeg must be installed and available in your system PATH.**

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS

```bash
# Using Homebrew
brew install ffmpeg
```

#### Windows

1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract the archive to a folder (e.g., `C:\ffmpeg`)
3. Add the `bin` folder to your system PATH:
   - Open System Properties → Advanced → Environment Variables
   - Edit the `Path` variable and add `C:\ffmpeg\bin`
   - Restart your command prompt

### Python Dependencies

Install the required Python package:

```bash
pip install psutil
```

Or on Linux/macOS:

```bash
python3 -m pip install psutil
```

## Installation

### Linux/macOS (Command-line usage)

1. Download the script:
```bash
git clone https://github.com/vincenzoarico/FFmpeg-HTTP-Streamer.git
cd FFmpeg-HTTP-Streamer
```

2. Make it executable and rename:
```bash
chmod +x FFmpegHTTPServer.py
mv FFmpegHTTPServer.py FFmpegHTTPServer
```

3. Move to a directory in your PATH (check with `echo $PATH` on Linux/macOS):
```bash
sudo mv FFmpegHTTPServer /usr/local/bin/
# or
mv FFmpegHTTPServer ~/.local/bin/  # Make sure ~/.local/bin is in your PATH
```

### Windows

1. Download `FFmpegHTTPServer.py` to your desired location
2. Use Python to run the script (see usage examples below)

**Windows Note**: You cannot run the script directly as a command, unlike on Linux/macOS. Instead, always invoke it with python FFmpegHTTPServer.py (or python3 FFmpegHTTPServer.py if you have multiple Python versions).
