from config import (
    CREDIT_PACK_AMOUNT,
    CREDIT_PACK_STARS,
)

from database import save_star_purchase


# ============================================================
# CONFIGURATION DU PRODUIT
# ============================================================

PRODUCT_ID = "nexa_credit_pack_100"

PRODUCT_TITLE = "💎 Pack 100 crédits"

PRODUCT_DESCRIPTION = (
    "Obtiens 100 crédits supplémentaires "
    "pour NEXA AI STUDIO."
)


# ============================================================
# PAYLOAD TELEGRAM
# ============================================================

def create_payload() -> str:
    """
    Payload unique permettant d'identifier
    le produit acheté.
    """

    return PRODUCT_ID


# ============================================================
# VALIDATION DU PAIEMENT
# ============================================================

def process_successful_payment(
    telegram_id: int,
    charge_id: str,
    stars: int,
) -> bool:
    """
    Traite un paiement Telegram Stars confirmé.

    Les crédits sont ajoutés uniquement ici,
    après successful_payment.
    """

    if stars != CREDIT_PACK_STARS:
        return False

    return save_star_purchase(
        telegram_id=telegram_id,
        charge_id=charge_id,
        stars=stars,
        credits_added=CREDIT_PACK_AMOUNT,
    )
