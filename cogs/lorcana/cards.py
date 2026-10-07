import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CARD_FILE = PROJECT_ROOT / "data" / "lorcana_cards.json"


class LorcanaCardDatabase:

    def __init__(self):
        self.cards = []
        self.cards_by_id = {}

        self.load()

    def load(self):
        if not CARD_FILE.exists():
            print("Lorcana database bestaat nog niet.")
            self.cards = []
            self.cards_by_id = {}
            return

        with open(CARD_FILE, "r", encoding="utf-8") as file:
            self.cards = json.load(file)

        self.cards_by_id = {
            card["id"]: card
            for card in self.cards
            if card.get("id")
        }

        print(
            f"Lorcana database geladen: "
            f"{len(self.cards)} kaarten"
        )

    def get_card(self, card_id):
        return self.cards_by_id.get(card_id)

    def search(self, query, limit=25):
        query = query.lower().strip()

        if not query:
            return []

        results = []
        seen = set()

        for card in self.cards:
            name = (card.get("name") or "").lower()
            version = (card.get("version") or "").lower()
            full_name = (card.get("full_name") or "").lower()

            if query in name or query in version or query in full_name:
                unique_key = (
                    card.get("name"),
                    card.get("version")
                )

                if unique_key in seen:
                    continue

                seen.add(unique_key)
                results.append(card)

                if len(results) >= limit:
                    break

        return results

    def get_by_name(self, name):
        name = name.lower().strip()

        for card in self.cards:
            if card.get("full_name", "").lower() == name:
                return card

        return None

    def get_by_ink(self, ink):
        ink = ink.lower()

        return [
            card
            for card in self.cards
            if (card.get("ink") or "").lower() == ink
        ]

    def get_card_count(self):
        return len(self.cards)


lorcana_db = LorcanaCardDatabase()