from django.contrib import admin
from .models import Categorie, ObjetTrouve, Reclamation

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    search_fields = ("nom",)

@admin.register(ObjetTrouve)
class ObjetTrouveAdmin(admin.ModelAdmin):
    list_display = ("titre", "categorie", "lieu", "date_decouverte", "remis_le")
    list_filter = ("categorie", "remis_le")
    search_fields = ("titre", "description", "lieu")

@admin.register(Reclamation)
class ReclamationAdmin(admin.ModelAdmin):
    list_display = ("objet", "reclamant", "statut", "creee_le", "decidee_le")
    list_filter = ("statut",)
    search_fields = ("objet__titre", "reclamant__username")
    readonly_fields = ("creee_le", "decidee_le", "remise_le")
