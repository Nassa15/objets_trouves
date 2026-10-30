from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import ObjetTrouve, Reclamation


class InscriptionForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse e-mail")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Django's validator guidance is useful internally but too technical for
        # this short registration form; validation errors remain visible on submit.
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""
        self.fields["password1"].label = "Mot de passe"
        self.fields["password2"].label = "Confirmer le mot de passe"

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {"username": "Nom d'utilisateur"}


class ObjetTrouveForm(forms.ModelForm):
    class Meta:
        model = ObjetTrouve
        fields = ("titre", "categorie", "description", "lieu", "date_decouverte", "image")
        labels = {"titre": "Titre de l'objet", "categorie": "Catégorie", "description": "Description générale", "lieu": "Lieu de découverte", "date_decouverte": "Date de découverte", "image": "Photo de l'objet (facultative)"}
        widgets = {"date_decouverte": forms.DateInput(attrs={"type": "date"}), "image": forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png,image/webp,image/svg+xml"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "field-control"

    def clean_date_decouverte(self):
        date = self.cleaned_data["date_decouverte"]
        if date > timezone.localdate():
            raise forms.ValidationError("La date ne peut pas être dans le futur.")
        return date


class ReclamationForm(forms.ModelForm):
    class Meta:
        model = Reclamation
        fields = ("description_proprietaire",)
        labels = {"description_proprietaire": "Éléments permettant d'identifier votre propriété"}
        widgets = {"description_proprietaire": forms.Textarea(attrs={"rows": 6})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "field-control"


def style_form_widgets(form):
    """Apply the shared Tailwind control class to authentication forms."""
    for field in form.fields.values():
        field.widget.attrs["class"] = "field-control"
    return form
