#!/bin/bash
echo -e "from scorecard_processor import models;models.ResponseSet.objects.all().delete();exit()" | ./manage.py shell --settings=local_settings 
./manage.py dumpdata scorecard_processor --settings=local_settings --indent=2 > ihp_results/example_data.json
