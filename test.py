import logging
import sys

from flow import Flow
from datetime import date

import sys
import pickle
import re

logging.basicConfig(level=logging.INFO)

with Flow() as flow:
    if True or flow.login('email', 'password'):
        start = date(2015, 4, 1)
        # end = date(2015, 5, 1)
        end = date.today()
        
        test = date(2015, 4, 2)

        # print(start <= test <= end)
        # flow.getEventsInRange(start, end)
        # flow.parseCalenderEvents()
        flow.processTraining()

sys.exit()

# class Jobs:
    # def download(self, id):
        # print(id)
        # print(x)

# for job in jobs[:]:    
    # getattr(Jobs, 'download')(None, *job[1])
