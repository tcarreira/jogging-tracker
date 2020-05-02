
import datetime

from django.db import migrations, models
from django.db.models import DateField, F, TimeField
from django.db.models.functions import Cast
from django.utils.timezone import utc


def datetime_to_date_and_time(apps, schema_editor):
    Activity = apps.get_model("api", "Activity")
    db_alias = schema_editor.connection.alias
    Activity.objects.using(db_alias).update(
        time=Cast("date", output_field=TimeField()),
    )


def date_and_time_to_datetime(apps, schema_editor):
    Activity = apps.get_model("api", "Activity")
    db_alias = schema_editor.connection.alias
    Activity.objects.using(db_alias).update(date=F("date") + F("time"))


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0004_auto_20200501_2158"),
    ]

    operations = [
        migrations.AddField(
            model_name="activity",
            name="time",
            field=models.TimeField(
                default=datetime.datetime(2020, 5, 2, 12, 28, 34, 567891, tzinfo=utc)
            ),
            preserve_default=False,
        ),
        migrations.RunPython(datetime_to_date_and_time, date_and_time_to_datetime),
    ]
