from django.db import migrations, models
from core.models import PosModel

def get_serial_number(apps, schema_editor):
    for i in PosModel.objects.all():
        i.serial_number_length = i.company.serial_number_length
        i.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='posmodel',
            name='serial_number_length',
            field=models.IntegerField(null=True, blank=True)
        ),
        migrations.RunPython(get_serial_number),
        migrations.RemoveField(
        	'poscompany',
        	'serial_number_length'
        )
    ]
