import sys


class MMLogger:
    @staticmethod
    def log_warn(msg, flush=False):
        print("[WARN]  " + msg, file=sys.stderr, flush=flush)

    @staticmethod
    def log_error(msg, flush=False):
        print("[ERROR] " + msg, file=sys.stderr, flush=flush)

    @staticmethod
    def log(msg, flush=False):
        print("        " + msg, file=sys.stderr, flush=flush)
