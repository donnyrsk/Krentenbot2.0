from cogs.lorcana.cards import lorcana_db


print("Aantal kaarten:")
print(lorcana_db.get_card_count())

print()
print("Zoeken naar Cheshire:")

results = lorcana_db.search("Cheshire")

for card in results:
    print(
        f"{card['full_name']} | "
        f"{card['ink']} | "
        f"{card['cost']} ink | "
        f"Lore: {card['lore']}"
    )