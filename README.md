# FFmpeg-HTTP-Streamer

![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-orange)

A simple lightweight Python script that sets up an HTTP server for streaming local or remote videos using FFmpeg. It transcodes videos to HLS (HTTP Live Streaming) format (if necessary) and serves them over a local network (LAN) via Python's built-in HTTP server module.

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

## Usage

### Command Syntax

```bash
# Linux/macOS (if installed in PATH)
FFmpegHTTPServer -p <port> -d <streaming_directory> -l <local_video_path>
FFmpegHTTPServer -p <port> -d <streaming_directory> -r <remote_video_url>

# Windows or direct Python execution
python FFmpegHTTPServer.py -p <port> -d <streaming_directory> -l <local_video_path>
python FFmpegHTTPServer.py -p <port> -d <streaming_directory> -r <remote_video_url>
```

### Parameters

- `-p, --port`(required): Server port (must be between 49152-65535, e.g., 50000). The script checks if it's free.
- `-d, --dir`(optional): **Absolute path** to the streaming directory (where HLS files are generated). Defaults to the current directory. It will be created if it doesn't exist.
- `-l, --local_path`(mutually exclusive with -r): **Absolute path** to a local video file (e.g., /path/to/video.mp4). Supports common extensions like .mp4, .mkv, etc.
- `-r, --remote_url`(mutually exclusive with -l): Remote video URL (e.g., https://example.com/video.mp4). Must be HTTP/HTTPS.

**Important**: You must specify either `-l` (local file) or `-r` (remote URL), but not both.

### Examples

#### Stream a local video file

**Linux/macOS:**
```bash
FFmpegHTTPServer -p 8080 -d /home/user/streaming -l /home/user/videos/movie.mp4
```

**Windows:**
```cmd
python FFmpegHTTPServer.py -p 8080 -d C:\Users\YourName\streaming -l C:\Users\YourName\Videos\movie.mp4
```

#### Stream a remote video URL

**Linux/macOS:**
```bash
FFmpegHTTPServer -p 8080 -d /home/user/streaming -r https://example.com/video.mp4
```

**Windows:**
```cmd
python FFmpegHTTPServer.py -p 8080 -d C:\Users\YourName\streaming -r https://example.com/video.mp4
```

#### Using the current directory for streaming

```bash
# Linux/macOS
FFmpegHTTPServer -p 8080 -l /path/to/video.mp4

# Windows
python FFmpegHTTPServer.py -p 8080 -r https://example.com/video.mp4
```

### Getting Help

```bash
# Linux/macOS
FFmpegHTTPServer --help

# Windows
python FFmpegHTTPServer.py --help
```

## How to Access the Stream

Once the server starts, you'll see output like:
```
✅ FFmpeg HTTP Server successfully started!
Open this URL in a player like VLC: http://<yourPrivateIP>:<port>/stream.m3u8
```

1. Open a media player that supports HLS streams (like VLC, IINA, mpv).
2. Find the "Open Network Stream" option (or similar).
3. Paste the URL provided by the script.

## Supported Video Formats

The script supports common video formats, including:
- MP4, MKV, AVI, MOV, FLV, WMV
- WebM, MPEG, MPG, 3GP, M4V, DivX

**Automatic Transcoding**: If your video isn't in H.264/AAC format, the script will automatically transcode it for optimal streaming compatibility.

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

4. **Video not playing**
   - Wait a few seconds for the stream to initialize
   - Check that your player supports HLS streams
   - Verify the video file is not corrupted

### Windows-Specific Notes

- Use forward slashes or double backslashes in paths: `C:/Videos/movie.mp4` or `C:\\Videos\\movie.mp4`
- Ensure Python and pip are properly installed and in your PATH

## Technical Details

- **Streaming Protocol**: HLS (HTTP Live Streaming)
- **Video Codec**: H.264 (transcoded if necessary)
- **Audio Codec**: AAC (transcoded if necessary)
- **Segment Duration**: 10 seconds
- **Playlist Size**: 24 segments (4 minutes of content)
- **Network Detection**: Automatically finds your private IP address

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.
