import os
from dotenv import load_dotenv

load_dotenv()


def get_required(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Variable d'environnement manquante : {name}"
        )

    return value


# ==============================
# TELEGRAM
# ==============================

BOT_TOKEN = get_required("BOT_TOKEN")


# ==============================
# ADMIN NEXA
# ==============================

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))


# ==============================
# DATABASE
# ==============================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///nexa_ai_studio.db"
)


# ==============================
# AI PROVIDERS
# ==============================

# OpenAI - génération d'images
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Google Gemini / Veo - génération vidéo
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Runway - vidéo
RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY", "")

# fal.ai - accès à différents modèles
FAL_KEY = os.getenv("FAL_KEY", "")


# ==============================
# CRÉDITS
# ==============================

DAILY_FREE_CREDITS = 100

# Prix du pack supplémentaire
CREDIT_PACK_STARS = 10

# Nombre de crédits obtenus avec le pack
CREDIT_PACK_AMOUNT = 100


# ==============================
# COÛT DES GÉNÉRATIONS
# ==============================

IMAGE_COST = 5

IMAGE_EDIT_COST = 5

IMAGE_VARIATION_COST = 5

IMAGE_TO_VIDEO_COST = 15

TEXT_TO_VIDEO_COST = 20


# ==============================
# APPLICATION
# ==============================

APP_NAME = "NEXA AI STUDIO"

APP_VERSION = "1.0.0"

APP_AUTHOR = "NEXA"


# ==============================
# LIMITES
# ==============================

MAX_PROMPT_LENGTH = 4000

MAX_HISTORY_ITEMS = 50


# ==============================
# VÉRIFICATION
# ==============================

def show_config_status():
    """Affiche uniquement l'état des configurations.
    Les clés secrètes ne sont jamais affichées.
    """

    providers = {
        "OpenAI": bool(OPENAI_API_KEY),
        "Gemini": bool(GEMINI_API_KEY),
        "Runway": bool(RUNWAY_API_KEY),
        "fal.ai": bool(FAL_KEY),
    }

    print("=" * 45)
    print(f"{APP_NAME} v{APP_VERSION}")
    print(f"Créé par {APP_AUTHOR}")
    print("=" * 45)

    print(f"Telegram : {'OK' if BOT_TOKEN else 'MANQUANT'}")
    print(f"Admin    : {'OK' if ADMIN_ID else 'NON CONFIGURÉ'}")

    for name, status in providers.items():
        print(f"{name:<10}: {'OK' if status else 'NON CONFIGURÉ'}")

    print("-" * 45)
    print(f"Crédits gratuits : {DAILY_FREE_CREDITS}")
    print(
        f"Pack : {CREDIT_PACK_AMOUNT} crédits "
        f"pour {CREDIT_PACK_STARS} ⭐"
    )
    print("=" * 45)
