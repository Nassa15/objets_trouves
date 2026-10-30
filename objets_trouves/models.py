from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


def validate_image_upload(upload):
    """Keep uploads lightweight and limited to browser-displayable images."""
    allowed = {".jpg", ".jpeg", ".png", ".webp", ".svg"}
    suffix = "." + upload.name.rsplit(".", 1)[-1].lower() if "." in upload.name else ""
    if suffix not in allowed:
        raise ValidationError("Ajoutez une image JPG, PNG, WebP ou SVG.")
    content_type = getattr(upload, "content_type", "")
    if content_type and content_type not in {"image/jpeg", "image/png", "image/webp", "image/svg+xml"}:
        raise ValidationError("Le fichier envoyé n'est pas une image compatible.")
    if upload.size > 5 * 1024 * 1024:
        raise ValidationError("L'image doit peser 5 Mo ou moins.")


class Categorie(models.Model):
    nom = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ["nom"]
        verbose_name = "catégorie"
        verbose_name_plural = "catégories"

    def __str__(self):
        return self.nom


class ObjetTrouve(models.Model):
    titre = models.CharField(max_length=150)
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name="objets")
    description = models.TextField(help_text="Description générale, sans détail permettant l'identification privée.")
    lieu = models.CharField(max_length=150)
    date_decouverte = models.DateField()
    image = models.FileField(upload_to="objets/", blank=True, null=True, validators=[validate_image_upload])
    publie_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="objets_publies")
    publie_le = models.DateTimeField(auto_now_add=True)
    remis_le = models.DateTimeField(null=True, blank=True)
    notes_remise = models.TextField(blank=True)

    class Meta:
        ordering = ["-date_decouverte", "-publie_le"]
        verbose_name = "objet trouvé"
        verbose_name_plural = "objets trouvés"

    @property
    def est_remis(self):
        return self.remis_le is not None

    def __str__(self):
        return self.titre


class Reclamation(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente"
        ACCEPTEE = "acceptee", "Acceptée"
        REFUSEE = "refusee", "Refusée"
        REMISE = "remise", "Remise"

    objet = models.ForeignKey(ObjetTrouve, on_delete=models.CASCADE, related_name="reclamations")
    reclamant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reclamations")
    description_proprietaire = models.TextField(help_text="Détails privés prouvant que vous êtes le propriétaire (non visibles par le public).")
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    commentaire_gestionnaire = models.TextField(blank=True)
    creee_le = models.DateTimeField(auto_now_add=True)
    decidee_le = models.DateTimeField(null=True, blank=True)
    decidee_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="decisions_reclamations")
    remise_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-creee_le"]
        constraints = [
            models.UniqueConstraint(
                fields=["objet", "reclamant"],
                name="une_reclamation_par_utilisateur_et_objet",
            ),
            models.UniqueConstraint(
                fields=["objet"],
                condition=Q(statut="acceptee"),
                name="une_reclamation_acceptee_par_objet",
            ),
        ]
        verbose_name = "réclamation"
        verbose_name_plural = "réclamations"

    def clean(self):
        if self.objet_id and self.objet.est_remis and self.statut in {self.Statut.EN_ATTENTE, self.Statut.ACCEPTEE}:
            raise ValidationError("Cet objet a déjà été remis : aucune nouvelle réclamation n'est possible.")
        if self.statut == self.Statut.ACCEPTEE and self.objet_id:
            if self.objet.reclamations.filter(statut=self.Statut.ACCEPTEE).exclude(pk=self.pk).exists():
                raise ValidationError("Une seule réclamation peut être acceptée pour un objet.")

    def __str__(self):
        return f"Réclamation de {self.reclamant} pour {self.objet}"
