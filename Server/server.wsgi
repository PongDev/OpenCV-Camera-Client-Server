#! /usr/bin/python3

import sys

sys.path.append('/home/VideoServer')

from server import init_app

application=init_app()
