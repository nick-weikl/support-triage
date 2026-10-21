import json
from pathlib import Path

from triage import triage_ticket

with open("data/eval_test.json", "r", encoding="utf-8") as file:
    ticket_list = json.load(file)

threshold = 0.7

category_correct = 0
category_count = 0

urgency_difference_total = 0
urgency_count = 0

routing_info_correct = 0
urgency_info_correct = 0
review_count = 0

evaluated_tickets = []

for ticket in ticket_list:
    result = triage_ticket(ticket["message"])

    predicted_missing_routing = (
        result["missing_routing_info"] >= threshold
    )
    predicted_missing_urgency = (
        result["missing_urgency_info"] >= threshold
    )

    category_matches = None
    if ticket["expected_category"] is not None:
        category_count += 1
        category_matches = (
            result["category"] == ticket["expected_category"]
        )
        category_correct += int(category_matches)

    urgency_difference = None
    if ticket["expected_urgency"] is not None:
        urgency_count += 1
        urgency_difference = abs(
            result["urgency"] - ticket["expected_urgency"]
        )
        urgency_difference_total += urgency_difference

    routing_matches = (
        predicted_missing_routing
        == ticket["expected_missing_routing_info"]
    )
    urgency_info_matches = (
        predicted_missing_urgency
        == ticket["expected_missing_urgency_info"]
    )

    routing_info_correct += int(routing_matches)
    urgency_info_correct += int(urgency_info_matches)
    review_count += int(result["needs_review"])

    evaluated_tickets.append({
        **ticket,
        "predicted_category": result["category"],
        "assigned_team": result["assigned_team"],
        "predicted_urgency": result["urgency"],
        "confidence": result["confidence"],
        "needs_review": result["needs_review"],
        "missing_routing_info": result["missing_routing_info"],
        "missing_urgency_info": result["missing_urgency_info"],
        "predicted_missing_routing_info": predicted_missing_routing,
        "predicted_missing_urgency_info": predicted_missing_urgency,
        "category_matches": category_matches,
        "urgency_difference": urgency_difference,
        "routing_info_matches": routing_matches,
        "urgency_info_matches": urgency_info_matches,
    })

    print(
        f"{ticket['id']} | "
        f"Category: {result['category']} "
        f"(expected {ticket['expected_category']}) | "
        f"Urgency: {result['urgency']:.2f} "
        f"(expected {ticket['expected_urgency']}) | "
        f"Missing routing info: {predicted_missing_routing} "
        f"(expected {ticket['expected_missing_routing_info']}) | "
        f"Missing urgency info: {predicted_missing_urgency} "
        f"(expected {ticket['expected_missing_urgency_info']})"
    )

total = len(ticket_list)

print("\nEvaluation Summary")

if category_count:
    print(
        f"Category accuracy: {category_correct / category_count:.1%} "
        f"({category_count} eligible tickets)"
    )
else:
    print("Category accuracy: no eligible tickets")

if urgency_count:
    print(
        f"Average urgency difference: "
        f"{urgency_difference_total / urgency_count:.2f} "
        f"({urgency_count} eligible tickets)"
    )
else:
    print("Average urgency difference: no eligible tickets")

if total:
    print(
        f"Routing-clarification accuracy: "
        f"{routing_info_correct / total:.1%}"
    )
    print(
        f"Urgency-clarification accuracy: "
        f"{urgency_info_correct / total:.1%}"
    )
    print(f"Flagged for routing review: {review_count}/{total}")
else:
    print("No tickets to evaluate.")

output_path = Path("data/evaluation_results.json")
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", encoding="utf-8") as file:
    json.dump(evaluated_tickets, file, indent=4)

print(f"Results saved to {output_path}")