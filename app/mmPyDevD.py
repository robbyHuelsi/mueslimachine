import sys

class mmPyDevD():
    
    def __init__(self):
        sys.path.append(r'/home/pi/pysrc')
        import pydevd
        pydevd.settrace('192.168.178.121') # replace IP with address of Eclipse host machine
    