# FFmpeg-HTTP-Streamer

![FFmpeg 7.1.1](https://shields.io/badge/FFmpeg-%23171717.svg?logo=ffmpeg&style=for-the-badge&labelColor=171717&logoColor=5cb85c)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-orange)

A simple, lightweight Python script that sets up an HTTP server for streaming local or remote videos using FFmpeg. It transcodes videos to HLS (HTTP Live Streaming) format (if necessary) and serves them over a local network (LAN) via Python's built-in HTTP server module.

It's perfect for watching your videos on other devices within the same network (like a Smart TV, tablet, or another computer) using any player (e.g., VLC, IINA, mpv). It supports both local video files and remote URLs, with automatic codec checking and transcoding for compatibility.

## Features

- 🎥 Streams local videos or remote URLs via HTTP on a specified port in the dynamic range 49152-65535)
- 🌐 Cross-platform support (Linux, macOS, Windows)
- 📱 Compatible with any player (VLC, IINA, mpv, QuickTime, M3U IPTV app for TV)
- 🔄 Automatic video/audio transcoding when needed (H.264/AAC)
- 🧹 Automatic cleanup of streaming files on exit
- 🔍 Automatic network interface detection (private IP)
- ⚡ Real-time streaming with FFmpeg

## Installation without using Docker

Prerequisites:
- **Python 3.7+**: Ensure Python is installed and in your PATH.
- **FFmpeg 7.1.1 and FFprobe 7.1.1**: Must be installed and available in your PATH. This script relies on them for transcoding and probing.
- **Poetry**: A Python dependency and package manager.
- A **video player** like VLC to open the stream URL.

**Note**: This script is primarily tested on macOS but is designed to be cross-platform. On Windows, some features may behave differently due to OS limitations.

### FFmpeg 7.1.1 Installation

**FFmpeg 7.1.1 must be installed and available in your system PATH.**

#### Linux (Ubuntu/Debian)

Install all prerequisites using Docker. Go to the [section](#installation-using-docker).

#### macOS

```bash
# Using Homebrew
brew tap-new mytaps/ffmpeg7
cd $(brew --repo mytaps/ffmpeg7)/Formula
curl https://raw.githubusercontent.com/Homebrew/homebrew-core/8c96d970d58cf9e4d9c7b062355a6f2a8d4288e9/Formula/f/ffmpeg%407.rb > ffmpeg@7.rb
brew install mytaps/ffmpeg7/ffmpeg@7
brew link --force --overwrite ffmpeg@7
```

#### Windows

1. Download FFmpeg 7.1.1 "Péter" from this [link](https://github.com/BtbN/FFmpeg-Builds/releases/download/autobuild-2025-09-14-13-31/ffmpeg-n7.1.1-152-gf893221c8d-win64-lgpl-7.1.zip)
2. Extract the archive to a folder (e.g., `C:\FFmpeg`)
3. Add the `bin` folder to your system PATH:
   - Open System Properties → Advanced → Environment Variables
   - Edit the `Path` variable and add `C:\FFmpeg\bin`
   - Restart your command prompt

### Poetry

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install pipx
pipx ensurepath
```

Then, if you have a Zsh shell: 
```bash
source ~/.zshrc
```

Or, if you have a bash shell:
```bash
source ~/.bashrc
```

Finally:
```bash
pipx install poetry
```

#### macOS

```bash
brew update
brew install pipx
pipx ensurepath
```

Then, if you have a Zsh shell: 
```bash
source ~/.zshrc
```

Or, if you have a bash shell:
```bash
source ~/.bashrc
```

Finally:
```bash
pipx install poetry
```

#### Windows

[Follow the official guide to install pipx](https://pipx.pypa.io/stable/installation/#on-windows)

Finally:
```bash
pipx install poetry
```

### FFmpeg-HTTP-Streamer installation using Poetry

```bash
git clone https://github.com/vincenzoarico/FFmpeg-HTTP-Streamer.git
cd FFmpeg-HTTP-Streamer
poetry install
```

## Installation using Docker

Install all prerequisites using the following Docker command:

```bash
docker run -it --name FFmpeg-HTTP-Streamer -p 50000:50000 vincenzoarico/ffmpeg-http-streamer:1.0
exit
```

## Usage

If you have installed it using Docker:

```bash
docker start FFmpeg-HTTP-Streamer
docker exec -ti -w /root FFmpeg-HTTP-Streamer bash
```

Navigate to the **folder of the repository**:

```bash
cd FFmpeg-HTTP-Streamer
```

Activate the virtual environment created by Poetry:
```bash
# macOS / Linux
source $(poetry env info --path)/bin/activate

# Windows
& $(poetry env info --path)\Scripts\activate.ps1
```

Now, you can use the `ffmpeg-http-streamer` command in any path of your terminal.

**Note**: The command to deactivate the virtual environment created by Poetry is `deactivate`.

### Command Syntax

```bash
ffmpeg-http-streamer -p <port> [-d <streaming_directory>] [--transcode] -l <local_video_path> | -r <remote_video_url>
```

### Parameters

- `-p, --port`(required): Server port (must be between 49152-65535, e.g., 50000). The script checks if it's free.
- `-d, --dir`(optional): **Path** to the streaming directory (where streaming files are generated). Defaults to the current directory. It will be created if it doesn't exist.
- `-t, --transcode` (optional): Flag to activate the transcoding (if needed).
- `-l, --local_path`(mutually exclusive with -r): **Absolute path** to a local video file (e.g., /path/to/video.mp4). Supports common extensions like .mp4, .mkv, etc.
- `-r, --remote_url`(mutually exclusive with -l): Remote video URL (e.g., https://example.com/video.mp4). Must be HTTP/HTTPS.

**Important**: You must specify either `-l` (local file) or `-r` (remote URL), but not both.

### Examples

#### Stream a local video file using transcoding

```bash
ffmpeg-http-streamer -p 50000 -d /home/user/streaming --transcode -l /home/user/videos/movie.mp4
```

#### Stream a remote video URL without using transcoding

```bash
ffmpeg-http-streamer -p 50000 -d /home/user/streaming -r 'https://example.com/video.mp4'
```

#### Using the current directory for streaming

```bash
ffmpeg-http-streamer -p 50000 -l /path/to/video.mp4
```

### Getting Help

```bash
ffmpeg-http-streamer --help
```

## How to Access the Stream

Once the server starts, you'll see output like:
```
✅ FFmpeg HTTP Server successfully started!
Open this URL in a player like VLC: http://<yourPrivateIP>:<port>/stream.m3u8
```

1. Open a media player (like VLC, IINA, mpv).
2. Find the "Open Network Stream" option (or similar).
3. Paste the URL provided by the script.

## How Automatic Transcoding works

The **--transcode** flag in the command activates the transcoding.

Running it with the --transcode flag, if your video doesn't have a H.264/AAC track among its tracks, the script will append a new video/audio track and transcode it in H.264/AAC format for optimal streaming compatibility. It never deletes already existing video/audio tracks.

## Supported Video Formats

The script supports common video formats, including:
- MP4, MKV, AVI, MOV, FLV, WMV
- WebM, MPEG, MPG, 3GP, M4V, DivX

## Troubleshooting

### Common Issues

1. **"FFmpeg or FFprobe is not installed or not in PATH"**
   - Ensure FFmpeg is properly installed and accessible from the command line
   - Test with: `ffmpeg -version`

2. **"Port already in use"**
   - Choose a different port number
   - Check what's using the port: `netstat -tulpn | grep <port>` (Linux/macOS)

3. **"Permission denied" errors**
   - Ensure the streaming directory is writable
   - On Linux/macOS, check file permissions

### Windows-Specific Notes

- Use forward slashes or double backslashes in paths: `C:/Videos/movie.mp4` or `C:\\Videos\\movie.mp4`
- Ensure Python and pip are properly installed and in your PATH

## Technical Details

- **Segment Duration**: 10 seconds
- **Playlist Size**: 24 segments (4 minutes of content)
- **Network Detection**: Automatically finds your private IP address

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.
