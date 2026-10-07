def get_card_effects(card):
    text = (card.get("text") or "").lower()
    keywords = card.get("keywords") or []

    if isinstance(keywords, list):
        keywords = " ".join(keywords).lower()
    else:
        keywords = str(keywords).lower()

    content = f"{text} {keywords}"

    effects = {
        "draw": False,
        "removal": False,
        "damage": False,
        "lore": False,
        "ramp": False,
        "discard": False,
        "bounce": False,
        "exert": False
    }

    # Card draw
    if any(word in content for word in [
        "draw a card",
        "draw 2 cards",
        "draw cards",
        "draw that many"
    ]):
        effects["draw"] = True

    # Removal / banish
    if any(word in content for word in [
        "banish",
        "banished"
    ]):
        effects["removal"] = True

    # Damage
    if any(word in content for word in [
        "deal damage",
        "deals damage",
        "damage to"
    ]):
        effects["damage"] = True

    # Lore
    if any(word in content for word in [
        "gain lore",
        "gains lore",
        "additional lore",
        "gain +"
    ]):
        effects["lore"] = True

    # Ramp
    if any(word in content for word in [
        "put into your inkwell",
        "put a card into your inkwell",
        "inkwell"
    ]):
        effects["ramp"] = True

    # Discard
    if any(word in content for word in [
        "discard a card",
        "discard cards",
        "discards a card"
    ]):
        effects["discard"] = True

    # Return to hand
    if any(word in content for word in [
        "return to their hand",
        "return to your hand",
        "return a character"
    ]):
        effects["bounce"] = True

    # Exert
    if "exert" in content:
        effects["exert"] = True

    return effects

def get_deck_checks(
    total_cards,
    inkable,
    uninkable,
    total_lore,
    effect_counts,
    cost_counts
):
    checks = []

    # Deck size
    if total_cards == 60:
        checks.append(("good", "Deck heeft precies 60 kaarten."))
    elif total_cards < 60:
        checks.append(("warning", f"Deck heeft nog maar {total_cards}/60 kaarten."))
    else:
        checks.append(("bad", "Deck bevat meer dan 60 kaarten."))

    # Inkable ratio
    if total_cards > 0:
        inkable_ratio = inkable / total_cards

        if inkable_ratio >= 0.65:
            checks.append(("good", "Goede hoeveelheid inkable kaarten."))
        elif inkable_ratio >= 0.55:
            checks.append(("warning", "Inkable ratio is aan de lage kant."))
        else:
            checks.append(("bad", "Er zijn relatief weinig inkable kaarten."))

    # Card draw
    if effect_counts["draw"] >= 8:
        checks.append(("good", "Goede hoeveelheid card draw."))
    elif effect_counts["draw"] >= 4:
        checks.append(("warning", "Je hebt wat card draw, maar niet heel veel."))
    else:
        checks.append(("bad", "Weinig card draw."))

    # Removal
    if effect_counts["removal"] >= 6:
        checks.append(("good", "Goede hoeveelheid removal."))
    elif effect_counts["removal"] >= 3:
        checks.append(("warning", "Redelijke hoeveelheid removal."))
    else:
        checks.append(("bad", "Weinig removal."))

    # Lore
    if total_lore >= 80:
        checks.append(("good", "Sterke hoeveelheid potentiële lore."))
    elif total_lore >= 50:
        checks.append(("warning", "Redelijke hoeveelheid lore."))
    else:
        checks.append(("bad", "Weinig potentiële lore."))

    # High-cost cards
    high_cost = sum(
        amount
        for cost, amount in cost_counts.items()
        if cost >= 6
    )

    if high_cost <= 6:
        checks.append(("good", "Niet te veel dure kaarten."))
    elif high_cost <= 10:
        checks.append(("warning", "Je hebt redelijk wat dure kaarten."))
    else:
        checks.append(("bad", "Veel kaarten kosten 6+ ink."))

    return checks

def get_deck_score(
    total_cards,
    inkable,
    total_lore,
    effect_counts,
    cost_counts
):
    if total_cards == 0:
        return 0

    score = 0

    # =========================
    # Deck size — 20 punten
    # =========================

    size_ratio = min(total_cards / 60, 1)

    score += int(size_ratio * 20)

    # =========================
    # Inkable — 15 punten
    # =========================

    inkable_ratio = inkable / total_cards

    if inkable_ratio >= 0.65:
        score += 15
    elif inkable_ratio >= 0.55:
        score += 12
    elif inkable_ratio >= 0.45:
        score += 8
    elif inkable_ratio >= 0.35:
        score += 4

    # =========================
    # Card Draw — 15 punten
    # =========================

    draw_ratio = effect_counts["draw"] / total_cards

    if draw_ratio >= 0.15:
        score += 15
    elif draw_ratio >= 0.10:
        score += 12
    elif draw_ratio >= 0.07:
        score += 8
    elif draw_ratio >= 0.04:
        score += 4

    # =========================
    # Removal — 15 punten
    # =========================

    removal_ratio = effect_counts["removal"] / total_cards

    if removal_ratio >= 0.15:
        score += 15
    elif removal_ratio >= 0.10:
        score += 12
    elif removal_ratio >= 0.07:
        score += 8
    elif removal_ratio >= 0.04:
        score += 4

    # =========================
    # Lore — 15 punten
    # =========================

    lore_per_card = total_lore / total_cards

    if lore_per_card >= 1.7:
        score += 15
    elif lore_per_card >= 1.4:
        score += 12
    elif lore_per_card >= 1.1:
        score += 9
    elif lore_per_card >= 0.8:
        score += 5
    elif lore_per_card >= 0.5:
        score += 2

    # =========================
    # Curve — 20 punten
    # =========================

    low_cost = sum(
        amount
        for cost, amount in cost_counts.items()
        if cost <= 2
    )

    high_cost = sum(
        amount
        for cost, amount in cost_counts.items()
        if cost >= 6
    )

    low_ratio = low_cost / total_cards
    high_ratio = high_cost / total_cards

    # Goed aantal goedkope kaarten
    if low_ratio >= 0.30:
        score += 10
    elif low_ratio >= 0.20:
        score += 7
    elif low_ratio >= 0.10:
        score += 4

    # Niet te veel dure kaarten
    if high_ratio <= 0.10:
        score += 10
    elif high_ratio <= 0.20:
        score += 7
    elif high_ratio <= 0.30:
        score += 4

    return min(score, 100)