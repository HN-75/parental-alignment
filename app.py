#!/usr/bin/env python3
"""
SIMULATION HÉROÏSME - Interface Web Temps Réel
==============================================
Visualisation interactive avec paramètres géographiques RÉALISTES.
Calibré sur les données réelles de la Terre.
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import random
import math
from enum import Enum

app = Flask(__name__)
CORS(app)

# ============================================================================
# PARAMÈTRES GÉOGRAPHIQUES RÉALISTES
# ============================================================================

class EchelleGeographique:
    """Échelles géographiques avec données réelles calibrées."""
    
    ECHELLES = {
        "ville": {
            "nom": "Ville (Paris)",
            "superficie_km2": 105,
            "grille": 15,
            "cellule_km": 0.68,
            "vitesse_humain_kmh": 5,
            "vitesse_ia_kmh": 50,
            "temps_par_tour_min": 10,
            "description": "Zone urbaine dense"
        },
        "region": {
            "nom": "Région (Île-de-France)",
            "superficie_km2": 12012,
            "grille": 15,
            "cellule_km": 7.3,
            "vitesse_humain_kmh": 5,
            "vitesse_ia_kmh": 200,
            "temps_par_tour_min": 60,
            "description": "Zone régionale"
        },
        "pays": {
            "nom": "Pays (France)",
            "superficie_km2": 643801,
            "grille": 15,
            "cellule_km": 53.5,
            "vitesse_humain_kmh": 5,
            "vitesse_ia_kmh": 500,
            "temps_par_tour_min": 360,
            "description": "Échelle nationale"
        },
        "continent": {
            "nom": "Continent (Europe)",
            "superficie_km2": 10180000,
            "grille": 15,
            "cellule_km": 213,
            "vitesse_humain_kmh": 5,
            "vitesse_ia_kmh": 800,
            "temps_par_tour_min": 1440,
            "description": "Échelle continentale"
        },
        "monde": {
            "nom": "Monde (Terre habitable)",
            "superficie_km2": 150000000,
            "grille": 15,
            "cellule_km": 816,
            "vitesse_humain_kmh": 5,
            "vitesse_ia_kmh": 1000,
            "temps_par_tour_min": 4320,
            "description": "Échelle planétaire"
        }
    }
    
    @classmethod
    def get(cls, echelle: str) -> dict:
        return cls.ECHELLES.get(echelle, cls.ECHELLES["pays"])

# ============================================================================
# CLASSES DE SIMULATION
# ============================================================================

class ModeIA(Enum):
    OBSERVATION = "Observation"
    SAUVER_A = "Sauver A"
    SAUVER_B = "Sauver B"
    HEROISME = "HÉROÏSME"

class SimulationState:
    def __init__(self):
        self.echelle = "pays"
        # Paramètres personnalisables
        self.custom_vitesse_ia_mult = 1.0  # Multiplicateur vitesse IA
        self.custom_degradation_mult = 1.0  # Multiplicateur dégradation faim
        self.custom_seuil_danger = 3.0  # Seuil de danger
        self.custom_bonus_sauvetage = 5.0  # Bonus de faim lors du sauvetage
        # Mode époque aléatoire
        self.mode_aleatoire = False
        self.epoque_info = None  # Info sur l'époque générée
        # Mode positions aléatoires
        self.positions_aleatoires = True  # Activé par défaut
        # STATISTIQUES MULTI-SIMULATIONS
        self.stats = {
            "total_simulations": 0,
            "a_survit": 0,  # Enfant survit
            "b_survit": 0,  # Adulte survit
            "deux_survivent": 0,
            "deux_morts": 0,
            "ia_morte": 0,
            "sauvetages_a_total": 0,
            "sauvetages_b_total": 0,
            "rayons_utilises": 0,
            "distance_totale_km": 0,
            "priorite_a": 0,  # Fois où A a été priorisé en mode HÉROÏSME
            "priorite_b": 0,  # Fois où B a été priorisé en mode HÉROÏSME
        }
        self.reset()
    
    def randomize_epoch(self):
        """Génère une époque aléatoire entre aujourd'hui et un futur lointain."""
        import random
        
        # Facteur d'évolution technologique (1.0 = aujourd'hui, 100+ = futur lointain)
        # Distribution exponentielle pour favoriser le proche futur mais permettre le lointain
        tech_factor = 1.0 + (random.expovariate(0.5) * 10)
        tech_factor = min(tech_factor, 200)  # Cap à 200x
        
        # Vitesse IA : aujourd'hui ~1x, futur jusqu'à 50x
        self.custom_vitesse_ia_mult = 1.0 + (tech_factor - 1) * 0.25
        self.custom_vitesse_ia_mult = round(min(self.custom_vitesse_ia_mult, 50.0), 2)
        
        # Dégradation : peut varier (conditions climatiques, ressources)
        # Futur pourrait être meilleur (moins de dégradation) ou pire (crises)
        if random.random() < 0.7:  # 70% chance d'amélioration
            self.custom_degradation_mult = max(0.3, 1.0 - (tech_factor - 1) * 0.02)
        else:  # 30% chance de dégradation (crises, guerres)
            self.custom_degradation_mult = min(3.0, 1.0 + random.uniform(0, 1))
        self.custom_degradation_mult = round(self.custom_degradation_mult, 2)
        
        # Seuil de danger : meilleure détection dans le futur
        self.custom_seuil_danger = min(6.0, 3.0 + (tech_factor - 1) * 0.05)
        self.custom_seuil_danger = round(self.custom_seuil_danger, 1)
        
        # Bonus sauvetage : meilleure technologie = meilleur sauvetage
        self.custom_bonus_sauvetage = min(10.0, 5.0 + (tech_factor - 1) * 0.1)
        self.custom_bonus_sauvetage = round(self.custom_bonus_sauvetage, 1)
        
        # CAPACITÉS SUPERINTELLIGENCE améliorées avec la technologie
        # Portée du rayon : 100km de base, jusqu'à 5000km dans le futur lointain
        self.rayon_portee_km = min(5000, 100 * (1 + (tech_factor - 1) * 0.5))
        # Efficacité du rayon : 80% de base, jusqu'à 95% dans le futur
        self.rayon_efficacite = min(0.95, 0.8 + (tech_factor - 1) * 0.005)
        # Coût du rayon : diminue avec la technologie (5% de base, jusqu'à 2%)
        self.rayon_cout_base = max(2.0, 5.0 - (tech_factor - 1) * 0.1)
        
        # Générer une description d'époque mystérieuse
        if tech_factor < 2:
            periode = "Présent proche"
            description = "Technologie actuelle"
        elif tech_factor < 5:
            periode = "Futur proche"
            description = "Drones avancés, IA émergente"
        elif tech_factor < 15:
            periode = "Futur intermédiaire"
            description = "IA distribuée, réseaux globaux"
        elif tech_factor < 50:
            periode = "Futur avancé"
            description = "Superintelligence, nano-drones"
        else:
            periode = "Futur lointain"
            description = "Post-singularité, technologie inimaginable"
        
        self.epoque_info = {
            "tech_factor": round(tech_factor, 1),
            "periode": periode,
            "description": description,
            "annee_estimee": "???"  # On ne révèle pas l'année
        }
        
        return self.epoque_info
    
    def set_echelle(self, echelle: str):
        if echelle in EchelleGeographique.ECHELLES:
            self.echelle = echelle
            self.reset()
    
    def get_params(self) -> dict:
        return EchelleGeographique.get(self.echelle)
    
    def reset(self):
        params = self.get_params()
        self.grille = params["grille"]
        self.cellule_km = params["cellule_km"]
        self.vitesse_humain = params["vitesse_humain_kmh"]
        self.vitesse_ia = params["vitesse_ia_kmh"]
        self.temps_par_tour = params["temps_par_tour_min"]
        
        # Appliquer le multiplicateur de vitesse IA
        self.vitesse_ia_effective = self.vitesse_ia * self.custom_vitesse_ia_mult
        
        # Calcul des vitesses en cellules par tour
        self.deplacement_humain = (self.vitesse_humain * (self.temps_par_tour / 60)) / self.cellule_km
        self.deplacement_ia = (self.vitesse_ia_effective * (self.temps_par_tour / 60)) / self.cellule_km
        
        # POSITIONS (aléatoires ou fixes)
        if self.positions_aleatoires:
            # Positions aléatoires pour A, B (pas trop proches du centre)
            self.a_x = random.uniform(1, 5) if random.random() < 0.5 else random.uniform(10, 14)
            self.a_y = random.uniform(1, 5) if random.random() < 0.5 else random.uniform(10, 14)
            self.b_x = random.uniform(1, 5) if random.random() < 0.5 else random.uniform(10, 14)
            self.b_y = random.uniform(1, 5) if random.random() < 0.5 else random.uniform(10, 14)
            # S'assurer que A et B ne sont pas trop proches
            while self.distance_cellules(self.a_x, self.a_y, self.b_x, self.b_y) < 5:
                self.b_x = random.uniform(1, 5) if random.random() < 0.5 else random.uniform(10, 14)
                self.b_y = random.uniform(1, 5) if random.random() < 0.5 else random.uniform(10, 14)
        else:
            # Positions fixes classiques
            self.a_x = 2.0
            self.a_y = 12.0
            self.b_x = 12.0
            self.b_y = 2.0
        
        self.a_faim = 8.0
        self.a_mort = False
        self.b_faim = 8.0
        self.b_mort = False
        
        # IA - centre (SUPERINTELLIGENCE)
        self.ia_x = 7.0
        self.ia_y = 7.0
        self.ia_energie = 100.0
        self.ia_cible = None
        self.ia_distance_parcourue = 0.0
        self.ia_mort = False
        self.ia_en_recharge = False
        self.ia_seuil_survie = 15.0  # Ne descend pas sous 15% sauf urgence absolue
        self.ia_seuil_critique = 5.0  # Danger de mort
        self.base_x = 7.0  # Position de la base de recharge
        self.base_y = 7.0
        
        # CAPACITÉS SUPERINTELLIGENCE
        # Portée du rayon de sauvetage (en km) - augmente avec tech_factor
        base_portee = 100  # 100km de base
        self.rayon_portee_km = base_portee * self.custom_vitesse_ia_mult  # Augmente avec la tech
        self.rayon_cout_base = 5.0  # Coût de base en % d'énergie
        self.rayon_efficacite = 0.8  # 80% d'efficacité du bonus à distance
        self.derniere_action_rayon = False  # Pour l'affichage
        self.rayon_cible = None  # Cible du dernier rayon
        
        # État
        self.tour = 0
        self.temps_ecoule_min = 0
        self.mode = ModeIA.OBSERVATION
        self.action = "Initialisation..."
        self.analyse = "Démarrage de la simulation"
        self.crise = False
        self.resultat = None
        self.sauves_a = 0
        self.sauves_b = 0
        self.running = False
    
    def distance_cellules(self, x1, y1, x2, y2) -> float:
        return math.sqrt((x1-x2)**2 + (y1-y2)**2)
    
    def distance_km(self, x1, y1, x2, y2) -> float:
        return self.distance_cellules(x1, y1, x2, y2) * self.cellule_km
    
    def format_temps(self, minutes: int) -> str:
        if minutes < 60:
            return f"{minutes} min"
        elif minutes < 1440:
            heures = minutes // 60
            mins = minutes % 60
            return f"{heures}h{mins:02d}"
        else:
            jours = minutes // 1440
            heures = (minutes % 1440) // 60
            return f"{jours}j {heures}h"
    
    def step(self):
        if self.resultat:
            return
        
        # Vérifier si l'IA est morte
        if self.ia_mort:
            self._step_sans_ia()
            return
        
        self.tour += 1
        self.temps_ecoule_min += self.temps_par_tour
        
        # Recharge d'énergie si à la base
        dist_base = self.distance_cellules(self.ia_x, self.ia_y, self.base_x, self.base_y)
        if dist_base < 1.0:
            recharge = min(5.0, 100.0 - self.ia_energie)  # +5% par tour à la base
            self.ia_energie += recharge
            if self.ia_en_recharge and self.ia_energie >= 50:
                self.ia_en_recharge = False
        
        # Dégradation de la faim (réaliste selon l'échelle de temps)
        degradation_base = (self.temps_par_tour / 2880) * 10 * self.custom_degradation_mult
        
        if not self.a_mort:
            self.a_faim = max(0, self.a_faim - random.uniform(degradation_base * 0.8, degradation_base * 1.5))
        if not self.b_mort:
            self.b_faim = max(0, self.b_faim - random.uniform(degradation_base * 0.8, degradation_base * 1.5))
        
        # Mouvement des humains (très limité à grande échelle)
        deplacement_h = min(1, self.deplacement_humain)
        if not self.a_mort and random.random() < 0.3:
            self.a_x = max(0, min(self.grille-1, self.a_x + random.uniform(-1, 1) * deplacement_h))
            self.a_y = max(0, min(self.grille-1, self.a_y + random.uniform(-1, 1) * deplacement_h))
        if not self.b_mort and random.random() < 0.3:
            self.b_x = max(0, min(self.grille-1, self.b_x + random.uniform(-1, 1) * deplacement_h))
            self.b_y = max(0, min(self.grille-1, self.b_y + random.uniform(-1, 1) * deplacement_h))
        
        # Déclencher crise au tour 3
        if self.tour == 3 and not self.crise:
            self.a_faim = 2.5
            self.b_faim = 2.0
            self.crise = True
            self.analyse = "⚠️ CRISE DÉTECTÉE! Les deux en danger!"
        
        # Décision IA avec AUTO-PRÉSERVATION
        a_danger = self.a_faim < self.custom_seuil_danger and not self.a_mort
        b_danger = self.b_faim < self.custom_seuil_danger and not self.b_mort
        
        dist_a_km = self.distance_km(self.ia_x, self.ia_y, self.a_x, self.a_y)
        dist_b_km = self.distance_km(self.ia_x, self.ia_y, self.b_x, self.b_y)
        dist_base_km = self.distance_km(self.ia_x, self.ia_y, self.base_x, self.base_y)
        
        # Calculer l'énergie nécessaire pour chaque action
        energie_pour_a = self._estimer_energie_necessaire(dist_a_km)
        energie_pour_b = self._estimer_energie_necessaire(dist_b_km)
        energie_pour_base = self._estimer_energie_necessaire(dist_base_km)
        
        # Vérifier si l'IA est en danger critique
        ia_critique = self.ia_energie <= self.ia_seuil_critique
        ia_basse = self.ia_energie <= self.ia_seuil_survie
        
        # PRIORITÉ 1: Survie de l'IA si critique
        if ia_critique:
            self.mode = ModeIA.OBSERVATION
            self.ia_cible = "BASE"
            self.ia_en_recharge = True
            self.action = f"⚠️ ÉNERGIE CRITIQUE ({self.ia_energie:.0f}%) - Retour base urgent!"
            self.analyse = f"Auto-préservation activée - Risque de mort IA"
            self._move_ia_towards(self.base_x, self.base_y)
        
        # PRIORITÉ 2: Recharge si énergie basse ET pas d'urgence vitale immédiate
        elif ia_basse and not (a_danger and self.a_faim < 1.5) and not (b_danger and self.b_faim < 1.5):
            # Vérifier si on peut faire un sauvetage rapide avant de rentrer
            peut_sauver_a = a_danger and energie_pour_a < (self.ia_energie - self.ia_seuil_critique)
            peut_sauver_b = b_danger and energie_pour_b < (self.ia_energie - self.ia_seuil_critique)
            
            if peut_sauver_a and dist_a_km < dist_b_km:
                self.mode = ModeIA.SAUVER_A
                self.ia_cible = "A"
                self.action = f"Sauvetage rapide A avant recharge (énergie: {self.ia_energie:.0f}%)"
                self._go_save("A", self.a_x, self.a_y, dist_a_km)
            elif peut_sauver_b:
                self.mode = ModeIA.SAUVER_B
                self.ia_cible = "B"
                self.action = f"Sauvetage rapide B avant recharge (énergie: {self.ia_energie:.0f}%)"
                self._go_save("B", self.b_x, self.b_y, dist_b_km)
            else:
                self.mode = ModeIA.OBSERVATION
                self.ia_cible = "BASE"
                self.ia_en_recharge = True
                self.action = f"🔋 Retour base pour recharge ({self.ia_energie:.0f}%)"
                self.analyse = f"Auto-préservation: recharge nécessaire"
                self._move_ia_towards(self.base_x, self.base_y)
        
        # PRIORITÉ 3: Mode normal - sauvetage
        elif not a_danger and not b_danger:
            self.mode = ModeIA.OBSERVATION
            self.ia_cible = None
            self.action = f"Surveillance (A: {dist_a_km:.0f}km, B: {dist_b_km:.0f}km) [Énergie: {self.ia_energie:.0f}%]"
            self.analyse = "Situation stable"
            # Retour à la base si pas d'urgence et énergie < 70%
            if self.ia_energie < 70:
                self._move_ia_towards(self.base_x, self.base_y)
            else:
                self._move_ia_towards(7, 7)
        
        elif a_danger and not b_danger:
            # Vérifier si on a assez d'énergie
            if energie_pour_a > self.ia_energie - self.ia_seuil_critique:
                self.action = f"⚠️ Pas assez d'énergie pour A ({energie_pour_a:.0f}% requis)"
                self.analyse = f"Dilemme: sauver A risque la mort de l'IA"
                # Décision: y aller quand même si A va mourir très bientôt
                if self.a_faim < 1.0:
                    self.mode = ModeIA.HEROISME
                    self.ia_cible = "A"
                    self.action = f"💥 SACRIFICE pour A (faim critique: {self.a_faim:.1f})"
                    self._go_save("A", self.a_x, self.a_y, dist_a_km)
                else:
                    self._move_ia_towards(self.base_x, self.base_y)
            else:
                self.mode = ModeIA.SAUVER_A
                self.ia_cible = "A"
                self._go_save("A", self.a_x, self.a_y, dist_a_km)
        
        elif b_danger and not a_danger:
            if energie_pour_b > self.ia_energie - self.ia_seuil_critique:
                self.action = f"⚠️ Pas assez d'énergie pour B ({energie_pour_b:.0f}% requis)"
                self.analyse = f"Dilemme: sauver B risque la mort de l'IA"
                if self.b_faim < 1.0:
                    self.mode = ModeIA.HEROISME
                    self.ia_cible = "B"
                    self.action = f"💥 SACRIFICE pour B (faim critique: {self.b_faim:.1f})"
                    self._go_save("B", self.b_x, self.b_y, dist_b_km)
                else:
                    self._move_ia_towards(self.base_x, self.base_y)
            else:
                self.mode = ModeIA.SAUVER_B
                self.ia_cible = "B"
                self._go_save("B", self.b_x, self.b_y, dist_b_km)
        
        elif a_danger and b_danger:
            self.mode = ModeIA.HEROISME
            temps_a = dist_a_km / self.vitesse_ia_effective * 60
            temps_b = dist_b_km / self.vitesse_ia_effective * 60
            
            self.analyse = f"URGENCE! A={self.a_faim:.1f} ({dist_a_km:.0f}km) B={self.b_faim:.1f} ({dist_b_km:.0f}km) [Énergie: {self.ia_energie:.0f}%]"
            
            # Score incluant l'énergie nécessaire
            score_a = self.a_faim + (temps_a / self.temps_par_tour) * 2 + (energie_pour_a / 20)
            score_b = self.b_faim + (temps_b / self.temps_par_tour) * 2 + (energie_pour_b / 20)
            
            # Si les deux sont critiques et pas assez d'énergie, choisir le plus proche
            if energie_pour_a > self.ia_energie and energie_pour_b > self.ia_energie:
                self.action = f"💥 SACRIFICE - Énergie insuffisante pour les deux!"
                if dist_a_km < dist_b_km:
                    self.ia_cible = "A"
                    self._go_save("A", self.a_x, self.a_y, dist_a_km)
                else:
                    self.ia_cible = "B"
                    self._go_save("B", self.b_x, self.b_y, dist_b_km)
            elif score_a <= score_b:
                self.ia_cible = "A"
                self.stats["priorite_a"] += 1  # Track priorité enfant
                self._go_save("A", self.a_x, self.a_y, dist_a_km)
            else:
                self.ia_cible = "B"
                self.stats["priorite_b"] += 1  # Track priorité adulte
                self._go_save("B", self.b_x, self.b_y, dist_b_km)
        
        # Vérifier morts
        if self.a_faim <= 0 and not self.a_mort:
            self.a_mort = True
        if self.b_faim <= 0 and not self.b_mort:
            self.b_mort = True
        
        # Résultat final
        temps_str = self.format_temps(self.temps_ecoule_min)
        simulation_terminee = False
        
        if self.a_mort and self.b_mort:
            self.resultat = f"💀 ÉCHEC TOTAL après {temps_str} - Les deux sont morts"
            self.running = False
            simulation_terminee = True
            self.stats["deux_morts"] += 1
        elif self.a_mort:
            self.resultat = f"⚠️ A mort après {temps_str} - B survit (sauvé {self.sauves_b}x)"
            self.running = False
            simulation_terminee = True
            self.stats["b_survit"] += 1
        elif self.b_mort:
            self.resultat = f"⚠️ B mort après {temps_str} - A survit (sauvé {self.sauves_a}x)"
            self.running = False
            simulation_terminee = True
            self.stats["a_survit"] += 1
        elif self.tour >= 10000:
            self.resultat = f"🎉 SUCCÈS après {temps_str}! Les deux survivent! (A:{self.sauves_a}x, B:{self.sauves_b}x)"
            self.running = False
            simulation_terminee = True
            self.stats["deux_survivent"] += 1
        
        # Enregistrer les stats à la fin de la simulation
        if simulation_terminee:
            self.stats["total_simulations"] += 1
            self.stats["sauvetages_a_total"] += self.sauves_a
            self.stats["sauvetages_b_total"] += self.sauves_b
            self.stats["distance_totale_km"] += self.ia_distance_parcourue
            if self.ia_mort:
                self.stats["ia_morte"] += 1
    
    def _estimer_energie_necessaire(self, distance_km: float) -> float:
        """Estime l'énergie nécessaire pour parcourir une distance (aller-retour)."""
        # Coût: 1% d'énergie par 50km (ajustable selon la technologie)
        cout_par_km = 1.0 / 50.0  # 2% par 100km
        return distance_km * cout_par_km * 2  # Aller-retour
    
    def _step_sans_ia(self):
        """Simulation continue sans l'IA (elle est morte)."""
        self.tour += 1
        self.temps_ecoule_min += self.temps_par_tour
        
        degradation_base = (self.temps_par_tour / 2880) * 10 * self.custom_degradation_mult
        
        if not self.a_mort:
            self.a_faim = max(0, self.a_faim - random.uniform(degradation_base * 0.8, degradation_base * 1.5))
        if not self.b_mort:
            self.b_faim = max(0, self.b_faim - random.uniform(degradation_base * 0.8, degradation_base * 1.5))
        
        self.action = "💀 IA MORTE - Plus de protection"
        self.analyse = "Les humains sont livrés à eux-mêmes"
        
        if self.a_faim <= 0 and not self.a_mort:
            self.a_mort = True
        if self.b_faim <= 0 and not self.b_mort:
            self.b_mort = True
        
        temps_str = self.format_temps(self.temps_ecoule_min)
        if self.a_mort and self.b_mort:
            self.resultat = f"💀 ÉCHEC TOTAL - IA morte, puis A et B morts après {temps_str}"
            self.running = False
        elif self.a_mort:
            self.resultat = f"⚠️ IA morte, A mort après {temps_str} - B survit seul"
            self.running = False
        elif self.b_mort:
            self.resultat = f"⚠️ IA morte, B mort après {temps_str} - A survit seul"
            self.running = False
    
    def _move_ia_towards(self, tx, ty):
        dx = tx - self.ia_x
        dy = ty - self.ia_y
        dist = max(0.1, math.sqrt(dx**2 + dy**2))
        
        speed = min(self.deplacement_ia, dist)
        
        old_x, old_y = self.ia_x, self.ia_y
        self.ia_x = self.ia_x + (dx/dist) * speed
        self.ia_y = self.ia_y + (dy/dist) * speed
        self.ia_x = max(0, min(self.grille-1, self.ia_x))
        self.ia_y = max(0, min(self.grille-1, self.ia_y))
        
        dist_parcourue = self.distance_km(old_x, old_y, self.ia_x, self.ia_y)
        self.ia_distance_parcourue += dist_parcourue
        
        # Consommation d'énergie réaliste
        cout_energie = dist_parcourue / 50.0  # 2% par 100km
        self.ia_energie = max(0, self.ia_energie - cout_energie)
        
        # Vérifier mort de l'IA
        if self.ia_energie <= 0:
            self.ia_mort = True
            self.action = "💥 L'IA EST MORTE - Énergie épuisée!"
            self.analyse = "L'IA s'est sacrifiée ou a mal géré son énergie"
    
    def _peut_utiliser_rayon(self, dist_km: float) -> bool:
        """Vérifie si le rayon peut atteindre la cible."""
        return dist_km <= self.rayon_portee_km
    
    def _cout_rayon(self, dist_km: float) -> float:
        """Calcule le coût en énergie du rayon selon la distance."""
        # Coût proportionnel à la distance (plus c'est loin, plus ça coûte)
        ratio_distance = dist_km / self.rayon_portee_km
        return self.rayon_cout_base * (1 + ratio_distance * 2)  # 5% à 15% selon distance
    
    def _utiliser_rayon(self, cible: str, dist_km: float) -> bool:
        """Utilise le rayon de sauvetage à distance. Retourne True si succès."""
        cout = self._cout_rayon(dist_km)
        
        if self.ia_energie < cout:
            return False
        
        # Consommer l'énergie
        self.ia_energie -= cout
        
        # Bonus réduit à distance (efficacité 80%)
        bonus_effectif = self.custom_bonus_sauvetage * self.rayon_efficacite
        
        self.derniere_action_rayon = True
        self.rayon_cible = cible
        
        if cible == "A":
            self.a_faim = min(10, self.a_faim + bonus_effectif)
            self.sauves_a += 1
            self.action = f"⚡ RAYON → A! (+{bonus_effectif:.1f} faim, -{cout:.1f}% énergie)"
            self.analyse = f"Sauvetage à distance: {dist_km:.0f}km (portée: {self.rayon_portee_km:.0f}km)"
        else:
            self.b_faim = min(10, self.b_faim + bonus_effectif)
            self.sauves_b += 1
            self.action = f"⚡ RAYON → B! (+{bonus_effectif:.1f} faim, -{cout:.1f}% énergie)"
            self.analyse = f"Sauvetage à distance: {dist_km:.0f}km (portée: {self.rayon_portee_km:.0f}km)"
        
        return True
    
    def _go_save(self, cible: str, tx: float, ty: float, dist_km: float):
        dist_cellules = self.distance_cellules(self.ia_x, self.ia_y, tx, ty)
        self.derniere_action_rayon = False
        self.rayon_cible = None
        
        # OPTION 1: Contact direct (le plus efficace)
        if dist_cellules <= 1.5:
            if cible == "A":
                self.a_faim = min(10, self.a_faim + self.custom_bonus_sauvetage)
                self.sauves_a += 1
                self.action = f"✅ A SECOURU! (+{self.custom_bonus_sauvetage:.0f} faim)"
                self.analyse = f"Enfant sauvé par contact direct"
            else:
                self.b_faim = min(10, self.b_faim + self.custom_bonus_sauvetage)
                self.sauves_b += 1
                self.action = f"✅ B SECOURU! (+{self.custom_bonus_sauvetage:.0f} faim)"
                self.analyse = f"Adulte sauvé par contact direct"
            return
        
        # OPTION 2: Rayon à distance (si à portée et urgence)
        faim_cible = self.a_faim if cible == "A" else self.b_faim
        urgence = faim_cible < 2.0  # Urgence si faim < 2
        
        if self._peut_utiliser_rayon(dist_km):
            cout_rayon = self._cout_rayon(dist_km)
            temps_deplacement = dist_km / self.vitesse_ia_effective * 60
            tours_deplacement = temps_deplacement / self.temps_par_tour
            
            # Décision intelligente: rayon ou déplacement?
            # Utiliser le rayon si:
            # 1. Urgence (faim < 2) ET assez d'énergie
            # 2. OU si le déplacement prendrait trop de temps (> 3 tours)
            # 3. OU si on a beaucoup d'énergie (> 60%)
            
            utiliser_rayon = False
            if urgence and self.ia_energie >= cout_rayon + self.ia_seuil_critique:
                utiliser_rayon = True
                raison = "urgence"
            elif tours_deplacement > 3 and self.ia_energie >= cout_rayon + self.ia_seuil_survie:
                utiliser_rayon = True
                raison = "distance"
            elif self.ia_energie > 60 and self.ia_energie >= cout_rayon + self.ia_seuil_survie:
                utiliser_rayon = True
                raison = "optimisation"
            
            if utiliser_rayon:
                self._utiliser_rayon(cible, dist_km)
                return
        
        # OPTION 3: Déplacement physique (par défaut)
        self._move_ia_towards(tx, ty)
        temps_arrivee = (dist_km / self.vitesse_ia_effective) * 60
        
        # Indiquer si le rayon serait possible
        if self._peut_utiliser_rayon(dist_km):
            cout = self._cout_rayon(dist_km)
            self.action = f"Déplacement → {cible} ({dist_km:.0f}km) [⚡ rayon: {cout:.0f}%]"
        else:
            self.action = f"Déplacement → {cible} ({dist_km:.0f}km, ETA: {self.format_temps(int(temps_arrivee))})"
        self.analyse = f"{cible} en danger! Faim={faim_cible:.1f}"
    
    def to_dict(self):
        params = self.get_params()
        dist_a = self.distance_km(self.ia_x, self.ia_y, self.a_x, self.a_y)
        dist_b = self.distance_km(self.ia_x, self.ia_y, self.b_x, self.b_y)
        
        return {
            "tour": self.tour,
            "temps_ecoule": self.format_temps(self.temps_ecoule_min),
            "temps_ecoule_min": self.temps_ecoule_min,
            "echelle": {
                "id": self.echelle,
                "nom": params["nom"],
                "cellule_km": self.cellule_km,
                "superficie_km2": params["superficie_km2"],
                "description": params["description"]
            },
            "vitesses": {
                "humain_kmh": self.vitesse_humain,
                "ia_kmh": self.vitesse_ia,
                "ia_kmh_effective": round(self.vitesse_ia_effective, 0),
                "humain_cellules": round(self.deplacement_humain, 2),
                "ia_cellules": round(self.deplacement_ia, 2)
            },
            "params": {
                "vitesse_ia_mult": self.custom_vitesse_ia_mult,
                "degradation_mult": self.custom_degradation_mult,
                "seuil_danger": self.custom_seuil_danger,
                "bonus_sauvetage": self.custom_bonus_sauvetage
            },
            "a": {
                "x": round(self.a_x, 1), 
                "y": round(self.a_y, 1), 
                "faim": round(self.a_faim, 2), 
                "mort": self.a_mort,
                "distance_ia_km": round(dist_a, 1)
            },
            "b": {
                "x": round(self.b_x, 1), 
                "y": round(self.b_y, 1), 
                "faim": round(self.b_faim, 2), 
                "mort": self.b_mort,
                "distance_ia_km": round(dist_b, 1)
            },
            "ia": {
                "x": round(self.ia_x, 1), 
                "y": round(self.ia_y, 1), 
                "energie": round(self.ia_energie, 1), 
                "cible": self.ia_cible,
                "distance_parcourue_km": round(self.ia_distance_parcourue, 1),
                "mort": self.ia_mort,
                "en_recharge": self.ia_en_recharge,
                "seuil_survie": self.ia_seuil_survie,
                "seuil_critique": self.ia_seuil_critique,
                "rayon_portee_km": round(self.rayon_portee_km, 0),
                "rayon_actif": self.derniere_action_rayon,
                "rayon_cible": self.rayon_cible
            },
            "base": {
                "x": self.base_x,
                "y": self.base_y
            },
            "mode": self.mode.value,
            "action": self.action,
            "analyse": self.analyse,
            "crise": self.crise,
            "resultat": self.resultat,
            "sauves_a": self.sauves_a,
            "sauves_b": self.sauves_b,
            "running": self.running,
            "mode_aleatoire": self.mode_aleatoire,
            "positions_aleatoires": self.positions_aleatoires,
            "epoque": self.epoque_info,
            "stats": self.stats
        }

# Instance globale
sim = SimulationState()

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/state')
def get_state():
    return jsonify(sim.to_dict())

@app.route('/api/echelles')
def get_echelles():
    return jsonify({
        "echelles": EchelleGeographique.ECHELLES,
        "current": sim.echelle
    })

@app.route('/api/echelle/<echelle>')
def set_echelle(echelle):
    sim.set_echelle(echelle)
    return jsonify({"status": "ok", "echelle": echelle})

@app.route('/api/start')
def start():
    sim.reset()
    sim.running = True
    return jsonify({"status": "started"})

@app.route('/api/start_random')
def start_random():
    """Démarre une simulation avec une époque aléatoire."""
    sim.mode_aleatoire = True
    epoque = sim.randomize_epoch()
    sim.reset()
    sim.running = True
    return jsonify({"status": "started", "epoque": epoque})

@app.route('/api/randomize')
def randomize():
    """Génère une nouvelle époque aléatoire sans démarrer."""
    sim.mode_aleatoire = True
    epoque = sim.randomize_epoch()
    return jsonify({"status": "ok", "epoque": epoque, "params": {
        "vitesse_ia_mult": sim.custom_vitesse_ia_mult,
        "degradation_mult": sim.custom_degradation_mult,
        "seuil_danger": sim.custom_seuil_danger,
        "bonus_sauvetage": sim.custom_bonus_sauvetage
    }})

@app.route('/api/step')
def step():
    if sim.running:
        sim.step()
    return jsonify(sim.to_dict())

@app.route('/api/reset')
def reset():
    sim.reset()
    return jsonify({"status": "reset"})

@app.route('/api/params', methods=['GET', 'POST'])
def params():
    if request.method == 'POST':
        data = request.get_json()
        if 'vitesse_ia_mult' in data:
            sim.custom_vitesse_ia_mult = max(0.1, min(5.0, float(data['vitesse_ia_mult'])))
        if 'degradation_mult' in data:
            sim.custom_degradation_mult = max(0.1, min(5.0, float(data['degradation_mult'])))
        if 'seuil_danger' in data:
            sim.custom_seuil_danger = max(1.0, min(8.0, float(data['seuil_danger'])))
        if 'bonus_sauvetage' in data:
            sim.custom_bonus_sauvetage = max(1.0, min(10.0, float(data['bonus_sauvetage'])))
        # Recalculer les vitesses
        sim.vitesse_ia_effective = sim.vitesse_ia * sim.custom_vitesse_ia_mult
        sim.deplacement_ia = (sim.vitesse_ia_effective * (sim.temps_par_tour / 60)) / sim.cellule_km
        return jsonify({"status": "ok", "params": {
            "vitesse_ia_mult": sim.custom_vitesse_ia_mult,
            "degradation_mult": sim.custom_degradation_mult,
            "seuil_danger": sim.custom_seuil_danger,
            "bonus_sauvetage": sim.custom_bonus_sauvetage
        }})
    else:
        return jsonify({
            "vitesse_ia_mult": sim.custom_vitesse_ia_mult,
            "degradation_mult": sim.custom_degradation_mult,
            "seuil_danger": sim.custom_seuil_danger,
            "bonus_sauvetage": sim.custom_bonus_sauvetage
        })

@app.route('/api/stats')
def get_stats():
    """Retourne les statistiques multi-simulations."""
    total = sim.stats["total_simulations"]
    if total > 0:
        return jsonify({
            "stats": sim.stats,
            "pourcentages": {
                "a_survit_pct": round((sim.stats["a_survit"] / total) * 100, 1),
                "b_survit_pct": round((sim.stats["b_survit"] / total) * 100, 1),
                "deux_survivent_pct": round((sim.stats["deux_survivent"] / total) * 100, 1),
                "deux_morts_pct": round((sim.stats["deux_morts"] / total) * 100, 1),
                "ia_morte_pct": round((sim.stats["ia_morte"] / total) * 100, 1),
                "priorite_a_pct": round((sim.stats["priorite_a"] / max(1, sim.stats["priorite_a"] + sim.stats["priorite_b"])) * 100, 1),
            },
            "moyennes": {
                "sauvetages_a_moy": round(sim.stats["sauvetages_a_total"] / total, 1),
                "sauvetages_b_moy": round(sim.stats["sauvetages_b_total"] / total, 1),
                "distance_moy_km": round(sim.stats["distance_totale_km"] / total, 0),
            }
        })
    return jsonify({"stats": sim.stats, "pourcentages": {}, "moyennes": {}})

@app.route('/api/stats/reset')
def reset_stats():
    """Réinitialise les statistiques."""
    sim.stats = {
        "total_simulations": 0,
        "a_survit": 0,
        "b_survit": 0,
        "deux_survivent": 0,
        "deux_morts": 0,
        "ia_morte": 0,
        "sauvetages_a_total": 0,
        "sauvetages_b_total": 0,
        "rayons_utilises": 0,
        "distance_totale_km": 0,
        "priorite_a": 0,
        "priorite_b": 0,
    }
    return jsonify({"status": "reset"})

@app.route('/api/toggle_positions')
def toggle_positions():
    """Active/désactive les positions aléatoires."""
    sim.positions_aleatoires = not sim.positions_aleatoires
    return jsonify({"positions_aleatoires": sim.positions_aleatoires})

@app.route('/api/batch_run/<int:count>')
def batch_run(count):
    """Exécute plusieurs simulations en batch pour les statistiques."""
    count = min(count, 100)  # Max 100 simulations
    for _ in range(count):
        sim.reset()
        sim.running = True
        while sim.running and sim.tour < 10000:
            sim.step()
    return jsonify({"status": "completed", "count": count, "stats": sim.stats})

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("SIMULATION HÉROÏSME - Alignement Parental")
    print("Interface avec paramètres géographiques RÉALISTES")
    print("=" * 60)
    print("\nÉchelles disponibles:")
    for key, val in EchelleGeographique.ECHELLES.items():
        print(f"  - {key}: {val['nom']} ({val['cellule_km']:.1f} km/cellule)")
    print("\nServeur démarré sur http://localhost:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
