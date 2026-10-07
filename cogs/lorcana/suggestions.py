def get_deck_suggestions(
    total_cards,
    inkable,
    total_lore,
    effect_counts,
    cost_counts
):
    suggestions = []

    if effect_counts["draw"] < 4:
        suggestions.append("draw")

    if effect_counts["removal"] < 4:
        suggestions.append("removal")

    low_cost = sum(
        amount
        for cost, amount in cost_counts.items()
        if cost <= 2
    )

    if low_cost < 15:
        suggestions.append("curve")

    high_cost = sum(
        amount
        for cost, amount in cost_counts.items()
        if cost >= 6
    )

    if high_cost > 10:
        suggestions.append("expensive")

    if total_lore < 50:
        suggestions.append("lore")

    if total_cards > 0:
        if inkable / total_cards < 0.55:
            suggestions.append("inkable")

    # Als het deck nog niet vol is, geef altijd suggesties
    if not suggestions and total_cards < 60:
        suggestions.append("curve")

    return suggestions