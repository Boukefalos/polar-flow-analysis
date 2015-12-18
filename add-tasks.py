from tasks import *
# add.delay(4, 4)

from datetime import date
start = date(2015, 4, 1)
end = date(2015, 5, 1) #date.today()
# findIt.delay(start, end)
findIt.direct(start, end)