import datetime
import odin.datetimeutil

ARE_YOU_EXPERIENCED = datetime.date(1967, 5, 12)
MWT = odin.datetimeutil.FixedTimezone(-6, 'Mountain War Time')
BOOM = datetime.datetime(1945, 7, 16, 5, 29, 45, 0, MWT)
