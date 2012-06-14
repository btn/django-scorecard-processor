from django.utils import simplejson
from ierg_results.management.commands.ierg_command import IergCommand


class Command(IergCommand):
    #TODO: We can get this from option or database later
    SHEET_NAME = '2.2 Coverage indicators'
    SURVEY_NAME = 'Coverage indicators'
    IDENTIFIER = '2.2.3'
    QUESTION = 'Antiretroviral prophylaxis for PMTCT'
    COLUM_NAME_ROW_STRING = "A4:AI4"
    RATING_COLUMN = 11
    VALUE_COLUMNS = xrange(12, 15)
    START_LINE = 4
    FINISH_LINE = 79


    def get_json(self, sheet, column_names, i):
        value = {}
        value[column_names[self.RATING_COLUMN]] = sheet.cell(row=i, column=self.RATING_COLUMN).value
        for j in self.VALUE_COLUMNS:
            value[column_names[j]] = sheet.cell(row=i, column=j).value
        return simplejson.dumps(value)

