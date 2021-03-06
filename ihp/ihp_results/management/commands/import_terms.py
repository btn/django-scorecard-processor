from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import xlrd
from scorecard_processor import models

lookup = {
}

class Command(BaseCommand):
    args = '<filename.xls>'
    help = 'Imports glossary terms into the system'
    output_transaction = True
    option_list = BaseCommand.option_list + (
        make_option('--lang',
            dest='lang',
            help='Language of the survey'),
        )


    def handle(self, *args, **options):
        survey_file = xlrd.open_workbook(args[0])
        lang = options.get('lang','en-gb')
        if not lang:
            lang = 'en-gb'
        
        project=models.Project.objects.get()

        skip = True
        order = 0
        sheet = survey_file.sheet_by_name('Sheet1')
        for row_num in xrange(1,sheet.nrows):
            row = sheet.row(row_num)
            definition = row[0].value
            if definition:
                definition,created = project.glossarydefinition_set.get_or_create(definition=definition, lang=lang)
                col = 1
                while 1:
                    if row[col].value!='':
                        print(len(row[col].value),row[col].value)
                        t,created =definition.glossaryterm_set.get_or_create(term=row[col].value) 
                    else:
                        break
                    col += 1

