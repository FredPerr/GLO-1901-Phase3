"""Module principal du programme, analyse de la commande de l'utilisateur"""
from datetime import date, datetime
from argparse import Namespace, ArgumentParser
from portefeuille import PortefeuilleGraphique
from bourse import Bourse


def analyser_commande() -> Namespace:
    """Analyse la commande entrée par l'utilisateur"""

    def configure_subparser(parser: ArgumentParser):
        parser.add_argument('-d', '--date', metavar="DATE",
                            type=lambda s: datetime.strptime(
                                s, '%Y-%m-%d').date(),
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
                            default=False, type=bool, nargs='?')
        parser.add_argument('-p', '--portefeuille', metavar="STRING",
                            help="Nom de portefeuille (par défaut, utiliser folio)",
                            default="folio", type=str)

    parser = ArgumentParser(
        prog="gesport.py", description="Gestionnaire de portefeuille d'actions")

    subparser = parser.add_subparsers(
        required=True, title="ACTIONS", dest='action')
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


def parse_symbol(symbol: str):
    """Parse le symbole d'un titre"""
    if '(' not in symbol:
        return symbol, None, None
    parts = symbol.split('(')
    s = parts[0]
    parenthesis = parts[1][:-1].split(',')
    mu = float(parenthesis[0])
    sigma = float(parenthesis[1])
    return s, mu, sigma


args = analyser_commande()

bourse = Bourse()
portefeuille = PortefeuilleGraphique(bourse, args.portefeuille)

if args.action == "déposer":
    portefeuille.déposer(args.quantité, args.date)
    print(f"solde = {portefeuille.solde()}")
elif args.action == 'acheter':
    for title in args.titres:
        portefeuille.acheter(title, args.quantité, args.date)
    print(f"solde = {portefeuille.solde()}")
elif args.action == 'vendre':
    for title in args.titres:
        portefeuille.vendre(title, args.quantité, args.date)
    print(f"solde = {portefeuille.solde()}")
elif args.action == 'projeter':
    if args.titres is None:
        args.titres = portefeuille.titres(date.today()).keys()
    TOTAL = 0
    for title in args.titres:
        symbole, rendement, ecart_type = parse_symbol(title)
        vo = portefeuille.valeur_des_titres([symbole,], date.today())
        delta = args.date - date.today()
        TOTAL += portefeuille.projection(vo,
                                          rendement if rendement is not None else args.rendement,
                                          delta.days / 365,
                                          ecart_type if ecart_type is not None else args.volatilité)
    print(f"valeur projetée = {TOTAL}")
elif args.action == 'lister':
    if args.graphique:
        data = bourse.données_bourse('goog', args.date, date.today())
        portefeuille.lister_graph(args.date, date.today())
    titles = portefeuille.titres(args.date)
    for symbole, qty in titles.items():
        montant = qty * bourse.prix(symbole, args.date)
        print(f"{symbole} = {qty} x {bourse.prix(symbole, args.date)} = {montant}")
