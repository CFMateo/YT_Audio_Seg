# 🎧 AudioSet Data Pipeline: Scraping, Processing & Visualization

Ce projet implémente un pipeline complet d'ingénierie de données pour construire un ensemble de données audio structuré à partir de sources web brutes. L'objectif est de transformer un index de métadonnées (identifiants YouTube et timestamps) en un dataset nettoyé, segmenté et prêt pour des tâches de Machine Learning.



## Objectifs du Projet

Le projet automatise la création d'un dataset audio à partir du jeu de données [AudioSet](https://research.google.com/audioset//download.html) de Google Research. Il traite les défis suivants :
* **Data Scraping** : Récupération automatisée de flux audio via des sources en ligne.
* **Metadata Engineering** : Nettoyage de données brutes via expressions régulières (Regex) et enrichissement sémantique des étiquettes (IDs vers noms de classes).
* **Traitement de Signal** : Segmentation temporelle précise pour isoler les événements sonores pertinents.
* **Exploration visuelle** : Analyse des spectrogrammes et des distributions de fréquences.

##  Architecture du Pipeline

### 1. Extraction et Nettoyage de Métadonnées
La première phase consiste à rendre les fichiers `.csv` bruts exploitables :
- Conversion des identifiants alphanumériques en étiquettes humaines (ex: `/m/04rlf` devient `Ratchet`).
- Analyse de la distribution des classes pour évaluer l'équilibre du dataset.
- Utilisation de **Regex** complexes pour valider l'intégrité des données d'entrée.

### 2. Pipeline de Traitement Audio
Mise en œuvre d'un moteur robuste pour l'acquisition de données multimédias :
- **Téléchargement sélectif** : Extraction uniquement de la piste audio pour optimiser la bande passante.
- **Segmentation temporelle** : Découpage chirurgical des fichiers `.wav` ou `.mp3` selon les intervalles temporels fournis.
- **Normalisation** : Formatage des segments pour garantir une cohérence de fréquence d'échantillonnage (Sampling Rate).

### 3. Analyse et Visualisation de Signal
Utilisation de `Librosa` et `Matplotlib` pour valider la qualité des données produites :
- Génération de **spectrogrammes** pour visualiser l'intensité fréquentielle.
- Étude des formes d'onde (waveforms) pour identifier les motifs sonores.



##  Structure du Dépôt

```text
.
├── src/
│   ├── metadata_processing.py  # Fonctions de nettoyage (Regex, mapping)
│   ├── audio_acquisition.py    # Téléchargement et découpage audio
│   └── data_pipeline.py        # Orchestration du flux de données
├── notebooks/
│   └── analysis.ipynb          # Visualisation interactive et spectrogrammes
├── data/                       # Dataset généré (segments audio)
└── requirements.txt            # Dépendances (Regex, Librosa, Youtube-dl, etc.)
