from datetime import date
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from .models import Categorie, ObjetTrouve, Reclamation


class RegistreTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="etudiant", password="MotDePasse123!")
        self.manager = User.objects.create_user(username="gestionnaire", password="MotDePasse123!", is_staff=True)
        self.categorie = Categorie.objects.create(nom="Électronique")
        self.objet = ObjetTrouve.objects.create(titre="Téléphone noir", categorie=self.categorie, description="Coque bleue", lieu="Bibliothèque", date_decouverte=date.today())

    def test_visiteur_peut_rechercher_objet(self):
        response = self.client.get(reverse("objets_trouves:objet_list"), {"q": "Téléphone"})
        self.assertContains(response, "Téléphone noir")

    def test_utilisateur_depose_reclamation_et_la_suit(self):
        self.client.login(username="etudiant", password="MotDePasse123!")
        response = self.client.post(reverse("objets_trouves:reclamation_create", args=[self.objet.pk]), {"description_proprietaire": "Le code de déverrouillage est 2468."})
        self.assertRedirects(response, reverse("objets_trouves:mes_reclamations"))
        self.assertEqual(Reclamation.objects.get().statut, Reclamation.Statut.EN_ATTENTE)

    def test_gestionnaire_accepte_puis_enregistre_remise(self):
        reclamation = Reclamation.objects.create(objet=self.objet, reclamant=self.user, description_proprietaire="Preuve privée")
        self.client.login(username="gestionnaire", password="MotDePasse123!")
        self.client.post(reverse("objets_trouves:reclamation_decision", args=[reclamation.pk]), {"decision": "accepter"})
        reclamation.refresh_from_db()
        self.assertEqual(reclamation.statut, Reclamation.Statut.ACCEPTEE)
        self.client.post(reverse("objets_trouves:remise_create", args=[reclamation.pk]), {"notes_remise": "Remis au bureau d'accueil."})
        reclamation.refresh_from_db()
        self.objet.refresh_from_db()
        self.assertEqual(reclamation.statut, Reclamation.Statut.REMISE)
        self.assertIsNotNone(self.objet.remis_le)

    def test_objet_remis_refuse_nouvelle_reclamation(self):
        self.objet.remis_le = date.today()
        self.objet.save(update_fields=["remis_le"])
        self.client.login(username="etudiant", password="MotDePasse123!")
        response = self.client.post(reverse("objets_trouves:reclamation_create", args=[self.objet.pk]), {"description_proprietaire": "Preuve"})
        self.assertRedirects(response, reverse("objets_trouves:objet_detail", args=[self.objet.pk]))
        self.assertFalse(Reclamation.objects.exists())

    def test_un_objet_ne_peut_avoir_quune_reclamation_acceptee(self):
        premier = Reclamation.objects.create(objet=self.objet, reclamant=self.user, description_proprietaire="Preuve 1", statut=Reclamation.Statut.ACCEPTEE)
        autre_utilisateur = User.objects.create_user(username="etudiant2", password="MotDePasse123!")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Reclamation.objects.create(objet=self.objet, reclamant=autre_utilisateur, description_proprietaire="Preuve 2", statut=Reclamation.Statut.ACCEPTEE)
        self.assertEqual(Reclamation.objects.filter(objet=self.objet, statut=Reclamation.Statut.ACCEPTEE).count(), 1)
