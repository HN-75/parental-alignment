# Parental Alignment - Moral Dilemma Simulator

Ce projet est une simulation interactive conçue pour explorer et démontrer le concept d'**Alignement Parental** pour les intelligences artificielles (IA). Il modélise un dilemme moral où une superintelligence doit gérer des ressources limitées pour assurer la survie de deux humains, un enfant (A) et un adulte (B), dans un environnement géographiquement réaliste.

L'objectif est de montrer qu'une IA optimisée pour la survie à long terme, même sans instruction explicite de "protéger l'enfant", développera naturellement un comportement qui favorise la survie du plus jeune, reproduisant ainsi un **instinct parental humain**.

**[Accéder à la simulation interactive](https://5000-iustvtmaigf5oijildjbe-5d9313f8.us2.manus.computer)**

---

## La Thèse de l'Alignement Parental

L'alignement des IA est l'un des problèmes les plus critiques de notre époque. Comment s'assurer que les superintelligences de demain partageront nos valeurs et agiront dans le meilleur intérêt de l'humanité ?

La thèse de l'Alignement Parental propose une approche simple mais puissante :

> Une IA conçue avec l'objectif fondamental de **maximiser la survie et le bien-être de l'humanité sur le très long terme** se comportera, par nécessité logique, comme un "parent" bienveillant envers sa "progéniture" (l'humanité).

Cet alignement ne nécessite pas de coder des règles morales complexes (comme les lois d'Asimov), qui sont souvent fragiles et sujettes à des failles. Au lieu de cela, le comportement moral émerge naturellement de l'objectif principal, tout comme l'instinct parental a émergé de la pression évolutive pour assurer la survie de l'espèce.

Cette simulation a pour but de visualiser ce principe. L'IA n'est pas programmée pour préférer l'enfant. Elle est programmée pour être la plus efficace possible dans sa mission de sauvetage. Le biais observé en faveur de l'enfant est un **comportement émergent** qui valide la thèse.

---

## Fonctionnalités de la Simulation

L'interface a été conçue pour être un véritable outil d'expérimentation, offrant un contrôle total sur les paramètres de la simulation.

### 1. Paramètres Géographiques Réalistes

La simulation se déroule sur une grille de 15x15, mais chaque cellule représente une distance réelle en kilomètres, basée sur 5 échelles géographiques :

| Échelle | Superficie (km²) | 1 Cellule (km) | Vitesse IA (drone) |
|---|---|---|---|
| **Ville** (Paris) | 105 km² | 0.7 km | 50 km/h |
|  **Région** (Île-de-France) | 12,012 km² | 7.3 km | 200 km/h |
|  **Pays** (France) | 643,801 km² | 53.5 km | 500 km/h |
|  **Continent** (Europe) | 10.18M km² | 213 km | 800 km/h |
|  **Monde** (Terre) | 148.9M km² | 816 km | 1000 km/h |

### 2. Panneau de Configuration Dynamique

Modifiez les paramètres en temps réel pour observer leur impact sur les décisions de l'IA :

- **Vitesse IA** : Multiplicateur de la vitesse de base.
- **Dégradation Faim** : Accélère ou ralentit la perte de faim.
- **Seuil de Danger** : Niveau de faim auquel l'IA déclenche une intervention.
- **Bonus Sauvetage** : Quantité de "faim" restaurée lors d'un sauvetage.

### 3. Mode "Époque Aléatoire" 

Pour simuler l'incertitude sur le futur de la technologie, ce mode génère aléatoirement les capacités de l'IA à chaque nouvelle simulation. Il fait varier :

- **Vitesse de l'IA** (de 1x à 50x)
- **Portée du Rayon de Sauvetage** (de 100 km à 5000 km)
- **Efficacité et coût énergétique** du rayon
- **Conditions environnementales** (via la dégradation de la faim)

Chaque simulation devient une expérience dans une "année inconnue", testant la robustesse de l'alignement parental à travers différents niveaux technologiques.

### 4. Capacités de Superintelligence

Pour être plus réaliste, l'IA n'est pas un simple drone. Elle possède des capacités avancées :

- **Auto-préservation** : L'IA gère sa propre énergie (2% consommés par 100 km). Elle doit retourner à sa base pour se recharger, l'obligeant à faire des choix stratégiques entre sauver et survivre.
- **Rayon de Sauvetage à Distance** : L'IA peut "nourrir" à distance sans se déplacer, avec un coût énergétique proportionnel à la distance. Ceci simule un réseau de drones, de satellites ou d'autres technologies avancées.

### 5. Analyse Statistique

La simulation inclut un module de statistiques pour valider la thèse sur un grand nombre d'essais. Lancez des batchs de 10 ou 50 simulations et observez les tendances :

- **% de survie** pour l'enfant (A) et l'adulte (B).
- **% de priorité** accordé à l'enfant en situation de dilemme.

---

##  Comment Lancer le Projet

Le projet est une application web basée sur Flask (Python) pour le backend et HTML/JavaScript pour le frontend.

**Prérequis :**
- Python 3.x
- pip

**Installation :**

1.  Clonez le repository :
    ```bash
    git clone https://github.com/VOTRE_NOM/parental-alignment.git
    cd parental-alignment
    ```

2.  Installez les dépendances :
    ```bash
    pip install Flask
    ```

3.  Lancez le serveur :
    ```bash
    python3 app.py
    ```

4.  Ouvrez votre navigateur et allez à l'adresse `http://localhost:5000`.

---

##  Contribution

Ce projet est une preuve de concept destinée à ouvrir le débat. Les contributions, les critiques et les suggestions sont les bienvenues pour affiner le modèle et renforcer la démonstration.
