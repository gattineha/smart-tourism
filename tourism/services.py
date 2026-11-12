import calendar
from .models import Destination

# Documented weights (they add up to 1.0). Mention these in your report.
WEIGHTS = {
    "interest": 0.40,
    "budget": 0.30,
    "duration": 0.15,
    "season": 0.15,
}


def recommend_destinations(budget, days, month, interest_ids, people=1, limit=5):
    """
    budget       : budget per person in rupees
    days         : number of days the user has
    month        : travel month (1-12)
    interest_ids : list of Category ids the user likes
    Returns a ranked list of dictionaries, best first.
    """
    interest_ids = set(interest_ids)
    month_name = calendar.month_name[month]
    results = []

    destinations = Destination.objects.filter(is_active=True).select_related("category")

    for d in destinations:
        # ---------- STEP 1: hard rules (remove unsuitable places) ----------
        if days < d.min_days:
            continue                      # user has too few days

        trip_days = min(days, d.max_days)   # no point staying longer than the max
        cost = float(d.estimated_cost(trip_days))
        if cost > budget:
            continue                      # too expensive

        reasons = []

        # ---------- STEP 2: score each factor out of 100 ----------
        # Interest match
        if not interest_ids:
            interest_score = 50           # user chose nothing, so stay neutral
        elif d.category_id in interest_ids:
            interest_score = 100
            reasons.append(f"Matches your interest in {d.category.name}")
        else:
            interest_score = 0

        # Budget fit: cheaper than budget = higher score (100 at zero cost, 50 at full budget)
        ratio = cost / budget
        budget_score = 100 - ratio * 50
        reasons.append(f"Estimated Rs {cost:,.0f} per person, Rs {budget - cost:,.0f} within your budget")

        # Duration fit
        if d.min_days <= days <= d.max_days:
            duration_score = 100
            reasons.append(f"Your {days} day(s) fit the ideal {d.min_days}-{d.max_days} days")
        else:
            duration_score = max(0, 100 - 25 * (days - d.max_days))
            reasons.append(f"Best enjoyed in {d.min_days}-{d.max_days} days (planned for {trip_days})")

        # Season fit
        if month in d.best_months_list():
            season_score = 100
            reasons.append(f"{month_name} is a good time to visit")
        else:
            season_score = 40
            reasons.append(f"{month_name} is not the ideal season")

        # ---------- STEP 3: weighted total ----------
        total = (
            WEIGHTS["interest"] * interest_score
            + WEIGHTS["budget"] * budget_score
            + WEIGHTS["duration"] * duration_score
            + WEIGHTS["season"] * season_score
        )

        results.append({
            "destination": d,
            "score": round(total, 1),
            "trip_days": trip_days,
            "cost_per_person": cost,
            "cost_total": cost * people,
            "reasons": reasons,
        })

    # ---------- STEP 4: rank (highest score first, cheaper wins a tie) ----------
    results.sort(key=lambda r: (-r["score"], r["cost_per_person"]))
    return results[:limit]



    

def cost_breakdown(destination, days, people):
    """Splits the estimated cost into parts. Costs are per person; total is for the group."""
    transport = float(destination.transport_cost)
    stay = float(destination.stay_cost_per_day) * days
    food = float(destination.food_cost_per_day) * days
    activities = float(destination.activity_cost)
    per_person = transport + stay + food + activities
    return {
        "transport": transport,
        "stay": stay,
        "food": food,
        "activities": activities,
        "per_person": per_person,
        "total": per_person * people,
    }