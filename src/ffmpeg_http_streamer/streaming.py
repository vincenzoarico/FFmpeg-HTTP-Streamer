import socket
import subprocess
import sys
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from . import constants


def delete_stream_files(streaming_directory):
    target_extensions = (".ts", ".m3u", ".m3u8")
    deleted_count = 0
    undeleted_count = 0

    try:
        for filename in Path(streaming_directory).iterdir():
            if str(filename).lower().endswith(target_extensions):
                file_path = Path(streaming_directory) / filename
                try:
                    if Path(file_path).is_file():
                        Path(file_path).unlink()
                        deleted_count += 1
                except Exception as e:
                    print(
                        f"⚠️  Notice: Impossible to delete the file '{file_path}'. Reason: {e}.",
                        file=sys.stderr,
                    )
                    undeleted_count += 1

    except PermissionError:
        print(
            f"Error: insufficient permissions to read from the directory '{streaming_directory}'.",
            file=sys.stderr,
        )
        return False

    if undeleted_count > 0:
        print(f"{deleted_count} deleted stream files.")
        print(f"Error: {undeleted_count} undeleted stream files.", file=sys.stderr)
        return False

    if deleted_count > 0:
        print(f"{deleted_count} deleted stream files.")
    else:
        print("No stream files to delete found.")
    return True


def has_codec(stream_type, address, target_codec):
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-select_streams",
        stream_type,
        "-show_entries",
        "stream=codec_name",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        address,
    ]

    output = subprocess.check_output(cmd, text=True, timeout=60).strip()
    if not output:
        return (False, 0)

    codecs = output.lower().splitlines()

    if target_codec.lower() in codecs:
        return (True, len(codecs))
    return (False, len(codecs))


def transcode_input(address):
    try:
        has_codec_video, num_codec_video = has_codec("v", address, "h264")
        if has_codec_video is False and num_codec_video == 0:
            print("Error: the input doesn't have a codec video.", file=sys.stderr)
            sys.exit(1)
        elif has_codec_video is False and num_codec_video > 0:
            print("Adding video track: h264.")
    except Exception as e:
        print(
            f"Error: it isn't possible to check the input codec video: {e}.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        has_codec_audio, num_codec_audio = has_codec("a", address, "aac")
        if has_codec_audio is False and num_codec_audio == 0:
            print("The input doesn't have a codec audio.")
        elif has_codec_audio is False and num_codec_audio > 0:
            print("Adding audio track: aac.")
    except Exception as e:
        print(
            f"Error: it isn't possible to check the input codec audio: {e}.",
            file=sys.stderr,
        )
        sys.exit(1)

    codecs = []
    if has_codec_video and has_codec_audio:
        codecs = ["-map", "0", "-c", "copy"]
    elif has_codec_video and (has_codec_audio is False and num_codec_audio):
        codecs = [
            "-map",
            "0:v?",
            "-map",
            "0:a?",
            "-map",
            "0:a:0?",
            "-map",
            "0:s?",
            "-map",
            "0:d?",
            "-map",
            "0:t?",
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            f"-c:a:{num_codec_audio}",
            "aac",
            f"-ac:a:{num_codec_audio}",
            "2",
            f"-b:a:{num_codec_audio}",
            "192k",
            "-c:s",
            "copy",
            "-c:d",
            "copy",
            "-c:t",
            "copy",
        ]
    elif has_codec_video and (has_codec_audio is False and num_codec_audio == 0):
        codecs = ["-map", "0", "-c", "copy"]
    elif (has_codec_video is False and num_codec_video) and has_codec_audio:
        codecs = [
            "-map",
            "0:v?",
            "-map",
            "0:v:0?",
            "-map",
            "0:a?",
            "-map",
            "0:s?",
            "-map",
            "0:d?",
            "-map",
            "0:t?",
            "-c:v",
            "copy",
            f"-c:v:{num_codec_video}",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "23",
            "-c:a",
            "copy",
            "-c:s",
            "copy",
            "-c:d",
            "copy",
            "-c:t",
            "copy",
        ]
    elif (has_codec_video is False and num_codec_video) and (
        has_codec_audio is False and num_codec_audio
    ):
        codecs = [
            "-map",
            "0:v?",
            "-map",
            "0:v:0?",
            "-map",
            "0:a?",
            "-map",
            "0:a:0?",
            "-map",
            "0:s?",
            "-map",
            "0:d?",
            "-map",
            "0:t?",
            "-c:v",
            "copy",
            f"-c:v:{num_codec_video}",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "23",
            "-c:a",
            "copy",
            f"-c:a:{num_codec_audio}",
            "aac",
            f"-ac:a:{num_codec_audio}",
            "2",
            f"-b:a:{num_codec_audio}",
            "192k",
            "-c:s",
            "copy",
            "-c:d",
            "copy",
            "-c:t",
            "copy",
        ]

    elif (has_codec_video is False and num_codec_video) and (
        has_codec_audio is False and num_codec_audio == 0
    ):
        codecs = [
            "-map",
            "0:v?",
            "-map",
            "0:v:0?",
            "-map",
            "0:s?",
            "-map",
            "0:d?",
            "-map",
            "0:t?",
            "-c:v",
            "copy",
            f"-c:v:{num_codec_video}",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "23",
            "-an",
            "-c:s",
            "copy",
            "-c:d",
            "copy",
            "-c:t",
            "copy",
        ]

    return codecs


def run_python_http_server_process(private_ip, port, streaming_directory):
    class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=streaming_directory, **kwargs)

    try:
        server = HTTPServer((private_ip, port), CustomHTTPRequestHandler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()

        start_time = time.time()
        while time.time() - start_time < constants.PROCESS_STARTUP_TIMEOUT_S:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((private_ip, port))
                if result == 0:
                    print(f"HTTP Server started (port: {port})")
                    return server, server_thread

            time.sleep(0.5)

    except OSError as e:
        if e.errno == constants.EADDRINUSE:
            print(f"Error: Port {port} already in use.", file=sys.stderr)
        else:
            print(
                f"Error: HTTP Server stops during the starting with error: {e}",
                file=sys.stderr,
            )
        return None, None
    except Exception as e:
        print(
            f"Error: HTTP Server stops during the starting with error: {e}",
            file=sys.stderr,
        )
        return None, None

    else:
        return None, None


def run_ffmpeg_process(private_ip, port, streaming_directory, transcode, address):
    codecs = ["-map", "0", "-c", "copy"]
    if transcode:
        codecs = transcode_input(address)

    base_url = f"http://{private_ip}:{port}/"
    output = Path(streaming_directory) / "stream.m3u8"
    command = [
        "ffmpeg",
        "-re",
        "-i",
        address,
        *codecs,
        "-f",
        "hls",
        "-hls_time",
        "10",
        "-hls_list_size",
        "24",
        "-hls_flags",
        "delete_segments+independent_segments",
        "-hls_base_url",
        base_url,
        "-hls_allow_cache",
        "1",
        "-hls_segment_type",
        "mpegts",
        "-loglevel",
        "info",
        output,
    ]

    try:
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL)
    except OSError as e:
        if isinstance(e, FileNotFoundError):
            print("Error: The FFmpeg command wasn't found.", file=sys.stderr)
            return None
        print(
            f"Error: a problem during FFmpeg command startup: {e}.",
            file=sys.stderr,
        )
        return None

    print(f"FFmpeg process starts with PID: {process.pid}.\n")

    start_time = time.time()
    while time.time() - start_time < constants.PROCESS_STARTUP_TIMEOUT_S:
        return_code = process.poll()
        if return_code is not None:
            print(f"\nReturn code FFmpeg: {process.returncode}", file=sys.stderr)

            if process.returncode != 0:
                print(
                    f"Error: FFmpeg stops prematurely due to a generic error (code={process.returncode}). Check the stderr traceback.",
                    file=sys.stderr,
                )
            else:
                print(
                    "Error: FFmpeg stops prematurely without any error.",
                    file=sys.stderr,
                )
            return None
        time.sleep(0.5)

    return process
