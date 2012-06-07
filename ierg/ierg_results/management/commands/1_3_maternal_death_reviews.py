from django.utils import simplejson
from ierg_results.management.commands.ierg_command import IergCommand


class Command(IergCommand):
    #TODO: We can get this from option or database later
    SHEET_NAME = '1.3MaternalDeathReviews'
    COLUM_NAME_ROW_STRING = "A5:V5"
    START_LINE = 5

    REGION_SC = 1
    QUESTIONS_SC = [
        range(2, 3),
        range(3, 4),
        range(4, 7),
        range(7, 10),
        range(10, 13),
        range(13, 16),
        range(16, 19),
        range(19, 22),
    ]


    def get_json(self, sheet, column_names, i):
        value = {}

        value[column_names[self.REGION_SC]] = sheet.cell(row=i,
            column=self.REGION_SC).value

        value['data'] = []
        for questions_sc in self.QUESTIONS_SC:
            questions = {}
            for j in questions_sc:
                questions[column_names[j]] = sheet.cell(row=i, column=j).value
            value['data'].append(questions)

        return simplejson.dumps(value)

