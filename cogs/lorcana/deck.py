import discord
from discord.ext import commands
from discord import app_commands

from cogs.lorcana import cards
from cogs.lorcana.cards import lorcana_db

from cogs.lorcana.analysis import (
    get_card_effects,
    get_deck_checks,
    get_deck_score
)

from cogs.lorcana.suggestions import get_deck_suggestions

from database import (
    create_lorcana_deck,
    delete_lorcana_deck,
    get_lorcana_deck,
    get_lorcana_deck_cards,
    get_lorcana_deck_card,
    get_lorcana_deck_card_count,
    add_lorcana_deck_card,
    remove_lorcana_deck_card
)

class DeleteDeckView(discord.ui.View):
    def __init__(self, deck_id):
        super().__init__(timeout=30)
        self.deck_id = deck_id

    @discord.ui.button(
        label="Ja, verwijderen",
        style=discord.ButtonStyle.danger
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        delete_lorcana_deck(self.deck_id)

        await interaction.response.edit_message(
            content="Je deck is verwijderd.",
            view=None
        )

    @discord.ui.button(
        label="Annuleren",
        style=discord.ButtonStyle.secondary
    )
    async def cancel(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            content="Verwijderen geannuleerd.",
            view=None
        )

class Deck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    lordeck = app_commands.Group(
        name="lordeck",
        description="Bouw en beheer je Lorcana deck"
    )

    @lordeck.command(name="nieuw", description="Maak een nieuw Lorcana deck")
    @app_commands.describe(
        naam="De naam van je deck",
        kleur1="Eerste ink-kleur",
        kleur2="Tweede ink-kleur"
    )
    @app_commands.choices(
        kleur1=[
            app_commands.Choice(name="Amber", value="Amber"),
            app_commands.Choice(name="Amethyst", value="Amethyst"),
            app_commands.Choice(name="Emerald", value="Emerald"),
            app_commands.Choice(name="Ruby", value="Ruby"),
            app_commands.Choice(name="Sapphire", value="Sapphire"),
            app_commands.Choice(name="Steel", value="Steel"),
        ],
        kleur2=[
            app_commands.Choice(name="Amber", value="Amber"),
            app_commands.Choice(name="Amethyst", value="Amethyst"),
            app_commands.Choice(name="Emerald", value="Emerald"),
            app_commands.Choice(name="Ruby", value="Ruby"),
            app_commands.Choice(name="Sapphire", value="Sapphire"),
            app_commands.Choice(name="Steel", value="Steel"),
        ]
    )

# =========================
# NIEUW FUNCTION
# =========================    

    async def nieuw(
        self,
        interaction: discord.Interaction,
        naam: str,
        kleur1: app_commands.Choice[str],
        kleur2: app_commands.Choice[str]
    ):
        if kleur1.value == kleur2.value:
            await interaction.response.send_message(
                "Je moet twee verschillende ink-kleuren kiezen.",
                ephemeral=True
            )
            return

        existing_deck = get_lorcana_deck(interaction.user.id)

        if existing_deck:
            await interaction.response.send_message(
                "Je hebt al een Lorcana deck. "
                "Gebruik eerst `/deck clear` of verwijder je huidige deck.",
                ephemeral=True
            )
            return

        create_lorcana_deck(
            interaction.user.id,
            naam,
            kleur1.value,
            kleur2.value
        )

        await interaction.response.send_message(
            f"**{naam}** aangemaakt!\n"
            f"Inkcolors: `{kleur1.value}/{kleur2.value}`\n"
        )

# =========================
# BEKIJK FUNCTION
# =========================

    @lordeck.command(name="bekijken", description="Bekijk je huidige Lorcana deck")
    async def bekijken(self, interaction: discord.Interaction):
        deck = get_lorcana_deck(interaction.user.id)

        if not deck:
            await interaction.response.send_message(
                "Je hebt nog geen deck. Gebruik eerst `/lordeck nieuw`.",
                ephemeral=True
            )
            return

        deck_id = deck[0]
        deck_name = deck[2]
        ink1 = deck[3]
        ink2 = deck[4]

        deck_cards = get_lorcana_deck_cards(deck_id)
        total_cards = sum(quantity for _, quantity in deck_cards)

        embed = discord.Embed(
            title=f"Bekijken - `{deck_name}`",
            description=(
                f"**{ink1}/{ink2}** • **{total_cards}/60 kaarten**"
            ),
            color=discord.Color.blue()
        )

        if not deck_cards:
            embed.add_field(
                name="Deck is leeg",
                value="Gebruik `/lordeck add` om kaarten toe te voegen.",
                inline=False
            )

            await interaction.response.send_message(embed=embed)
            return

        cards = []

        inkable = 0
        uninkable = 0

        for card_id, quantity in deck_cards:
            card = lorcana_db.get_card(card_id)

            if not card:
                continue

            cards.append((card, quantity))

            if card.get("inkable"):
                inkable += quantity
            else:
                uninkable += quantity

        embed.add_field(
            name="Deck Info",
            value=(
                f"Inkable: `{inkable}`\n"
                f"Uninkable: `{uninkable}`"
            ),
            inline=True
        )

        cards.sort(
            key=lambda x: (
                x[0].get("cost") or 0,
                x[0].get("full_name") or ""
            )
        )

        costs = {}

        for card, quantity in cards:
            cost = card.get("cost") or 0

            if cost not in costs:
                costs[cost] = []

            costs[cost].append(
                f"`{quantity}x` {card['full_name']}"
            )

        for cost in sorted(costs):
            embed.add_field(
                name=f"{cost} Ink",
                value="\n".join(costs[cost]),
                inline=False
            )

        await interaction.response.send_message(embed=embed)

# =========================
# DELETE FUNCTION
# =========================

    @lordeck.command(name="delete", description="Verwijder je huidige Lorcana deck")
    async def delete(self, interaction: discord.Interaction):
        deck = get_lorcana_deck(interaction.user.id)

        if not deck:
            await interaction.response.send_message(
                "Je hebt geen deck om te verwijderen.",
                ephemeral=True
            )
            return

        deck_id = deck[0]
        deck_name = deck[2]

        await interaction.response.send_message(
            f"Weet je zeker dat je **{deck_name}** wilt verwijderen?",
            view=DeleteDeckView(deck_id),
            ephemeral=True
        )

# =========================
# AUTOCOMPLETE FUNCTION
# =========================

    async def card_autocomplete(
            self,
            interaction: discord.Interaction,
            current: str
        ):
            results = lorcana_db.search(current, limit=25)

            return [
                app_commands.Choice(
                    name=card["full_name"][:100],
                    value=card["full_name"][:100]
                )
                for card in results
            ]

# =========================
# ADD FUNCTION
# =========================

    @lordeck.command(name="add", description="Voeg een kaart toe aan je deck")
    @app_commands.describe(
        kaart="Naam van de kaart",
        aantal="Aantal kaarten om toe te voegen"
    )
    @app_commands.autocomplete(kaart=card_autocomplete)
    async def add(
        self,
        interaction: discord.Interaction,
        kaart: str,
        aantal: app_commands.Range[int, 1, 4] = 1
    ):
        deck = get_lorcana_deck(interaction.user.id)

        if not deck:
            await interaction.response.send_message(
                "Je hebt nog geen deck. Gebruik eerst `/lordeck nieuw`.",
                ephemeral=True
            )
            return

        results = lorcana_db.search(kaart, limit=10)

        if not results:
            await interaction.response.send_message(
                f"Ik kon geen kaart vinden voor **{kaart}**.",
                ephemeral=True
            )
            return

        if len(results) > 1:
            description = "\n".join(
                f"**{index}.** {card['full_name']} "
                f"({card['ink']}, {card['cost']} ink)"
                for index, card in enumerate(results, start=1)
            )

            embed = discord.Embed(
                title="Meerdere kaarten gevonden",
                description=description,
                color=discord.Color.blue()
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )
            return

        card = results[0]

        deck_id = deck[0]
        deck_name = deck[2]
        ink1 = deck[3]
        ink2 = deck[4]

        if card["ink"] not in (ink1, ink2):
            await interaction.response.send_message(
                f"**{card['full_name']}** is {card['ink']}, "
                f"maar je deck gebruikt **{ink1} / {ink2}**.",
                ephemeral=True
            )
            return

        card_count = get_lorcana_deck_card_count(deck_id)

        if card_count >= 60:
            await interaction.response.send_message(
                f"Je deck **{deck_name}** zit al op **60/60 kaarten**.",
                ephemeral=True
            )
            return

        existing = get_lorcana_deck_card(
            deck_id,
            card["id"]
        )

        current_quantity = existing[0] if existing else 0
        new_quantity = current_quantity + aantal

        if new_quantity > 4:
            await interaction.response.send_message(
                f"Je hebt al **{current_quantity}× {card['full_name']}**.\n"
                f"Je kunt nog maximaal **{4 - current_quantity}×** toevoegen.",
                ephemeral=True
            )
            return

        if card_count + aantal > 60:
            await interaction.response.send_message(
                f"Je kunt geen **{aantal}×** toevoegen.\n"
                f"Je deck zou dan boven de **60 kaarten** komen.",
                ephemeral=True
            )
            return

        for _ in range(aantal):
            add_lorcana_deck_card(
                deck_id,
                card["id"]
            )

        await interaction.response.send_message(
            f"**{aantal}× {card['full_name']}** toegevoegd!\n\n"
            f"Deck: `{deck_name}`\n"
            f"Kaarten: `{card_count + aantal}/60`\n"
            f"Aantal van deze kaart: `{new_quantity}/4`"
        )

# =========================
# REMOVE FUNCTION
# =========================

    @lordeck.command(name="remove", description="Verwijder een kaart uit je deck")
    @app_commands.describe(
        kaart="Naam van de kaart",
        aantal="Aantal kaarten om te verwijderen"
    )
    @app_commands.autocomplete(kaart=card_autocomplete)
    async def remove(
        self,
        interaction: discord.Interaction,
        kaart: str,
        aantal: app_commands.Range[int, 1, 4] = 1
    ):
        deck = get_lorcana_deck(interaction.user.id)

        if not deck:
            await interaction.response.send_message(
                "Je hebt nog geen deck. Gebruik `/lordeck nieuw`.",
                ephemeral=True
            )
            return

        deck_id = deck[0]

        results = lorcana_db.search(kaart, limit=10)

        if not results:
            await interaction.response.send_message(
                f"Ik kon geen kaart vinden voor **{kaart}**.",
                ephemeral=True
            )
            return

        if len(results) > 1:
            description = "\n".join(
                f"**{index}.** {card['full_name']} "
                f"({card['ink']}, {card['cost']} ink)"
                for index, card in enumerate(results, start=1)
            )

            embed = discord.Embed(
                title="Meerdere kaarten gevonden",
                description=description,
                color=discord.Color.blue()
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )
            return

        card = results[0]

        existing = get_lorcana_deck_card(
            deck_id,
            card["id"]
        )

        if not existing:
            await interaction.response.send_message(
                f"**{card['full_name']}** zit niet in je deck.",
                ephemeral=True
            )
            return

        current_quantity = existing[0]

        if aantal > current_quantity:
            await interaction.response.send_message(
                f"Je hebt maar **{current_quantity}× "
                f"{card['full_name']}** in je deck.",
                ephemeral=True
            )
            return

        for _ in range(aantal):
            remove_lorcana_deck_card(
                deck_id,
                card["id"]
            )

        remaining = current_quantity - aantal

        await interaction.response.send_message(
            f"**{aantal}× {card['full_name']}** verwijderd.\n\n"
            f"Resterend: **{remaining}×**"
        )

# =========================
# ANALYSE FUNCTION
# =========================

    @lordeck.command(name="analyse", description="Analyseer je huidige Lorcana deck")
    async def analyse(self, interaction: discord.Interaction):
        deck = get_lorcana_deck(interaction.user.id)

        if not deck:
            await interaction.response.send_message(
                "Je hebt nog geen deck. Gebruik eerst `/lordeck nieuw`.",
                ephemeral=True
            )
            return

        deck_id = deck[0]
        deck_name = deck[2]
        ink1 = deck[3]
        ink2 = deck[4]

        deck_cards = get_lorcana_deck_cards(deck_id)

        if not deck_cards:
            await interaction.response.send_message(
                "Je deck is nog leeg.",
                ephemeral=True
            )
            return

        total_cards = 0
        total_lore = 0
        inkable = 0
        uninkable = 0

        type_counts = {
            "Character": 0,
            "Action": 0,
            "Item": 0,
            "Location": 0
        }

        effect_counts = {
            "draw": 0,
            "removal": 0,
            "damage": 0,
            "lore": 0,
            "ramp": 0,
            "discard": 0,
            "bounce": 0,
            "exert": 0
        }

        cost_counts = {}

        for card_id, quantity in deck_cards:
            card = lorcana_db.get_card(card_id)

            if not card:
                continue

            effects = get_card_effects(card)

            for effect, has_effect in effects.items():
                if has_effect:
                    effect_counts[effect] += quantity

            lore = card.get("lore") or 0
            total_lore += lore * quantity
            total_cards += quantity

            if card.get("inkable"):
                inkable += quantity
            else:
                uninkable += quantity

            card_types = card.get("type", [])

            if isinstance(card_types, str):
                card_types = [card_types]

            for card_type in card_types:
                if card_type in type_counts:
                    type_counts[card_type] += quantity

            cost = card.get("cost") or 0
            cost_counts[cost] = cost_counts.get(cost, 0) + quantity

        curve_lines = []

        for cost in sorted(cost_counts):
            amount = cost_counts[cost]
            bar = "▰" * min(amount, 15)

            curve_lines.append(
                f"**{cost}** {bar} `{amount}`"
            )

        curve = "\n".join(curve_lines)

        deck_score = get_deck_score(
            total_cards,
            inkable,
            total_lore,
            effect_counts,
            cost_counts
        )
        
        checks = get_deck_checks(
            total_cards,
            inkable,
            uninkable,
            total_lore,
            effect_counts,
            cost_counts
        )

        check_lines = []
        
        for status, message in checks:
            if status == "good":
                icon = "✓"
            elif status == "warning":
                icon = "⚠"
            else:
                icon = "✗"

            check_lines.append(
                f"{icon} {message}"
            )

        embed = discord.Embed(
            title=f"Analyse - `{deck_name}`",
            description=f"**{ink1}/{ink2}** • **{total_cards}/60 kaarten**",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Ink",
            value=(
                f"Inkable: `{inkable}`\n"
                f"Uninkable: `{uninkable}`"
            ),
            inline=True
        )

        embed.add_field(
            name="Kaarttypes",
            value=(
                f"Characters: `{type_counts['Character']}`\n"
                f"Actions: `{type_counts['Action']}`\n"
                f"Items: `{type_counts['Item']}`\n"
                f"Locations: `{type_counts['Location']}`"
            ),
            inline=True
        )

        embed.add_field(
            name="Ink Curve",
            value=curve,
            inline=False
        )

        embed.add_field(
            name="Effecten",
            value=(
                f"Card Draw: `{effect_counts['draw']}`\n"
                f"Removal: `{effect_counts['removal']}`\n"
                f"Damage: `{effect_counts['damage']}`\n"
                f"Lore: `{effect_counts['lore']}`\n"
                f"Ramp: `{effect_counts['ramp']}`\n"
                f"Discard: `{effect_counts['discard']}`\n"
                f"Bounce: `{effect_counts['bounce']}`\n"
                f"Exert: `{effect_counts['exert']}`"
            ),
            inline=False
        )

        embed.add_field(
            name="Deck Score",
            value=f"**{deck_score}/100**",
            inline=False
        )

        embed.add_field(
            name="Deck Check",
            value="\n".join(check_lines),
            inline=False
        )

        await interaction.response.send_message(embed=embed)

# =========================
# FIND SUGGESTIONS FUNCTION
# =========================

    def find_suggestions(
        self,
        deck_cards,
        ink1,
        ink2,
        category,
        effect_counts,
        cost_counts,
        total_lore,
        limit=3
    ):
        owned = {
            card_id: quantity
            for card_id, quantity in deck_cards
        }

        candidates = []
        seen = set()

        for card in lorcana_db.cards:
            card_id = card.get("id")
            card_name = card.get("full_name") or card.get("name")

            if not card_id or not card_name or card_name in seen:
                continue

            if card.get("ink") not in (ink1, ink2):
                continue

            current_quantity = owned.get(card_id, 0)

            if current_quantity >= 4:
                continue

            cost = card.get("cost") or 0

            # Speciale/promokaarten zonder normale ink cost
            if cost <= 0:
                continue

            lore = card.get("lore") or 0

            text = (card.get("text") or "").lower()

            keywords = card.get("keywords") or []

            if isinstance(keywords, list):
                keywords = " ".join(
                    str(keyword) for keyword in keywords
                ).lower()
            else:
                keywords = str(keywords).lower()

            content = f"{text} {keywords}"

            score = 0

            # Hoe meer het deck iets nodig heeft,
            # hoe hoger de score voor die categorie.

            if category == "draw":
                if effect_counts["draw"] < 4:
                    score += 20
                elif effect_counts["draw"] < 7:
                    score += 10

            elif category == "removal":
                if effect_counts["removal"] < 4:
                    score += 20
                elif effect_counts["removal"] < 7:
                    score += 10

            elif category == "lore":
                if total_lore < 50:
                    score += 20
                elif total_lore < 80:
                    score += 10

            elif category == "curve":
                low_cost = sum(
                    amount
                    for cost, amount in cost_counts.items()
                    if cost <= 2
                )

                if low_cost < 15:
                    score += 20
                elif low_cost < 20:
                    score += 10

            elif category == "inkable":
                total_cards = sum(
                    quantity
                    for _, quantity in deck_cards
                )

                if total_cards > 0:
                    inkable_cards = sum(
                        quantity
                        for card_id, quantity in deck_cards
                        if lorcana_db.get_card(card_id)
                        and lorcana_db.get_card(card_id).get("inkable")
                    )

                    inkable_ratio = inkable_cards / total_cards

                    if inkable_ratio < 0.55:
                        score += 20
                    elif inkable_ratio < 0.65:
                        score += 10

            # ==========================================
            # CARD DRAW
            # ==========================================

            if category == "draw":

                if "draw a card" in content:
                    score += 20

                if "draw 2 cards" in content:
                    score += 30

                if "draw 3 cards" in content:
                    score += 40

                if "draw cards" in content:
                    score += 15

                # Goedkope draw is waardevoller
                if cost <= 2:
                    score += 10
                elif cost <= 4:
                    score += 5

                # Meerdere kopieën zijn nuttiger
                if current_quantity > 0:
                    score += 5

                if score == 0:
                    continue

            # ==========================================
            # REMOVAL
            # ==========================================

            elif category == "removal":

                if "banish chosen character" in content:
                    score += 35
                elif "banish an opposing character" in content:
                    score += 30
                elif "banish another character" in content:
                    score += 25
                elif "banish" in content:
                    score += 15

                # Goedkope removal is beter
                if cost <= 2:
                    score += 15
                elif cost <= 4:
                    score += 10
                elif cost <= 5:
                    score += 5

                # Directe removal heeft voorkeur
                if "chosen" in content:
                    score += 5

                if score == 0:
                    continue

            # ==========================================
            # LORE
            # ==========================================

            elif category == "lore":

                # Basis lore
                if lore >= 3:
                    score += 30
                elif lore == 2:
                    score += 20
                elif lore == 1:
                    score += 8

                # Lore via effect
                if "gain lore" in content:
                    score += 25

                if "gains lore" in content:
                    score += 25

                if "additional lore" in content:
                    score += 20

                # Goedkope lore is extra interessant
                if cost <= 2:
                    score += 15
                elif cost <= 4:
                    score += 8

                if score == 0:
                    continue

            # ==========================================
            # CURVE
            # ==========================================

            elif category == "curve":

                if cost == 1:
                    score += 30
                elif cost == 2:
                    score += 25
                else:
                    continue

                # Character is vaak nuttiger voor curve
                card_types = card.get("type", [])

                if isinstance(card_types, str):
                    card_types = [card_types]

                if "Character" in card_types:
                    score += 10

                if lore >= 1:
                    score += 5

            # ==========================================
            # EXPENSIVE
            # ==========================================

            elif category == "expensive":

                if cost <= 2:
                    score += 5
                elif cost <= 3:
                    score += 15
                elif cost <= 4:
                    score += 20
                else:
                    continue

                if lore >= 2:
                    score += 5

            # ==========================================
            # INKABLE
            # ==========================================

            elif category == "inkable":

                if not card.get("inkable"):
                    continue

                score += 20

                if cost <= 2:
                    score += 15
                elif cost <= 4:
                    score += 10

                if lore >= 1:
                    score += 5

            if score <= 0:
                continue

            candidates.append(
                (
                    score,
                    cost,
                    card.get("full_name", ""),
                    card
                )
            )

            seen.add(card_name)

        # Hoogste score eerst
        candidates.sort(
            key=lambda x: (
                -x[0],
                x[1],
                x[2]
            )
        )

        return [
            card
            for _, _, _, card in candidates[:limit]
        ]

# =========================
# SUGGESTIE FUNCTION
# =========================

    @lordeck.command(
        name="suggesties",
        description="Krijg suggesties voor je Lorcana deck"
    )
    async def suggest(self, interaction: discord.Interaction):
        deck = get_lorcana_deck(interaction.user.id)

        if not deck:
            await interaction.response.send_message(
                "Je hebt nog geen deck. Gebruik eerst `/lordeck nieuw`.",
                ephemeral=True
            )
            return

        deck_id = deck[0]
        deck_name = deck[2]
        ink1 = deck[3]
        ink2 = deck[4]

        deck_cards = get_lorcana_deck_cards(deck_id)

        if not deck_cards:
            await interaction.response.send_message(
                "Je deck is nog leeg.",
                ephemeral=True
            )
            return

        total_cards = 0
        inkable = 0
        total_lore = 0

        effect_counts = {
            "draw": 0,
            "removal": 0,
            "damage": 0,
            "lore": 0,
            "ramp": 0,
            "discard": 0,
            "bounce": 0,
            "exert": 0
        }

        cost_counts = {}

        for card_id, quantity in deck_cards:
            card = lorcana_db.get_card(card_id)

            if not card:
                continue

            total_cards += quantity

            if card.get("inkable"):
                inkable += quantity

            lore = card.get("lore") or 0
            total_lore += lore * quantity

            cost = card.get("cost") or 0
            cost_counts[cost] = cost_counts.get(cost, 0) + quantity

            effects = get_card_effects(card)

            for effect, has_effect in effects.items():
                if has_effect:
                    effect_counts[effect] += quantity

        suggestions = get_deck_suggestions(
            total_cards,
            inkable,
            total_lore,
            effect_counts,
            cost_counts
        )

        embed = discord.Embed(
            title=f"Suggesties - `{deck_name}`",
            description=f"**{ink1}/{ink2}** • **{total_cards}/60 kaarten**",
            color=discord.Color.blue()
        )

        if not suggestions:
            embed.add_field(
                name="Deck Check",
                value="Je deck heeft op basis van de huidige analyse geen duidelijke zwakke punten.",
                inline=False
            )
        else:
            for category in suggestions:
                cards = self.find_suggestions(
                    deck_cards,
                    ink1,
                    ink2,
                    category,
                    effect_counts,
                    cost_counts,
                    total_lore
                )

                if not cards:
                    continue

                names = "\n".join(
                    f"• **{card['full_name']}** "
                    f"({card.get('cost', '?')} ink)"
                    for card in cards
                )

                category_names = {
                    "draw": "Card Draw",
                    "removal": "Removal",
                    "curve": "Goedkopere kaarten",
                    "expensive": "Duurdere kaarten vervangen",
                    "lore": "Lore",
                    "inkable": "Inkable kaarten"
                }

                embed.add_field(
                    name=category_names.get(category, category),
                    value=names,
                    inline=False
                )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Deck(bot))