import sys
from pathlib import Path

from .constants import VIDEO_EXTENSIONS


def is_valid_directory(absolute_path_dir):
    if not Path(absolute_path_dir).is_absolute():
        print("Error: the streaming directory path isn't absolute.", file=sys.stderr)
        return False
    if Path(absolute_path_dir).exists():
        if Path(absolute_path_dir).is_dir():
            return True
        print(
            "Error: the streaming directory path doesn't refer to a directory.",
            file=sys.stderr,
        )
        return False
    try:
        Path(absolute_path_dir).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(
            f"Error: the streaming directory can't be created: {e}.",
            file=sys.stderr,
        )
        return False
    else:
        print(f"📁 Streaming directory created: {absolute_path_dir}.")
        return True


def is_valid_local_video(absolute_path_video):
    if not Path(absolute_path_video).is_absolute():
        print("Error: the local video path isn't absolute.", file=sys.stderr)
        return False

    if not Path(absolute_path_video).is_file():
        print("Error: the local video path doesn't refer to a video.", file=sys.stderr)
        return False

    ext = Path(absolute_path_video).suffix
    if ext.lower() in VIDEO_EXTENSIONS:
        return True
    print(
        "Error: the local video path refers to a file that isn't a video.",
        file=sys.stderr,
    )
    return False
