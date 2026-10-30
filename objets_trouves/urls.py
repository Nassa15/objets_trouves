from django.urls import path
from . import views
app_name = "objets_trouves"
urlpatterns = [
    path("", views.objet_list, name="objet_list"),
    path("objet/<int:pk>/", views.objet_detail, name="objet_detail"),
    path("inscription/", views.inscription, name="inscription"),
    path("reclamation/<int:pk>/", views.reclamation_create, name="reclamation_create"),
    path("mes-reclamations/", views.mes_reclamations, name="mes_reclamations"),
    path("gestionnaire/", views.gestionnaire_dashboard, name="gestionnaire"),
    path("gestionnaire/objet/nouveau/", views.objet_create, name="objet_create"),
    path("gestionnaire/reclamation/<int:pk>/decision/", views.reclamation_decision, name="reclamation_decision"),
    path("gestionnaire/reclamation/<int:pk>/remise/", views.remise_create, name="remise_create"),
]
