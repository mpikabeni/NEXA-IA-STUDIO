from datetime import datetime, timezone

from config import (
    DAILY_FREE_CREDITS,
    CREDIT_PACK_AMOUNT,
)

from database import (
    SessionLocal,
    User,
    get_total_credits,
    remove_credits,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def refresh_daily_credits(telegram_id: int) -> int:
    """
    Renouvelle uniquement les crédits gratuits.

    Les crédits achetés sont conservés.
    """

    now = utc_now()

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

        last_reset = user.last_credit_reset

        # Nouveau jour
        if (
            last_reset is None
            or last_reset.date() != now.date()
        ):

            user.daily_credits = DAILY_FREE_CREDITS
            user.last_credit_reset = now

            session.commit()

        return (
            user.daily_credits
            + user.purchased_credits
        )


def get_balance(telegram_id: int) -> int:
    """
    Retourne le nombre total de crédits disponibles.
    """

    refresh_daily_credits(telegram_id)

    return get_total_credits(
        telegram_id
    )


def has_enough_credits(
    telegram_id: int,
    required: int,
) -> bool:

    if required <= 0:
        return True

    balance = get_balance(
        telegram_id
    )

    return balance >= required


def spend_credits(
    telegram_id: int,
    amount: int,
) -> bool:
    """
    Déduit les crédits gratuits en premier,
    puis les crédits achetés.
    """

    if amount <= 0:
        return False

    # Vérifie d'abord le nouveau jour.
    refresh_daily_credits(
        telegram_id
    )

    return remove_credits(
        telegram_id,
        amount,
    )


def get_credit_details(
    telegram_id: int,
):
    """
    Retourne le détail du portefeuille.
    """

    refresh_daily_credits(
        telegram_id
    )

    with SessionLocal() as session:

        user = (
            session.query(User)
            .filter(
                User.telegram_id == telegram_id
            )
            .first()
        )

        if user is None:
            return {
                "daily": 0,
                "purchased": 0,
                "total": 0,
            }

        return {
            "daily": user.daily_credits,
            "purchased": user.purchased_credits,
            "total": (
                user.daily_credits
                + user.purchased_credits
            ),
        }


def credits_message(
    telegram_id: int,
) -> str:

    data = get_credit_details(
        telegram_id
    )

    return (
        "💎 <b>NEXA AI STUDIO</b>\n\n"
        f"🎁 Crédits gratuits : "
        f"<b>{data['daily']}</b>\n"
        f"⭐ Crédits achetés : "
        f"<b>{data['purchased']}</b>\n"
        "━━━━━━━━━━━━━━\n"
        f"💎 Total : <b>{data['total']}</b>\n\n"
        f"🎁 Renouvellement : "
        f"<b>{DAILY_FREE_CREDITS}</b> crédits/jour\n"
        f"⭐ Pack : "
        f"<b>{CREDIT_PACK_AMOUNT} crédits</b> "
        f"pour <b>10 ⭐</b>"
    )
