import objets_trouves.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('objets_trouves', '0002_reclamation_une_reclamation_acceptee_par_objet'),
    ]

    operations = [
        migrations.AddField(
            model_name='objettrouve',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to='objets/', validators=[objets_trouves.models.validate_image_upload]),
        ),
    ]
