# Campus — Objets retrouvés

Application Django de publication et de réclamation des objets trouvés sur un campus. Un visiteur peut rechercher un objet ; un utilisateur inscrit peut déposer une preuve privée ; un gestionnaire examine, décide et trace la remise.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata demo_data
python manage.py runserver
```

Le projet utilise SQLite en développement. Les fichiers `env/`, `db.sqlite3`, `media/`, `__pycache__/` et `node_modules/` ne font pas partie du livrable, à l'exception des deux visuels SVG fournis dans `media/objets/` pour la démonstration. Les gestionnaires peuvent joindre une photo JPG, PNG, WebP ou SVG de 5 Mo maximum lors de la publication. Pour les styles Tailwind, installer Node puis exécuter `cd theme/static_src && npm install && npm run build`.

## Comptes et rôles

Créer un gestionnaire avec `python manage.py createsuperuser` puis utiliser le compte dans `/admin/`. Tout compte avec `is_staff=True` accède à `/gestionnaire/` pour publier, examiner les réclamations et enregistrer les remises. Les autres utilisateurs créent leur compte depuis `/inscription/`.

## Tests

```bash
python manage.py test
```

Les tests couvrent la recherche publique, la création et le suivi d'une réclamation, la décision du gestionnaire et l'interdiction de réclamer un objet remis.

## Règles métier

Une seule réclamation par utilisateur et par objet est autorisée. Une seule réclamation peut être acceptée ; l'enregistrement de la remise passe l'objet et la réclamation à l'état `remise` et refuse automatiquement les demandes encore en attente. Les détails d'identification sont stockés dans la réclamation et ne sont jamais affichés dans le registre public.
