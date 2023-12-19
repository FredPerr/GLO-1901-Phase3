"""
Classe définissant les erreurs. 
"""


class ErreurDate(RuntimeError):
    """Erreur levée lorsque la date est postérieure à la date du jour."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class LiquiditéInsuffisante(RuntimeError):
    """Erreur levée lorsque la liquidité est insuffisante pour effectuer une transaction."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ErreurQuantité(RuntimeError):
    """Erreur levée lorsque la quantité d'actions à vendre est trop grande."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
