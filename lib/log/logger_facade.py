from console_logger import ConsoleLogger
from file_logger import FileLogger
import shutil

class LoggerFacade:

    def __init__(self, results_path, console=False, file=False, telegram=False):
        self.results_path = results_path
        self.console = console
        self.file = file
        self.telegram = telegram

    def log_line(self, message, console=None, file=None, telegram=None):
        if console or (console == None and self.console):
            ConsoleLogger().log_line(message)
        if file or (file == None and self.file):
            FileLogger().log_line(self.results_path, message)
