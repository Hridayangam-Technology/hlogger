import os
import traceback
from typing import Callable

import logfire
import structlog

from src.hlogger.constants import LOGGER_COLORS


class Logger:
    show_source_location: bool = True

    def __init__(self) -> None:
        self.environment = os.getenv("ENV", "dev")
        self.log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()

        if self.environment == "prod":
            self.logger = logfire
            self.allowed_levels = ["ERROR", "CRITICAL"]
            self.critical_log_method = self.logger.fatal
        else:
            self.logger = structlog.getLogger(__name__)
            self.allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            self.critical_log_method = self.logger.critical

    def _log(
        self, log_method: Callable, message: str, exc_info: bool, level: str
    ) -> None:
        if level not in self.allowed_levels:
            return None
        loc: str = ""
        fn: str = ""
        tb: list[traceback.FrameSummary] = traceback.extract_stack()
        if len(tb) > 2 and self.show_source_location:
            loc = f"({os.path.basename(tb[-3][0])}:{tb[-3][1]}):"
            fn = tb[-3][2]
            if fn != "<module>":
                fn += "()"
        color: str = LOGGER_COLORS.get(level, LOGGER_COLORS["RESET"])
        reset: str = LOGGER_COLORS["RESET"]
        colored_message: str = f"{color}{loc + fn}: {message}{reset}"
        log_method(colored_message, exc_info=exc_info)

    def info(self, message: str, exc_info: bool = False) -> None:
        self._log(self.logger.info, message, exc_info, "INFO")

    def debug(self, message: str, exc_info: bool = False) -> None:
        self._log(self.logger.debug, message, exc_info, "DEBUG")

    def warning(self, message: str, exc_info: bool = True) -> None:
        self._log(self.logger.warn, message, exc_info, "WARNING")

    def error(self, message: str, exc_info: bool = True) -> None:
        self._log(self.logger.error, message, exc_info, "ERROR")

    def critical(self, message: str, exc_info: bool = True) -> None:
        self._log(self.critical_log_method, message, exc_info, "CRITICAL")


logger = Logger()
