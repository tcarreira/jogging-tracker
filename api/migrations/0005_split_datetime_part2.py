from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0005_split_datetime_part1"),
    ]

    operations = [
        migrations.AlterField(
            model_name="activity", name="date", field=models.DateField(),
        ),
    ]
