import json
import logging

import coloredlogs  # type: ignore[import-untyped]
import requests
from packaging import version

log_level = None
debug_logfile_handler = None
debug_log_filter = None


def get_logger(name=__name__, verbosity=None, debug_file=None, debug_filter=None) -> logging.Logger:
    """
    Colored logging

    :param name: logger name (use __name__ variable)
    :param verbosity:
    :return: Logger
    """
    global log_level
    if verbosity is not None:
        if log_level is None:
            log_level = verbosity
        else:
            raise RuntimeError("Verbosity has already been set.")

    global debug_logfile_handler
    if debug_file is not None:
        print(f"Setting up debug logfile {debug_file}")
        if debug_logfile_handler is None:
            debug_logfile_handler = logging.FileHandler(debug_file)
            debug_logfile_handler.setLevel(logging.DEBUG)
            debug_logfile_handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )
        else:
            raise RuntimeError("Debug logfile handler has already been initialized.")

    global debug_log_filter
    if debug_filter is not None:
        if debug_log_filter is None:
            debug_log_filter = debug_filter.split(",")
        else:
            raise RuntimeError("Debug log filter has already been set.")

    shortname = name.replace("pytr.", "")
    logger = logging.getLogger(shortname)
    logger.setLevel(logging.DEBUG)

    if debug_logfile_handler is not None and (debug_log_filter is None or shortname in debug_log_filter):
        if debug_logfile_handler not in logger.handlers:
            logger.addHandler(debug_logfile_handler)

    # no logging of libs
    logger.propagate = False

    if log_level == "debug":
        fmt = "%(asctime)s %(name)-9s %(levelname)-8s %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S%z"
    else:
        fmt = "%(asctime)s %(message)s"
        datefmt = "%H:%M:%S"

    fs = {
        "asctime": {"color": "green"},
        "hostname": {"color": "magenta"},
        "levelname": {"color": "red", "bold": True},
        "name": {"color": "magenta"},
        "programname": {"color": "cyan"},
        "username": {"color": "yellow"},
    }

    ls = {
        "critical": {"color": "red", "bold": True},
        "debug": {"color": "green"},
        "error": {"color": "red"},
        "info": {},
        "notice": {"color": "magenta"},
        "spam": {"color": "green", "faint": True},
        "success": {"color": "green", "bold": True},
        "verbose": {"color": "blue"},
        "warning": {"color": "yellow"},
    }

    coloredlogs.install(
        level=log_level,
        logger=logger,
        fmt=fmt,
        datefmt=datefmt,
        level_styles=ls,
        field_styles=fs,
    )

    return logger


def preview(response, num_lines=5):
    lines = json.dumps(response, indent=2).splitlines()
    head = "\n".join(lines[:num_lines])
    tail = len(lines) - num_lines

    if tail <= 0:
        return f"{head}\n"
    else:
        return f"{head}\n{tail} more lines hidden"


def check_version(installed_version):
    log = get_logger(__name__)
    try:
        r = requests.get("https://api.github.com/repos/pytr-org/pytr/tags", timeout=1)
    except Exception as e:
        log.error("Could not check for a newer version")
        log.debug(str(e))
        return
    latest_version = r.json()[0]["name"]

    if version.parse(installed_version) < version.parse(latest_version):
        log.warning(f"Installed pytr version ({installed_version}) is outdated. Latest version is {latest_version}")
    else:
        log.info("pytr is up to date")
