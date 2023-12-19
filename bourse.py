"""Implémentation de la classe Bourse permettant de récupérer le prix d'une action à une date.
"""
import sys
import datetime
import json
import requests
from exceptions import ErreurDate


class Bourse:
    """Classe permettant de récupérer le prix d'une action à une date."""

    valeurs_possibles = ("fermeture", "ouverture", "min", "max", "volume")

    def prix(self, symbole: str, date: datetime.date):
        """Retourne le prix d'une action à une date donnée."""

        if date > datetime.date.today():
            raise ErreurDate(
                "La date spécifiée correspond à une date postérieure!")

        # On récupère les prix d'ouverture et de fermeture des 3 derniers jours
        # (la bourse est fermée le week-end et parfois les jours fériés).
        données_symbole = self.données_bourse(symbole, date - datetime.timedelta(days=3), date)
        fermeture = self.trouver_valeurs(données_symbole, "fermeture")
        return fermeture[-1][1]

    def données_bourse(self, symbole: str, début: datetime.date, fin: datetime.date):
        """
        Récupère les données historiques du marché boursier pour un symbole donné 
        dans une plage de dates spécifiée.

        Args:
            symbole (str): Le symbole de l'action.
            début (datetime.date): La date de début de la plage de données.
            fin (datetime.date): La date de fin de la plage de données.

        Returns:
            dict: Un dictionnaire contenant les données historiques du marché boursier.
        """

        if fin is None:
            fin = datetime.date.today()
        if début is None:
            début = fin

        response = requests.get(
            url=f'https://pax.ulaval.ca/action/{symbole}/historique/',
            params={
                'début': str(début),
                'fin': str(fin),
            },
            timeout=30
        )

        if response.status_code != 200:
            print("La réponse de la requête envoyée n'est pas valide.")
            sys.exit()

        response = json.loads(response.text)

        if "message d'erreur" in response:
            print("Erreur: " + response["message d'erreur"])
            sys.exit()

        return response

    def trouver_valeurs(self, données_bourse: dict, valeur: str):
        """
        Trouve les valeurs d'un attribut spécifique dans les données de la bourse.

        Args:
            données_bourse (dict): Les données de la bourse.
            valeur (str): L'attribut pour lequel trouver les valeurs.

        Returns:
            list: Une liste de tuples contenant la date et la valeur correspondante pour l'attribut.
        """

        if valeur not in self.valeurs_possibles:
            print(
                f"Vous devez choisir un attribute entre:\n {str(self.valeurs_possibles)}.")
            return None

        valeurs = [(datetime.date.fromisoformat(r_date), float(historique[valeur]))
            for r_date, historique in données_bourse['historique'].items()]
        valeurs.reverse()
        return valeurs
