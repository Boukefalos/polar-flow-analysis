import logging
import sys

from flow import Flow
from datetime import date

import sys
import pickle
import re

logging.basicConfig(level=logging.INFO)

with Flow(restart=True) as flow:
    if flow.login('email', 'password'):
        start = date(2015, 4, 1)
        end = date.today()
        flow.getEventsInRange(start, end)
        flow.parseCalenderEvents()

sys.exit()
