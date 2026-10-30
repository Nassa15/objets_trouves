from functools import wraps
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import InscriptionForm, ObjetTrouveForm, ReclamationForm, style_form_widgets
from .models import Categorie, ObjetTrouve, Reclamation


def gestionnaire_requis(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.is_staff:
            return render(request, "objets_trouves/403.html", status=403)
        return view(request, *args, **kwargs)
    return wrapper


def objet_list(request):
    objets = ObjetTrouve.objects.select_related("categorie").all()
    query = request.GET.get("q", "").strip()
    categorie_id = request.GET.get("categorie", "")
    if query:
        objets = objets.filter(Q(titre__icontains=query) | Q(description__icontains=query) | Q(lieu__icontains=query))
    if categorie_id:
        objets = objets.filter(categorie_id=categorie_id)
    return render(request, "objets_trouves/objet_list.html", {"objets": objets, "categories": Categorie.objects.all(), "query": query, "categorie_id": categorie_id})


def objet_detail(request, pk):
    objet = get_object_or_404(ObjetTrouve.objects.select_related("categorie"), pk=pk)
    reclamation_existante = objet.reclamations.filter(reclamant=request.user).first() if request.user.is_authenticated else None
    return render(request, "objets_trouves/objet_detail.html", {"objet": objet, "reclamation_existante": reclamation_existante})


@login_required
def reclamation_create(request, pk):
    objet = get_object_or_404(ObjetTrouve, pk=pk)
    if objet.est_remis:
        messages.error(request, "Cet objet a déjà été remis.")
        return redirect("objets_trouves:objet_detail", pk=pk)
    if objet.reclamations.filter(reclamant=request.user).exists():
        messages.info(request, "Vous avez déjà déposé une réclamation pour cet objet.")
        return redirect("objets_trouves:mes_reclamations")
    form = ReclamationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        reclamation = form.save(commit=False)
        reclamation.objet, reclamation.reclamant = objet, request.user
        try:
            with transaction.atomic():
                reclamation.save()
        except IntegrityError:
            form.add_error(None, "Une réclamation existe déjà pour cet objet. Consultez votre espace personnel.")
        else:
            messages.success(request, "Votre réclamation a été enregistrée et sera examinée par un gestionnaire.")
            return redirect("objets_trouves:mes_reclamations")
    return render(request, "objets_trouves/reclamation_form.html", {"form": form, "objet": objet})


@login_required
def mes_reclamations(request):
    reclamations = Reclamation.objects.select_related("objet", "objet__categorie").filter(reclamant=request.user)
    return render(request, "objets_trouves/mes_reclamations.html", {"reclamations": reclamations})


@gestionnaire_requis
def gestionnaire_dashboard(request):
    reclamations = Reclamation.objects.select_related("objet", "reclamant").filter(statut=Reclamation.Statut.EN_ATTENTE)
    accepte = Reclamation.objects.select_related("objet", "reclamant").filter(statut=Reclamation.Statut.ACCEPTEE)
    objets = ObjetTrouve.objects.select_related("categorie").filter(remis_le__isnull=True)
    return render(request, "objets_trouves/gestionnaire_dashboard.html", {"reclamations": reclamations, "accepte": accepte, "objets": objets})


@gestionnaire_requis
def objet_create(request):
    form = ObjetTrouveForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        objet = form.save(commit=False)
        objet.publie_par = request.user
        objet.save()
        messages.success(request, "L'objet a été publié.")
        return redirect("objets_trouves:objet_detail", pk=objet.pk)
    return render(request, "objets_trouves/objet_form.html", {"form": form})


@gestionnaire_requis
def reclamation_decision(request, pk):
    if request.method != "POST":
        return redirect("objets_trouves:gestionnaire")
    with transaction.atomic():
        reclamation = get_object_or_404(Reclamation.objects.select_for_update(), pk=pk)
        objet = ObjetTrouve.objects.select_for_update().get(pk=reclamation.objet_id)
        decision, commentaire = request.POST.get("decision"), request.POST.get("commentaire", "").strip()
        if reclamation.statut != Reclamation.Statut.EN_ATTENTE:
            messages.info(request, "Cette réclamation a déjà été traitée.")
        elif decision == "accepter" and (objet.remis_le or Reclamation.objects.filter(objet=objet, statut=Reclamation.Statut.ACCEPTEE).exists()):
            messages.error(request, "Impossible d'accepter : l'objet est déjà attribué ou remis.")
        elif decision in {"accepter", "refuser"}:
            reclamation.statut = Reclamation.Statut.ACCEPTEE if decision == "accepter" else Reclamation.Statut.REFUSEE
            reclamation.commentaire_gestionnaire, reclamation.decidee_par, reclamation.decidee_le = commentaire, request.user, timezone.now()
            reclamation.save(update_fields=["statut", "commentaire_gestionnaire", "decidee_par", "decidee_le"])
            messages.success(request, "Réclamation acceptée. Vous pouvez enregistrer la remise." if decision == "accepter" else "Réclamation refusée.")
    return redirect("objets_trouves:gestionnaire")


@gestionnaire_requis
def remise_create(request, pk):
    if request.method != "POST":
        return redirect("objets_trouves:gestionnaire")
    with transaction.atomic():
        reclamation = get_object_or_404(Reclamation.objects.select_related("objet").select_for_update(), pk=pk)
        objet = ObjetTrouve.objects.select_for_update().get(pk=reclamation.objet_id)
        if reclamation.statut != Reclamation.Statut.ACCEPTEE or objet.remis_le:
            messages.error(request, "La remise nécessite une réclamation acceptée et un objet non remis.")
        else:
            now = timezone.now()
            objet.remis_le, objet.notes_remise = now, request.POST.get("notes_remise", "").strip()
            objet.save(update_fields=["remis_le", "notes_remise"])
            reclamation.statut, reclamation.remise_le = Reclamation.Statut.REMISE, now
            reclamation.save(update_fields=["statut", "remise_le"])
            Reclamation.objects.filter(objet=objet, statut=Reclamation.Statut.EN_ATTENTE).update(statut=Reclamation.Statut.REFUSEE, decidee_par=request.user, decidee_le=now, commentaire_gestionnaire="Objet remis à un autre réclamant.")
            messages.success(request, "La remise de l'objet a été enregistrée.")
    return redirect("objets_trouves:gestionnaire")


def inscription(request):
    if request.user.is_authenticated:
        return redirect("objets_trouves:objet_list")
    form = style_form_widgets(InscriptionForm(request.POST or None))
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        messages.success(request, "Votre compte a été créé.")
        return redirect("objets_trouves:objet_list")
    return render(request, "registration/inscription.html", {"form": form})
