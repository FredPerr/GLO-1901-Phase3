"""Module principal du programme, analyse de la commande de l'utilisateur"""
from datetime import date
from argparse import Namespace, ArgumentParser
from portefeuille import Portefeuille
from bourse import Bourse

def analyser_commande()-> Namespace:
    """Analyse la commande entrée par l'utilisateur"""

    def configure_subparser(parser: ArgumentParser):
        parser.add_argument('-d', '--date', metavar="DATE",
                            type=date.fromisoformat,
                            help="Date effective (par défaut, date du jour)", default=date.today())
        parser.add_argument('-q', '--quantité', metavar="INT",
                            type=int, help="Quantité désirée (par défaut: 1)", default=1)
        parser.add_argument('-t', '--titres', metavar="STRING", nargs='+',
                            help="Le ou les titres à considérer \
                            (par défaut, tous les titres du portefeuille sont considérés)")
        parser.add_argument('-r', '--rendement', metavar="FLOAT",
                            help="Rendement annuel global (par défaut, 0)",
                            default=0, type=float)
        parser.add_argument('-v', '--volatilité', metavar="FLOAT",
                            help="Indice de volatilité global sur le rendement \
                                annuel (par défaut, 0)",
                            default=0, type=float)
        parser.add_argument('-g', '--graphique', metavar="BOOL",
                            help="Affichage graphique (par défaut, pas d'affichage graphique)",
                            default=False, type=bool)
        parser.add_argument('-p', '--portefeuille', metavar="STRING",
                            help="Nom de portefeuille (par défaut, utiliser folio)",
                            default="folio", type=str)

    parser = ArgumentParser(prog="gesport.py", description="Gestionnaire de portefeuille d'actions")

    subparser = parser.add_subparsers(required=True, title="ACTIONS", dest = 'action')
    configure_subparser(subparser.add_parser('déposer',
        help="À la date spécifiée, déposer la quantité de dollars spécifiée"))

    configure_subparser(subparser.add_parser('acheter',
        help="À la date spécifiée, acheter la quantité spécifiée des titres spécifiées"))
    configure_subparser(subparser.add_parser('vendre',
        help="À la date spécifiée, vendre la quantité spécifiée des titres spécifiées"))
    configure_subparser(subparser.add_parser('lister',
        help="À la date spécifiée, pour chacun des titres spécifiés, lister les nombres \
            d'actions détenues ainsi que leur"))
    configure_subparser(subparser.add_parser('projeter',
        help="À la date future spécifiée, projeter la valeur totale des titres spécifiés, \
            en tenant compte des rendements et indices de volatilité spécifiés"))

    return parser.parse_args()

args = analyser_commande()
portefeuille = Portefeuille(Bourse(), args.portefeuille)

if args.action == "déposer":
    portefeuille.déposer(args.quantité, args.date)
if args.action == 'acheter':
    for i in args.titres:
        portefeuille.acheter(i, args.quantité, args.date)
if args.action == 'vendre':
    portefeuille.vendre(args.titres, args.quantité, args.date)
if args.action == 'projeter':
    portefeuille.projection(portefeuille.valeur_des_titres(args.titres, date.today()), args.rendement, args.date - date.today(), 365)
if args.action == 'lister':
    portefeuille.titres(args.date)