from dotenv import load_dotenv
from typesafe_sdk import TypeSafeClient, Noul, Score, Choice

load_dotenv()


def triage_ticket(message):

    urgency_rubric = [
        "A general question or minor inconvenience. The employee explicitly "
        "reports that normal work can continue without meaningful disruption.",

        "An issue disrupts a task, but an available workaround lets the employee "
        "continue working. Timely attention is needed without immediate critical impact.",

        "Essential work is explicitly blocked with no available workaround, "
        "ongoing data loss is reported, or an immediate deadline cannot be met "
        "because of the issue.",
    ]

    with TypeSafeClient() as client:
        response = client.system_one(
            state={
                "message": message,
                "urgency_rubric": urgency_rubric,
            },
            questions={
                "category": Choice(
                    instructions="Which internal IT support category best matches the primary issue reported by the employee?",
                    criteria={
                        "hardware": "Physical equipment, power, displays, and peripherals", 
                        "identity_and_access": "Sign-in, passwords, MFA/2FA, and permissions",
                        "network": "Wi-Fi, wired connectivity, VPN, and network reachability",
                        "software": "Application installation, crashes, updates, and functionality",
                        "other": "The issue does not fit the categories above.",
                    }
                ), 
                "urgency": Score(
                    instructions=(
                        "How urgently does the issue in `message` need attention? "
                        "Assess only reported facts. Do not assume an unstated deadline, "
                        "workaround, or complete work blockage. When information is "
                        "insufficient, this score is provisional."
                    ),
                    criteria=urgency_rubric,
                ),
                "missing_routing_info": Noul(
                    instructions="Does the employee's message lack enough information to choose an initial IT support category? Answer yes when the affected equipment, service, or symptom is too unclear to route. Missing troubleshooting details alone do not count if the initial support category is clear."
                ),
                "missing_urgency_info": Noul(
                    instructions=(
                        "Does `message` lack enough information to assess urgency using "
                        "`urgency_rubric`? Answer yes when missing details about work impact, "
                        "workarounds, or timing prevent distinguishing the levels. "
                        "Do not require every detail if the reported facts already establish "
                        "a level. An explicit working backup method that allows continued "
                        "work is sufficient to establish the workaround level unless other "
                        "reported facts make urgency unclear."
                    ),
                ),
                "clarifying_question": Choice(
                    instructions=(
                        "Select the single most useful follow-up question for the employee's "
                        "message using the shared urgency rubric. Prioritize identifying the affected "
                        "device or service when routing is unclear. Otherwise, select a question that "
                        "resolves missing urgency information. Do not ask for information already provided. " 
                        "Select none when enough information exists to route and assess urgency."
                    ),
                    criteria={
                        "affected_system": "Which device, application, or service is affected?",
                        "work_impact": "What work is this preventing you from doing?",
                        "workaround": "Is there another way you can continue working?",
                        "deadline": "Is there a deadline this issue puts at risk?",
                        "none": "No clarification needed"
                    }
                )
            },
        )

    category = response.choices["category"].choice
    confidence = response.choices["category"].confidence
    urgency = response.scores["urgency"].score
    missing_routing_info = response.nouls["missing_routing_info"].noul
    missing_urgency_info = response.nouls["missing_urgency_info"].noul
    clarifying_question = response.choices["clarifying_question"].choice

    teams = {
        "hardware": "Hardware Support",
        "identity_and_access": "Account Support",
        "network": "Network Support",
        "software": "Application Support",
        "other": "General Support",
    }

    assigned_team = teams[category]

    if confidence < 0.8 or missing_routing_info >= 0.7:
        needs_review = True
    else: 
        needs_review = False

    return {
        "category": category, 
        "confidence": confidence,
        "assigned_team": assigned_team,
        "urgency": urgency,
        "needs_review": needs_review,
        "missing_routing_info": missing_routing_info,
        "missing_urgency_info": missing_urgency_info,
        "clarifying_question": clarifying_question
    }
