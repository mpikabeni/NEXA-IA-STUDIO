from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from config import DATABASE_URL, DAILY_FREE_CREDITS


# ============================================================
# BASE
# ============================================================

class Base(DeclarativeBase):
    pass


# ============================================================
# UTILISATEURS
# ============================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    telegram_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        index=True,
        nullable=False,
    )

    username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    first_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Crédit gratuit disponible aujourd'hui
    daily_credits: Mapped[int] = mapped_column(
        Integer,
        default=DAILY_FREE_CREDITS,
        nullable=False,
    )

    # Crédits achetés avec Telegram Stars
    purchased_credits: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Date du dernier renouvellement
    last_credit_reset: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# ============================================================
# HISTORIQUE DES GÉNÉRATIONS
# ============================================================

class Generation(Base):
    __tablename__ = "generations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    telegram_id: Mapped[int] = mapped_column(
        Integer,
        index=True,
        nullable=False,
    )

    generation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    provider: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    result_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    credits_used: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# ============================================================
# ACHATS TELEGRAM STARS
# ============================================================

class StarPurchase(Base):
    __tablename__ = "star_purchases"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    telegram_id: Mapped[int] = mapped_column(
        Integer,
        index=True,
        nullable=False,
    )

    telegram_payment_charge_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    stars: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    credits_added: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# ============================================================
# DATABASE
# ============================================================

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# ============================================================
# INITIALISATION
# ============================================================

def init_database():
    Base.metadata.create_all(engine)


# ============================================================
# UTILISATEUR
# ============================================================

def get_or_create_user(
    telegram_id: int,
    username: str | None = None,
    first_name: str | None = None,
):

    with SessionLocal() as session:

        user = session.scalar(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        if user is None:

            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                daily_credits=DAILY_FREE_CREDITS,
                purchased_credits=0,
            )

            session.add(user)
            session.commit()
            session.refresh(user)

        else:

            user.username = username
            user.first_name = first_name

            session.commit()
            session.refresh(user)

        return user


# ============================================================
# RÉCUPÉRER UN UTILISATEUR
# ============================================================

def get_user(telegram_id: int):

    with SessionLocal() as session:

        return session.scalar(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )


# ============================================================
# AJOUTER DES CRÉDITS ACHETÉS
# ============================================================

def add_purchased_credits(
    telegram_id: int,
    amount: int,
):

    if amount <= 0:
        raise ValueError(
            "Le nombre de crédits doit être positif."
        )

    with SessionLocal() as session:

        user = session.scalar(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        if user is None:
            raise ValueError(
                "Utilisateur introuvable."
            )

        user.purchased_credits += amount

        session.commit()

        return user.purchased_credits


# ============================================================
# CALCUL DU SOLDE TOTAL
# ============================================================

def get_total_credits(
    telegram_id: int,
):

    with SessionLocal() as session:

        user = session.scalar(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        if user is None:
            return 0

        return (
            user.daily_credits
            + user.purchased_credits
        )


# ============================================================
# DÉDUIRE DES CRÉDITS
# ============================================================

def remove_credits(
    telegram_id: int,
    amount: int,
):

    if amount <= 0:
        return False

    with SessionLocal() as session:

        user = session.scalar(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        if user is None:
            return False

        total = (
            user.daily_credits
            + user.purchased_credits
        )

        if total < amount:
            return False

        # On utilise d'abord les crédits gratuits.
        from_daily = min(
            user.daily_credits,
            amount,
        )

        user.daily_credits -= from_daily

        remaining = amount - from_daily

        # Puis les crédits achetés.
        if remaining > 0:
            user.purchased_credits -= remaining

        session.commit()

        return True


# ============================================================
# HISTORIQUE
# ============================================================

def save_generation(
    telegram_id: int,
    generation_type: str,
    prompt: str,
    credits_used: int,
    provider: str | None = None,
    result_url: str | None = None,
    status: str = "completed",
):

    with SessionLocal() as session:

        generation = Generation(
            telegram_id=telegram_id,
            generation_type=generation_type,
            prompt=prompt,
            provider=provider,
            result_url=result_url,
            credits_used=credits_used,
            status=status,
        )

        session.add(generation)
        session.commit()

        return generation.id


# ============================================================
# PAIEMENT STARS
# ============================================================

def save_star_purchase(
    telegram_id: int,
    charge_id: str,
    stars: int,
    credits_added: int,
):

    with SessionLocal() as session:

        existing = session.scalar(
            select(StarPurchase).where(
                StarPurchase.telegram_payment_charge_id
                == charge_id
            )
        )

        # Empêche un double crédit du même paiement.
        if existing is not None:
            return False

        purchase = StarPurchase(
            telegram_id=telegram_id,
            telegram_payment_charge_id=charge_id,
            stars=stars,
            credits_added=credits_added,
        )

        session.add(purchase)

        user = session.scalar(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        if user is None:
            return False

        user.purchased_credits += credits_added

        session.commit()

        return True


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    init_database()

    print(
        "✅ Base de données NEXA AI STUDIO initialisée."
    )
