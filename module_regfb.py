import requests
import json
import re
import time
import unicodedata
import os
from datetime import datetime
import random
import subprocess


class RegFb:
    def get_ipv4_from_ipconfig():
        output = subprocess.check_output("ipconfig", shell=True, text=True, encoding="utf-8", errors="ignore")
        match = re.search(r"IPv4 Address[^\d]*([\d]+\.[\d]+\.[\d]+\.[\d]+)", output)
        serverlocal = match.group(1) if match else None
        return serverlocal

    def openApp(bundleID: str):
        return f'at.appRun("{bundleID}")'

    