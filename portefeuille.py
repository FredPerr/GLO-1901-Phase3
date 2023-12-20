"""Gestion d'un portefeuille d'actions et de liquidités
"""
from typing import Union
import datetime as dt
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from exceptions import ErreurDate, LiquiditéInsuffisante, ErreurQuantité
from bourse import Bourse


class Portefeuille:
    """Gestion d'un portefeuille d'actions et de liquidités"""

    def __init__(self, bourse: Bourse, nom: str = "folio"):
        self.bourse = bourse
        self.nom = nom
        self.courtage = []  # (date, symbole, quantité, prix unitaire)
        self.courant = []  # (date, montant)

    def déposer(self, montant: float, date: dt.date = dt.date.today()):
        """
        Dépose un montant spécifié dans le portefeuille à la date spécifiée.

        Args:
            montant (float): Le montant à déposer dans le portefeuille.
            date (datetime.date, optional): La date du dépôt. Par défaut, la date du 
                jour est utilisée.

        Raises:
            ErreurDate: Si la date spécifiée est postérieure à la date du jour.
        """
        if date > dt.date.today():
            raise ErreurDate(
                "La date spécifiée est postérieure à la date du jour.")
        self.courtage.append((date, montant))

    def solde(self, date: dt.date = dt.date.today()):
        """
        Calcule le solde du portefeuille jusqu'à une date spécifiée.

        Args:
            date (datetime.date, facultatif): La date jusqu'à laquelle le solde est calculé.
                Par défaut, il s'agit de la date du jour.

        Raises:
            ErreurDate: Si la date spécifiée est dans le futur.

        Returns:
            float: Le solde du portefeuille jusqu'à la date spécifiée.
        """

        if date > dt.date.today():
            raise ErreurDate(
                "La date spécifiée est postérieure à la date du jour.")

        solde = 0.0
        for t_date, t_montant in self.courtage:
            if t_date <= date:
                solde += t_montant
        return solde

    def acheter(self, symbole: str, quantité: int, date: dt.date = dt.date.today()):
        """
        Achète une quantité spécifiée d'un symbole donné à une date donnée.

        Args:
            symbole (str): Le symbole de l'action à acheter.
            quantité (int): La quantité d'actions à acheter.
            date (dt.date, optional): La date à laquelle effectuer l'achat. Par défaut, 
                la date du jour.

        Raises:
            ErreurDate: Si la date spécifiée est postérieure à la date du jour.
            LiquiditéInsuffisante: Si l'argent restant dans le portefeuille est insuffisant 
                pour effectuer l'achat.
        """
        if date > dt.date.today():
            raise ErreurDate(
                "La date spécifiée est postérieure à la date du jour.")

        prix = self.bourse.prix(symbole, date)
        valeur_totale = prix * quantité
        if self.solde(date) < valeur_totale:
            raise LiquiditéInsuffisante(
                "L'argent restant dans le portefeuille est insuffisant")

        self.courant.append((date, -valeur_totale))
        self.courtage.append((date, symbole, quantité, prix))

    def nombre_actions(self, symbole: str, date: dt.date = dt.date.today()):
        """
        Retourne le nombre total d'actions pour un symbole donné à une date donnée.

        Args:
            symbole (str): Le symbole de l'action.
            date (dt.date, optional): La date à laquelle on souhaite obtenir le nombre d'actions. 
                Par défaut, la date est définie sur la date du jour.

        Returns:
            int: Le nombre total d'actions pour le symbole donné à la date donnée.
        """
        total = 0
        for t_date, t_symbole, t_quantité, _ in self.courtage:
            if t_date <= date and t_symbole == symbole:
                total += t_quantité
        return total

    def vendre(self, symbole: str, quantité: int, date: dt.date = dt.date.today()):
        """
        Vend des actions du portefeuille.

        Args:
            symbole (str): Le symbole de l'action à vendre.
            quantité (int): Le nombre d'actions à vendre.
            date (dt.date, optional): La date de la vente. Par défaut, la date du jour.

        Raises:
            ErreurDate: Si la date spécifiée est postérieure à la date du jour.
            ErreurQuantité: Si le nombre d'actions à vendre est supérieur au nombre 
                d'actions possédées.
        """

        if date > dt.date.today():
            raise ErreurDate(
                "La date spécifiée est postérieure à la date du jour.")

        if self.nombre_actions(symbole, date) < quantité:
            raise ErreurQuantité(
                "Le nombre d'actions à vendre est supérieur au nombre d'actions possédées.")

        prix = self.bourse.prix(symbole, date)
        valeur_totale = prix * quantité
        self.courtage.append((date, symbole, -quantité, prix))
        self.courant.append((date, valeur_totale))

    def valeur_totale(self, date: dt.date = dt.date.today()):
        """
        Calcule la valeur totale du portefeuille à une date donnée.

        Args:
            date (datetime.date, optional): La date à laquelle calculer la valeur totale. 
                Par défaut, la date du jour est utilisée.

        Returns:
            float: La valeur totale du portefeuille à la date spécifiée.

        Raises:
            ErreurDate: Si la date spécifiée est postérieure à la date du jour.
        """
        if date > dt.date.today():
            raise ErreurDate(
                "La date spécifiée est postérieure à la date du jour.")

        total = 0.0
        for t_date, t_montant in self.courant:
            if t_date <= date:
                total += t_montant
        return total + self.solde(date)

    def valeur_des_titres(self, symboles: iter, date: dt.date = dt.date.today()):
        """
        Calcule la valeur totale des titres pour les symboles donnés et la date spécifiée.

        Args:
            symboles (iter): Un itérable contenant les symboles des titres.
            date (dt.date, optionnel): La date pour laquelle calculer la valeur. 
                Par défaut, la date d'aujourd'hui.

        Raises:
            ErreurDate: Si la date spécifiée est dans le futur.
        Returns:
            float: La valeur totale des titres pour les symboles donnés et la date spécifiée.
        """
        if date > dt.date.today():
            raise ErreurDate(
                "La date spécifiée est postérieur à la date du jour.")

        total = 0.0
        for t_date, t_symbole, t_quantité, t_prix in self.courtage:
            if t_date <= date and t_symbole in symboles:
                total += t_quantité * t_prix
        return total

    def titres(self, date: dt.date = dt.date.today()):
        """
        Renvoie un dictionnaire contenant les titres détenus à une date donnée.

        Args:
            date (datetime.date, optional): La date à laquelle on souhaite obtenir les titres. 
                Par défaut, la date du jour est utilisée.

        Raises:
            ErreurDate: Si la date spécifiée est postérieure à la date du jour.

        Returns:
            dict: Un dictionnaire contenant les symboles des titres en tant que clés 
                et les quantités détenues en tant que valeurs.
        """
        if date > dt.date.today():
            raise ErreurDate(
                "La date spécifiée est postérieure à la date du jour.")

        titres = {}
        for t_date, t_symbole, t_quantité, _ in self.courtage:
            if t_date <= date and t_symbole != 0:
                nouvelle_quantité = t_quantité + titres.get(t_symbole, 0)
                if nouvelle_quantité == 0:
                    titres.pop(t_symbole)
                else:
                    titres.update({t_symbole: nouvelle_quantité})
        return titres

    def valeur_projetée(self, date: str, rendement: Union[float, dict]):
        """
        Calcule la valeur projetée du portefeuille à une date donnée en utilisant le 
            rendement spécifié.

        Args:
            date (str): La date à laquelle la valeur projetée doit être calculée.
            rendement (Union[float, dict]): Le rendement utilisé pour le calcul. 
                Peut être un nombre flottant unique ou un dictionnaire de rendements par symbole.

        Returns:
            float: La valeur projetée du portefeuille à la date spécifiée.
        """

        if date > dt.date.today():
            raise ErreurDate(
                "La date spécifiée est postérieur à la date du jour.")

        totale = 0.0
        if isinstance(rendement, float):
            for symbole, quantité in self.titres(date).items():
                prix = self.bourse.prix(symbole, date)
                totale += self.valeur_projetée_symbole(
                    date - dt.date.today(), prix, quantité, rendement)
        else:
            for symbole, quantité in self.titres(date).items():
                prix = self.bourse.prix(symbole, date)
                totale += self.valeur_projetée_symbole(
                    date - dt.date.today(), prix, quantité, rendement.get(symbole, 0))
        return totale

    def valeur_projetée_symbole(self, duration: dt.timedelta, prix: float, quantité: int,
                                 rendement: float):
        """
        Calcule la valeur projetée d'un symbole sur une période donnée.

        Args:
            duration (datetime.timedelta): La période sur laquelle calculer la valeur projetée.
            prix (float): Le prix du symbole.
            quantité (int): La quantité du symbole.
            rendement (float): Le rendement du symbole en pourcentage.

        Returns:
            float: La valeur projetée du symbole sur la période donnée.
        """
        diff_years = duration.days / 365
        remain_days = duration.days % 365
        return prix * quantité * (1 + rendement/100) ** diff_years + \
            remain_days / 365 * prix * quantité * rendement / 100
    

    #sauvegarde portefeuille

    def lire_json(self):
        porte_feuille = {}
        nom_fichier = f"{self.nom}.json"
        if os.path.isfile(nom_fichier):
            with open(nom_fichier, 'r', encoding="utf8") as fichier:
                porte_feuille = json.load(fichier)
        return porte_feuille


    def écrire_json(self):
        nom_fichier = f"{self.nom}.json"
        with open(nom_fichier, "w", encoding="utf8") as fichier:
            a = json.dumps(self)
            fichier.write(a)


    #rendement annuel
            
    def projection(self, vo, tau, annee, m):
        Vn = (vo*(1 + (tau/100))**annee)
        projection = (m/365)*Vn*(tau/100)
        return Vn + projection
    
    #calculer_quartiles
    def calculer_quartiles(self, volatilite, rendement):
        nbr_projection = 1000

        rendements = np.random.normal(rendement, volatilite, nbr_projection)

        Q1 = np.percentile(rendements, 25)
        Q2 = np.percentile(rendements, 50)
        Q3 = np.percentile(rendements, 75)

        return Q1, Q2, Q3
    
    
class PortefeuilleGraphique(Portefeuille):

    def __init__(self, bourse: Bourse, nom: str = "folio"):
        super().__init__(bourse, nom)

        def lister(self, date, valeurs):    # CHANGER VALEUR POUR CE QU'ON VEUT
            
            x = np.linspace(date, datetime.today())

            plt.title("Historique des valeurs des actions")
            plt.ylabel("Valeurs projetées à la bourse")
            plt.xlabel("Dates")
            plt.xticks(rotation=46)   #pour l'esthétique
            plt.plot(x, valeurs, "b-", label="valeur bourse")
            plt.legend()
            plt.grid(True)
            plt.show()


        def projeter(self):
    
