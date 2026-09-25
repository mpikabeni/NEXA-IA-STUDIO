from datetime import datetime, timezone

from config import (
    DAILY_FREE_CREDITS,
    CREDIT_PACK_AMOUNT,
)
from database import (
    SessionLocal,
    User,
    add_credits,
    remove_credits,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def refresh_daily_credits(user: User) -> int:
    """
    Vérifie si le quota quotidien doit être renouvelé.

    Important :
    les crédits achetés ne sont pas séparés dans cette première
    version. Le système remet le solde à 100 chaque nouveau jour.
    """

    now = utc_now()

    last_reset = user.last_credit_reset

    if last_reset is None:
        needs_reset = True
    else:
        needs_reset = (
            last_reset.date() != now.date()
        )

    if not needs_reset:
        return user.credits

    with SessionLocal() as session:

        db_user = session.get(User, user.id)

        if db_user is None:
            return 0

        db_user.credits = DAILY_FREE_CREDITS
        db_user.last_credit_reset = now

        session.commit()

        return db_user.credits


def get_balance(telegram_id: int) -> int:
    """
    Retourne le solde actuel après vérification
    du renouvellement quotidien.
    """

    with SessionLocal() as session:

        user = (
            session.query(User)
            .filter(
                User.telegram_id == telegram_id
            )
            .first()
        )

        if user is None:
            return 0

        now = utc_now()

        if (
            user.last_credit_reset is None
            or user.last_credit_reset.date()
            != now.date()
        ):
            user.credits = DAILY_FREE_CREDITS
            user.last_credit_reset = now

            session.commit()

        return user.credits


def has_enough_credits(
    telegram_id: int,
    required: int,
) -> bool:

    if required <= 0:
        return True

    balance = get_balance(telegram_id)

    return balance >= required


def spend_credits(
    telegram_id: int,
    amount: int,
) -> bool:

    if amount <= 0:
        return False

    # Vérifie d'abord le renouvellement.
    get_balance(telegram_id)

    return remove_credits(
        telegram_id,
        amount,
    )


def purchase_credit_pack(
    telegram_id: int,
) -> int:

    """
    Ajoute le pack acheté.

    Cette fonction doit être appelée UNIQUEMENT
    après confirmation du paiement Telegram Stars.
    """

    return add_credits(
        telegram_id,
        CREDIT_PACK_AMOUNT,
    )


def credits_message(
    telegram_id: int,
) -> str:

    balance = get_balance(telegram_id)

    return (
        "💎 <b>NEXA AI STUDIO</b>\n\n"
        f"Crédits disponibles : <b>{balance}</b>\n\n"
        f"🎁 Quota quotidien : "
        f"<b>{DAILY_FREE_CREDITS}</b>\n"
        f"⭐ Pack supplémentaire : "
        f"<b>{CREDIT_PACK_AMOUNT} crédits</b>"
    )
