from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import xlrd
from scorecard_processor import models

lookup = {
}

class Command(BaseCommand):
    args = '<filename.xls>'
    help = 'Imports a 2012 legacy survey into the system'
    option_list = BaseCommand.option_list + (
        make_option('--name',
            dest='name',
            help='Give the survey a name'),
        make_option('--verbose',
            dest='verbose',
            default=False,
            action='store_true',
            help='verbose_output'),
        )
    output_transaction = True

    def handle(self, *args, **options):
        survey_file = xlrd.open_workbook(args[0])
        name = options['name']
        verbose = options['verbose']
        if not name:
            raise CommandError("Require a name for the survey")
        
        group = None
        survey, created = models.Survey.objects.get_or_create(name=name, project=models.Project.objects.get())
        survey.question_set.all().delete()
        survey.questiongroup_set.all().delete()

        skip = True
        sup = None
        order = 0
        sheet = survey_file.sheet_by_name('Survey Tool')
        comment_text = sheet.row(6)[6].value
        section = None
        description = ''
        tick_mode = False
        for row_num in xrange(7,sheet.nrows):
            row = sheet.row(row_num)
            if row[2].ctype!=0 and int(row[2].value)==16:
                row[0].value = 'Additional questions'
                row[0].ctype = 1

            if row[0].ctype != 0: #Empty
                if section!=None and int(q_num) <= 12:
                    question = section.question_set.create(survey=survey, identifier=group_name, question="Voluntary additional information", help_text="Please use this space to provide any additional information", widget='textbox')
                section_name = group_name = row[0].value
                if group_name in lookup:
                    section_name = '%s: %s' % (group_name, lookup.get(group_name,group_name))
                section = survey.questiongroup_set.create(name= section_name, help_text=row[1].value)

                if verbose:
                    print("\n")
                    print(section.name)
                    print(' '+section.help_text)


            try:
                q_num = str(int(row[2].value))
                q = row[3].value
            except:
                pass

            q_type = {
                    '1':'yes_no_choice',
                    '2':'yes_no_choice',
                    '3':'yes_no_choice',
                    '4':'yes_no_choice',
                    '9':'rating_0_5_half',
                    '10':'rating_0_5_half',
                    '11':'yes_no_choice',
                    '12':'yes_no_choice',
                    '13':'integer',
                    '14':'rep_types',
                    '15':'cso_involved',
                    '16':'integer',
                    '17':'integer',
                    '18':'integer',
                    '19':'integer',
                    '20':'integer',
                    '22':'yes_no_choice',
                    '23':'integer',
                    '24':'integer',
                    '25':'date',
                    '26':'textbox',
                    '27':'textbox',
                }.get(q_num,'multi_currency')

            if q_num in ['14','15']:
                if tick_mode == False:
                    tick_mode = True
            else:
                tick_mode = False

            
            if tick_mode and q != row[3].value:
                continue
            else:
                question = section.question_set.create(survey=survey, identifier=q_num, question=q, widget=q_type)
                if int(q_num) > 12 and q_num not in ['26','27']:
                    add_question = section.question_set.create(survey=survey, identifier="%s+" % q_num, question="Voluntary additional information", help_text="Please use this space to provide any additional information", widget='textbox')
                if verbose:
                    print('   '+str(question))
