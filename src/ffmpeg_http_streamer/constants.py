import errno

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".flv",
    ".wmv",
    ".webm",
    ".mpeg",
    ".mpg",
    ".3gp",
    ".m4v",
    ".divx",
}


PORT_RANGE_START = 49152
PORT_RANGE_END = 65535


PROCESS_STARTUP_TIMEOUT_S = 20


EADDRINUSE = errno.EADDRINUSE
