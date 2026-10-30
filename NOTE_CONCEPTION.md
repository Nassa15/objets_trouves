# Note de conception — Objets retrouvés

## Objectif et rôles

Le registre centralise les objets retrouvés sur le campus. Le visiteur consulte les annonces sans compte. L'utilisateur inscrit dépose une réclamation et suit son état. Le gestionnaire (compte Django `is_staff`) publie les objets, vérifie les éléments privés, décide et documente la remise.

## Modèle de données

`Categorie` classe les objets. `ObjetTrouve` contient le titre, la description générale, la catégorie, le lieu et la date de découverte ; `publie_par` trace le gestionnaire et `remis_le` matérialise la remise. `Reclamation` relie un objet à son `reclamant` Django et conserve la description sensible, le statut, le décideur, le commentaire et les dates de décision/remise.

## Règles principales

Les états sont `en_attente`, `acceptee`, `refusee` et `remise`. Une contrainte d'unicité empêche un utilisateur de soumettre deux fois le même objet. Les décisions sont protégées par transaction et verrouillage SQL : deux gestionnaires ne peuvent pas accepter simultanément des réclamations concurrentes. Une remise n'est possible qu'après acceptation ; elle refuse les autres demandes en attente et bloque toute nouvelle réclamation.

## Organisation

L'application `objets_trouves` regroupe les modèles, vues, routes et templates du registre des objets trouvés. Les templates séparent le registre public, l'espace utilisateur et le tableau de gestion. Les migrations versionnent le schéma et les tests Django vérifient les parcours critiques.
