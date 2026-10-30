from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('objets_trouves', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='reclamation',
            constraint=models.UniqueConstraint(condition=models.Q(('statut', 'acceptee')), fields=('objet',), name='une_reclamation_acceptee_par_objet'),
        ),
    ]
