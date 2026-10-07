import json
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


BASE_URL = "https://api.lorcast.com/v0"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_FILE = DATA_DIR / "lorcana_cards.json"


def get_json(url):
    request = Request(
        url,
        headers={
            "User-Agent": "Krentenbot/1.0"
        }
    )

    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    except HTTPError as e:
        print(f"HTTP fout {e.code}: {url}")
        return None

    except URLError as e:
        print(f"Verbindingsfout: {e.reason}")
        return None


def get_sets():
    print("Sets ophalen...")

    data = get_json(f"{BASE_URL}/sets")

    if not data:
        return []

    return data.get("results", [])


def get_cards_for_set(set_code):
    print(f"  Kaarten ophalen uit set {set_code}...")

    url = f"{BASE_URL}/sets/{set_code}/cards"
    data = get_json(url)

    if not data:
        return []

    return data


def simplify_card(card):
    """
    Alleen de gegevens bewaren die we voor onze deckbuilder nodig hebben.
    """

    return {
        "id": card.get("id"),

        "name": card.get("name"),
        "version": card.get("version"),

        "full_name": (
            f"{card.get('name')} - {card.get('version')}"
            if card.get("version")
            else card.get("name")
        ),

        "ink": card.get("ink"),
        "inkable": card.get("inkwell"),

        "cost": card.get("cost"),

        "type": card.get("type", []),
        "classifications": card.get("classifications") or [],

        "text": card.get("text", ""),
        "keywords": card.get("keywords", []),

        "strength": card.get("strength"),
        "willpower": card.get("willpower"),
        "lore": card.get("lore"),
        "move_cost": card.get("move_cost"),

        "rarity": card.get("rarity"),

        "collector_number": card.get("collector_number"),

        "set": {
            "id": card.get("set", {}).get("id"),
            "code": card.get("set", {}).get("code"),
            "name": card.get("set", {}).get("name")
        },

        "released_at": card.get("released_at"),

        "legalities": card.get("legalities", {}),

        "image": (
            card.get("image_uris", {})
            .get("digital", {})
            .get("normal")
        )
    }


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    sets = get_sets()

    if not sets:
        print("Geen sets gevonden.")
        return

    print(f"{len(sets)} sets gevonden.\n")

    all_cards = []

    for index, lorcana_set in enumerate(sets, start=1):
        set_code = lorcana_set.get("code")
        set_name = lorcana_set.get("name")

        print(f"[{index}/{len(sets)}] {set_name} ({set_code})")

        cards = get_cards_for_set(set_code)

        for card in cards:
            # Alleen Engelse kaarten gebruiken
            if card.get("lang") != "en":
                continue

            all_cards.append(simplify_card(card))

        # Lorcast vraagt om een kleine pauze tussen requests.
        time.sleep(0.1)

    # Sorteren voor een nette JSON
    all_cards.sort(
        key=lambda card: (
            card["name"] or "",
            card["version"] or ""
        )
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            all_cards,
            file,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("--------------------------------")
    print("Lorcana database bijgewerkt!")
    print(f"Kaarten: {len(all_cards)}")
    print(f"Bestand: {OUTPUT_FILE}")
    print("--------------------------------")


if __name__ == "__main__":
    main()