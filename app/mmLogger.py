import sys

class mmLogger():
	def logWarn(self, msg, flush=False):
		print("[WARN]  " + msg, file=sys.stderr, flush=flush)

	def logErr(self, msg, flush=False):
		print("[ERROR] " + msg, file=sys.stderr, flush=flush)

	def log(self, msg, flush=False):
		print("        " + msg, file=sys.stderr, flush=flush)