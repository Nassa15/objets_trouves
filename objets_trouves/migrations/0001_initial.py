import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categorie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=80, unique=True)),
            ],
            options={
                'verbose_name': 'catégorie',
                'verbose_name_plural': 'catégories',
                'ordering': ['nom'],
            },
        ),
        migrations.CreateModel(
            name='ObjetTrouve',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=150)),
                ('description', models.TextField(help_text="Description générale, sans détail permettant l'identification privée.")),
                ('lieu', models.CharField(max_length=150)),
                ('date_decouverte', models.DateField()),
                ('publie_le', models.DateTimeField(auto_now_add=True)),
                ('remis_le', models.DateTimeField(blank=True, null=True)),
                ('notes_remise', models.TextField(blank=True)),
                ('categorie', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='objets', to='objets_trouves.categorie')),
                ('publie_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='objets_publies', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'objet trouvé',
                'verbose_name_plural': 'objets trouvés',
                'ordering': ['-date_decouverte', '-publie_le'],
            },
        ),
        migrations.CreateModel(
            name='Reclamation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description_proprietaire', models.TextField(help_text='Détails privés prouvant que vous êtes le propriétaire (non visibles par le public).')),
                ('statut', models.CharField(choices=[('en_attente', 'En attente'), ('acceptee', 'Acceptée'), ('refusee', 'Refusée'), ('remise', 'Remise')], default='en_attente', max_length=20)),
                ('commentaire_gestionnaire', models.TextField(blank=True)),
                ('creee_le', models.DateTimeField(auto_now_add=True)),
                ('decidee_le', models.DateTimeField(blank=True, null=True)),
                ('remise_le', models.DateTimeField(blank=True, null=True)),
                ('decidee_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='decisions_reclamations', to=settings.AUTH_USER_MODEL)),
                ('objet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reclamations', to='objets_trouves.objettrouve')),
                ('reclamant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reclamations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'réclamation',
                'verbose_name_plural': 'réclamations',
                'ordering': ['-creee_le'],
                'constraints': [models.UniqueConstraint(fields=('objet', 'reclamant'), name='une_reclamation_par_utilisateur_et_objet')],
            },
        ),
    ]
