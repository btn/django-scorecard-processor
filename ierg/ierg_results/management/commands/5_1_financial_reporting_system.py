from datetime import datetime
from django.utils import simplejson
from ierg_results.management.commands.ierg_command import IergCommand


class Command(IergCommand):
    #TODO: We can get this from option or database later
    SHEET_NAME = '5.1 Financial reporting system'
    COLUM_NAME_ROW_STRING = "A4:K4"
    START_LINE = 4
    FINISH_LINE = 79


    def get_json(self, sheet, column_names, i):
        value = {}
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime) else None
        for j in column_names:
            value[column_names[j]] = sheet.cell(row=i, column=j).value
        return simplejson.dumps(value, default=dthandler)

