# LOCAL VIDEO COMMAND: ffmpeg-http-streamer -p <port> -d <streaming_directory_path> --transcode -l <local_absolute_path> (-d, --transcode optionals)
# REMOTE VIDEO COMMAND: ffmpeg-http-streamer -p <port> -d <streaming_directory_path> --transcode -r <remote_url> (-d, --transcode optionals)

import argparse
import shutil
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

from . import constants, network, streaming, validation


def parse_args():
    parser = argparse.ArgumentParser(description="FFmpeg HTTP Server")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        required=True,
        help="Specify the server port (49152-65535).",
    )
    parser.add_argument(
        "-d",
        "--dir",
        type=str,
        default=Path.cwd(),
        help="Specify the absolute path of the streaming directory (default: the current directory).",
    )
    parser.add_argument(
        "-t",
        "--transcode",
        action="store_true",
        help="Enable automatic video/audio transcoding when needed (H.264/AAC)",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-l",
        "--local_path",
        type=str,
        help="Specify the absolute path of the local video.",
    )
    group.add_argument(
        "-r",
        "--remote_url",
        type=str,
        help="Specify the video remote url.",
    )

    return parser.parse_args()


def check_args(args):
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        print(
            "Error: FFmpeg or FFprobe is not installed or not in PATH.",
            file=sys.stderr,
        )
        sys.exit(1)

    private_ip = network.get_private_ip()
    if private_ip is None:
        print("Error: the private ip wasn't found.", file=sys.stderr)
        sys.exit(1)

    port = args.port
    if not constants.PORT_RANGE_START <= port <= constants.PORT_RANGE_END:
        print(f"Error: the port must be between {constants.PORT_RANGE_START}-{constants.PORT_RANGE_END}.", file=sys.stderr)
        sys.exit(1)
    if not network.is_port_free(private_ip, port):
        print(
            f"Error: Port {port} is already in use on {private_ip}. Choose another port.",
            file=sys.stderr,
        )
        sys.exit(1)

    streaming_directory = str(Path(args.dir).resolve())
    if not validation.is_valid_directory(streaming_directory):
        sys.exit(1)

    transcode = args.transcode

    is_remote_video = False
    address = ""
    if args.local_path:
        is_remote_video = False
        address = args.local_path
        if not validation.is_valid_local_video(address):
            sys.exit(1)
    elif args.remote_url:
        is_remote_video = True
        address = args.remote_url
        parsed = urlparse(address)
        is_valid_url = parsed.scheme in ["http", "https"] and parsed.netloc != ""
        if not is_valid_url:
            print("Error: the video remote url is not valid.", file=sys.stderr)
            sys.exit(1)

    return private_ip, port, streaming_directory, transcode, is_remote_video, address


def main():
    args = parse_args()

    private_ip, port, streaming_dir, transcode, is_remote_video, address = check_args(
        args,
    )
    print(f"- Private IP Server: {private_ip}")
    print(f"- Server port: {port}")
    print(f"- Directory server (streaming): {streaming_dir}")
    if is_remote_video:
        print(f"- Video source: Remote URL -> {address}")
    else:
        print(f"- Video source: Local file -> {address}")

    server = None
    server_thread = None
    ffmpeg_process = None

    try:
        server, server_thread = streaming.run_python_http_server_process(
            private_ip,
            port,
            streaming_dir,
        )
        if server is None and server_thread is None:
            sys.exit(1)

        ffmpeg_process = streaming.run_ffmpeg_process(
            private_ip,
            port,
            streaming_dir,
            transcode,
            address,
        )
        if ffmpeg_process is None:
            sys.exit(1)

        print("\n✅ FFmpeg HTTP Server successfully started!")
        print(
            f"Open this URL in a player like VLC: http://{private_ip}:{port}/stream.m3u8",
        )
        print(
            "Press Ctrl+C to stop the streaming and clean the stream files in the streaming directory.\n",
        )

        ffmpeg_process.wait()

        time.sleep(10)

    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Closing of current processes...")
        sys.exit(130)
    finally:
        if ffmpeg_process and ffmpeg_process.poll() is None:
            print("FFmpeg termination...")
            ffmpeg_process.terminate()
            ffmpeg_process.wait()
            print("FFmpeg process terminated.")
        else:
            print("FFmpeg process was no longer active.")

        if server and server_thread and server_thread.is_alive():
            print("Server HTTP termination...")
            server.shutdown()
            server_thread.join()
            print("HTTP Server process terminated.")
        else:
            print("HTTP Server was no longer active.")

        if not streaming.delete_stream_files(streaming_dir):
            print(
                f"Delete manually the stream files in the streaming directory:{streaming_dir}.",
            )


if __name__ == "__main__":
    main()
