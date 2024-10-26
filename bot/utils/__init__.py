from .logger import logger
from . import launcher


import os

if not os.path.exists("sessions"):
    os.mkdir(path="sessions")
