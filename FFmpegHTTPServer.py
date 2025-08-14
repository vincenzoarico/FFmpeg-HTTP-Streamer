#!/usr/bin/env python3

# 1. chmod 755 FFmpegHTTPServer.py
# 2. mv FFmpegHTTPServer.py FFmpegHTTPServer
# 3. move FFmpegHTTPServer file to a directory that is present in your path variable (echo $PATH)

# LOCAL VIDEO COMMAND: FFmpegHTTPServer -p <port> -d <streamingDirectory_absolute_path> -l <local_absolute_path>
# REMOTE VIDEO COMMAND: FFmpegHTTPServer -p <port> -d <streamingDirectory_absolute_path> -r <remote_url>

import os
from urllib.parse import urlparse
import sys
import subprocess
import argparse
import time
import socket
import shutil
import psutil

VIDEO_EXTENSIONS = {
    '.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv',
    '.webm', '.mpeg', '.mpg', '.3gp', '.m4v', '.divx'
}

def getPrivateIP():
    allInterfaces = psutil.net_if_addrs()

    for interfaceName, interfaceAddresses in allInterfaces.items():

        if "loopback" in interfaceName.lower() or "virtual" in interfaceName.lower() or "vpn" in interfaceName.lower() or "tap" in interfaceName.lower() or "tun" in interfaceName.lower():
            continue

        for addr in interfaceAddresses:
            if addr.family == socket.AF_INET:
                IP = addr.address
                if IP.startswith('192.168.') or IP.startswith('10.'):
                    return IP

                if IP.startswith('172.'):
                    try:
                        secondOctet = int(IP.split('.')[1])
                        if 16 <= secondOctet <= 31:
                            return IP
                    except (IndexError, ValueError):
                        continue

    return None

def isValidDirectory(absolutePathDir):
    if not os.path.isabs(absolutePathDir):
        print(f"Error: the streaming directory path isn't absolute.", file=sys.stderr)
        return False
    if os.path.exists(absolutePathDir):
        if os.path.isdir(absolutePathDir):
            return True
        else:
            print(f"Error: the streaming directory path doesn't refer to a directory.", file=sys.stderr)
            return False
    else:
        try:
            os.makedirs(absolutePathDir, exist_ok=True)
            print(f"📁 Streaming directory created: {absolutePathDir}.")
            return True
        except Exception as e:
            print(f"Error: the streaming directory can't be created: {e}.", file=sys.stderr)
            return False

def isPortFree(privateIP, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.bind((privateIP, port))
            return True
        except OSError:
            return False

def isValidLocalVideo(absolutePathVideo):
    if not os.path.isabs(absolutePathVideo):
        print(f"Error: the local video path isn't absolute.", file=sys.stderr)
        return False

    if not os.path.isfile(absolutePathVideo):
        print(f"Error: the local video path doesn't refer to a video.", file=sys.stderr)
        return False

    _, ext = os.path.splitext(absolutePathVideo)
    if ext.lower() in VIDEO_EXTENSIONS:
        return True
    else:
        print(f"Error: the local video path refers to a file that isn't a video.", file=sys.stderr)
        return False

def parseArgs():
    parser = argparse.ArgumentParser(description="FFmpeg HTTP Server")
    parser.add_argument("-p", "--port",
                        type=int,
                        required=True,
                        help="Specify the server port (49152-65535).")
    parser.add_argument("-d", "--dir",
                        type=str,
                        default=os.getcwd(),
                        help="Specify the absolute path of the streaming directory (default: the current directory).")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-l", "--local_path",
        type=str,
        help="Specify the absolute path of the local video."
    )
    group.add_argument(
        "-r", "--remote_url",
        type=str,
        help="Specify the video remote url."
    )

    return parser.parse_args()

def checkArgs(args):
    if shutil.which('ffmpeg') is None or shutil.which('ffprobe') is None:
        print("Error: FFmpeg or FFprobe is not installed or not in PATH.", file=sys.stderr)
        sys.exit(1)

    privateIP = getPrivateIP()
    if privateIP is None:
        print(f"Error: the private IP wasn't found.", file=sys.stderr)
        sys.exit(1)

    port = args.port
    if not 49152 <= port <= 65535:
        print(f"Error: the port must be between 49152-65535.", file=sys.stderr)
        sys.exit(1)
    if not isPortFree(privateIP, port):
        print(f"Error: Port {port} is already in use on {privateIP}. Choose another port.", file=sys.stderr)
        sys.exit(1)

    streamingDirectory = args.dir
    if not isValidDirectory(streamingDirectory):
        sys.exit(1)

    isRemoteVideo = False
    address = ''
    if args.local_path:
        isRemoteVideo = False
        address = args.local_path
        if not isValidLocalVideo(address):
            sys.exit(1)
    elif args.remote_url:
        isRemoteVideo = True
        address = args.remote_url
        parsed = urlparse(address)
        isValidURL = parsed.scheme in ['http', 'https'] and parsed.netloc != ''
        if not isValidURL:
            print(f"Error: the video remote url is not valid.", file=sys.stderr)
            sys.exit(1)

    return privateIP, port, streamingDirectory, isRemoteVideo, address

def deleteStreamFiles(streamingDirectory):
    targetExtensions = ('.ts', '.m3u', '.m3u8')
    deletedCount = 0
    undeletedCount = 0

    try:
        for filename in os.listdir(streamingDirectory):
            if filename.lower().endswith(targetExtensions):
                filePath = os.path.join(streamingDirectory, filename)
                try:
                    if os.path.isfile(filePath):
                        os.remove(filePath)
                        deletedCount += 1
                except Exception as e:
                    print(f"⚠️  Notice: Impossible to delete the file '{filePath}'. Reason: {e}.", file=sys.stderr)
                    undeletedCount += 1

    except PermissionError:
        print(f"Error: insufficient permissions to read from the directory '{streamingDirectory}'.", file=sys.stderr)
        return False

    if undeletedCount > 0:
        print(f"{deletedCount} deleted stream files.")
        print(f"Error: {undeletedCount} undeleted stream files.", file=sys.stderr)
        return False

    if deletedCount > 0:
        print(f"{deletedCount} deleted stream files.")
    else:
        print("No stream files to delete found.")
    return True

def hasCodec(streamType, input, targetCodec):
    cmd = [
        'ffprobe', '-v', 'quiet',
        '-select_streams', f'{streamType}:0',
        '-show_entries', 'stream=codec_name',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        input
    ]

    output = subprocess.check_output(cmd, universal_newlines=True, timeout=60).strip()
    if not output:
        return None

    return targetCodec.lower() in output.lower().splitlines()

def transcodeInput(address):
    transcodedCodecVideo = [
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23']

    transcodedCodecAudio = [
        '-c:a', 'aac',
        '-b:a', '192k']

    codecVideo = [
        '-c:v', 'copy']

    codecAudio = [
        '-c:a', 'copy']

    try:
        hasCodecVideo = hasCodec('v', address, 'h264')
        if hasCodecVideo is None:
            print("Error: the input doesn't have a codec video.", file=sys.stderr)
            sys.exit(1)
        elif hasCodecVideo == False:
            print("Video transcoded to h264.")
            codecVideo = transcodedCodecVideo
    except Exception as e:
        print(f"Error: it isn't possible to check the input codec video: {e}.", file=sys.stderr)
        sys.exit(1)

    try:
        hasCodecAudio = hasCodec('a', address, 'aac')
        if hasCodecAudio is None:
            print("The input doesn't have a codec audio.")
            codecAudio = ['-an']
        elif hasCodecAudio == False:
            print("Audio transcoded to aac.")
            codecAudio = transcodedCodecAudio
    except Exception as e:
        print(f"Error: it isn't possible to check the input codec audio: {e}.", file=sys.stderr)
        sys.exit(1)

    return codecVideo, codecAudio

def runPythonHTTPServerProcess(port, streamingDirectory):
    command = [sys.executable, '-m', 'http.server', str(port)]

    try:
        process = subprocess.Popen(
            command,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            text=True,
            encoding='utf-8',
            errors='ignore',
            cwd=streamingDirectory
        )
    except OSError as e:
        if isinstance(e, FileNotFoundError):
            print(f"Error: The python3 command wasn't found.", file=sys.stderr)
            return None
        else:
            print(f"Error: a problem during python3 command startup.", file=sys.stderr)
            return None

    print(f"HTTP Server process starts with PID: {process.pid}.")

    startTime = time.time()
    while time.time() - startTime < 20:
        returnCode = process.poll()
        if process.poll() is not None:
            print(f"\nReturn code HTTP Server: {process.returncode}", file=sys.stderr)

            if process.returncode != 0:
                print(f"Error: the HTTP Server stops prematurely due to a generic error (code={process.returncode}).", file=sys.stderr)
            else:
                print("Error: the HTTP Server stops prematurely without any error.", file=sys.stderr)
            return None
        time.sleep(0.5)

    return process

def runFFmpegProcess(privateIP, port, streamingDirectory, address):
    codecVideo, codecAudio = transcodeInput(address)
    baseURL = f'http://{privateIP}:{port}/'
    output = os.path.join(streamingDirectory, 'stream.m3u8')
    command = [
        'ffmpeg', '-re',
        '-i', address] + codecVideo + codecAudio + [
        '-f', 'hls',
        '-hls_time', '10',
        '-hls_list_size', '24',
        '-hls_flags', 'delete_segments+independent_segments',
        '-hls_base_url', baseURL,
        '-hls_allow_cache', '1',
        '-hls_segment_type', 'mpegts',
        '-loglevel', 'info',
        output]

    try:
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL)
    except OSError as e:
        if isinstance(e, FileNotFoundError):
            print(f"Error: The FFmpeg command wasn't found.", file=sys.stderr)
            return None
        else:
            print(f"Error: a problem during FFmpeg command startup: {e}.", file=sys.stderr)
            return None

    print(f"FFmpeg process starts with PID: {process.pid}.\n")

    startTime = time.time()
    while time.time() - startTime < 20:
        returnCode = process.poll()
        if returnCode is not None:
            print(f"\nReturn code FFmpeg: {process.returncode}", file=sys.stderr)

            if process.returncode != 0:
                print(f"Error: FFmpeg stops prematurely due to a generic error (code={process.returncode}). Check the stderr traceback.", file=sys.stderr)
            else:
                print("Error: FFmpeg stops prematurely without any error.", file=sys.stderr)
            return None
        time.sleep(0.5)

    return process

def main():
    args = parseArgs()

    PRIVATE_IP, PORT, STREAMING_DIR, IS_REMOTE_VIDEO, ADDRESS = checkArgs(args)
    print(f"- IP Server: {PRIVATE_IP}")
    print(f"- Server PORT: {PORT}")
    print(f"- Directory server (streaming): {STREAMING_DIR}")
    if IS_REMOTE_VIDEO:
        print(f"- Video source: Remote URL -> {ADDRESS}")
    else:
        print(f"- Video source: Local file -> {ADDRESS}")

    serverProcess = None
    FFmpegProcess = None

    try:
        serverProcess = runPythonHTTPServerProcess(PORT, STREAMING_DIR)
        if serverProcess is None:
            sys.exit(1)

        FFmpegProcess = runFFmpegProcess(PRIVATE_IP, PORT, STREAMING_DIR, ADDRESS)
        if FFmpegProcess is None:
            sys.exit(1)

        print("\n✅ FFmpeg HTTP Server successfully started!")
        print(f"Open this URL in a player like VLC: http://{PRIVATE_IP}:{PORT}/stream.m3u8")
        print("Press Ctrl+C to stop the streaming and clean the stream files in the streaming directory.\n")

        FFmpegProcess.wait()

        time.sleep(10)

    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Closing of current processes...")
        sys.exit(130)
    finally:
        if FFmpegProcess and FFmpegProcess.poll() is None:
            print("FFmpeg termination...")
            FFmpegProcess.terminate()
            FFmpegProcess.wait()
            print("FFmpeg process terminated.")

        if serverProcess and serverProcess.poll() is None:
            print("Server HTTP termination...")
            serverProcess.terminate()
            serverProcess.wait()
            print("HTTP Server process terminated.")

        if not deleteStreamFiles(STREAMING_DIR):
            print(f"Delete manually the stream files in the streaming directory:{STREAMING_DIR}.")

if __name__ == "__main__":
    main()
