# Rapport de Projet : Profiling et Optimisation de Code d'Algorithme de Trading

## Introduction

Dans le cadre de ce projet, nous avons travaillé sur l'analyse et l'optimisation d'un algorithme de trading utilisé par ENGIE, l'un des leaders mondiaux dans la production et la distribution d'énergie. L'objectif principal était de profiler le code existant pour identifier les goulets d'étranglement en termes de performance et proposer des améliorations pour réduire les temps d'exécution.

## Description du Projet

### Contexte
L'algorithme en question est utilisé dans le cadre de la gestion des transactions sur un *Limit Order Book* (LOB), une structure de données qui répertorie les offres d'achat (bids) et de vente (asks) pour une ressource donnée. Le projet s'est focalisé sur deux types de fichiers : les fichiers de transactions (*trades*) et les fichiers de citations (*quotes*), stockés en format Parquet pour leur efficacité avec des volumes de données importants.

### Objectifs
1. **Profiling du code** : Identifier les fonctions les plus consommatrices de temps pour les optimiser.
2. **Optimisation du code** : Réduire les temps d'exécution en utilisant diverses techniques comme la fusion de fichiers et l'amélioration des performances de certaines fonctions critiques.

## Démarche et Expériences

### 1. Profiling Initial
Nous avons utilisé l'outil Snakeviz pour profiler le code existant. Cela nous a permis de visualiser les fonctions qui nécessitaient le plus de temps de calcul. Une première analyse a montré que la fonction `ymdssm2datetime` était particulièrement chronophage, avec un temps d'exécution de 3,49 secondes.


### 2. Optimisation du Code
Après l'analyse, nous avons apporté des modifications au code pour améliorer les performances. Par exemple, l'optimisation de la fonction `ymdssm2datetime` a permis de réduire le temps d'exécution à 0,395 secondes, soit une division du temps par un facteur de 8,83.


### 3. Fusion des Fichiers Parquet
Nous avons également testé différentes méthodes pour traiter les fichiers Parquet. La solution retenue a été de fusionner tous les fichiers en une seule opération, ce qui a permis de gagner du temps d'exécution.

#### Expérience avec Fusion des Fichiers
Bien que la méthode se soit révélée efficace sur des petits jeux de données, des problèmes d'échelle sont apparus lors de tests avec des volumes plus importants.

## Résultats et Conclusion

Les optimisations apportées ont permis de réduire significativement les temps d'exécution des fonctions critiques. Néanmoins, certaines solutions, notamment la fusion des fichiers Parquet, nécessitent encore des tests supplémentaires pour garantir leur efficacité à grande échelle. Des pistes d'amélioration supplémentaires incluent l'utilisation de langages plus performants comme C++ ou des optimisations avec Numba.
