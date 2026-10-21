import streamlit as st
from triage import triage_ticket
from storage import initialize_database, save_ticket, load_tickets, update_ticket

initialize_database()

st.title("Support Ticket Triage")

message = st.text_area("Report Issue")

if st.button("Analyze Ticket"):
    if message.strip():
        try:
            with st.spinner("Analyzing ticket..."):
                result = triage_ticket(message.strip())
                ticket_id = save_ticket(message.strip(), result)

        except Exception:
            st.error(
                "The ticket could not be analyzed or saved. "
                "Your message is still available above. Please try again."
            )

        else:
            st.session_state.latest_result = result
            st.session_state.original_message = message.strip()
            st.session_state.ticket_id = ticket_id
            st.session_state.follow_up_history = []

    else:
        st.warning("Please enter an issue before analyzing.")

if "latest_result" in st.session_state:
    result = st.session_state.latest_result

    st.subheader("Latest Triage Results")

    st.write("**Category:**", result["category"].title())
    st.write("**Assigned team:**", result["assigned_team"])

    if result["missing_urgency_info"] >= 0.8:
        st.write(
            "**Provisional urgency:**",
            f"{result['urgency']:.2f} / 2",
        )
        st.warning(
            "Priority needs clarification: ask how this affects the "
            "employee's work, whether a workaround exists, "
            "and whether there's a deadline."
        )
    else:
        st.write("**Urgency:**", f"{result['urgency']:.2f} / 2")

    st.write("**Category confidence:**", f"{result['confidence']:.0%}")
    st.write(
        "**Probability of insufficient routing information:**",
        f"{result['missing_routing_info']:.0%}",
    )
    st.write(
        "**Probability of insufficient urgency information:**",
        f"{result['missing_urgency_info']:.0%}",
    )

    if result["needs_review"]:
        st.warning("Needs human review before routing.")
    else:
        st.success("Ready to route.")

    follow_up_questions = {
        "affected_system": "Which device, application, or service is affected?",
        "work_impact": "What work is this preventing you from doing?",
        "workaround": "Is there another way you can continue working?",
        "deadline": "Is there a deadline this issue puts at risk?",
    }

    selected_question = result["clarifying_question"]

    if selected_question != "none":
        st.subheader("Suggested follow-up")

        question_text = follow_up_questions[selected_question]
        st.write(question_text)

        answer_key = (
            f"follow_up_{st.session_state.ticket_id}_"
            f"{len(st.session_state.follow_up_history)}"
        )

        answer = st.text_area("Your answer", key=answer_key)

        if st.button("Update triage"):
            if answer.strip():
                updated_history = (
                    st.session_state.follow_up_history
                    + [{
                        "question": question_text,
                        "answer": answer.strip(),
                    }]
                )

                context_parts = [
                    "Original employee report:",
                    st.session_state.original_message,
                ]

                for exchange in updated_history:
                    context_parts.extend([
                        "",
                        f"IT follow-up: {exchange['question']}",
                        f"Employee answer: {exchange['answer']}",
                    ])

                combined_context = "\n".join(context_parts)

                try:
                    with st.spinner("Updating triage..."):
                        updated_result = triage_ticket(combined_context)

                        update_ticket(
                            st.session_state.ticket_id,
                            combined_context,
                            updated_result,
                        )

                except Exception:
                    st.error(
                        "The update could not be analyzed or saved. "
                        "Your answer and the previous results have been kept. "
                        "Please try again."
                    )

                else:
                    st.session_state.follow_up_history = updated_history
                    st.session_state.latest_result = updated_result
                    st.rerun()

            else:
                st.warning("Please enter an answer before updating.")


    with st.expander("View raw results"):
        st.json(result)

st.subheader("Ticket History")

needs_review_only = st.checkbox("Needs review only")
needs_clarification_only = st.checkbox("Priority needs clarification only")

tickets = load_tickets()

if needs_review_only:
    tickets = [
        ticket for ticket in tickets
        if ticket["needs_review"] == 1
    ]

if needs_clarification_only:
    tickets = [
        ticket for ticket in tickets
        if ticket["missing_urgency_info"] is not None
        and ticket["missing_urgency_info"] >= 0.8
    ]

if tickets:
    st.dataframe(tickets, hide_index=True)
elif needs_review_only and needs_clarification_only:
    st.info("No tickets need both routing review and priority clarification.")
elif needs_review_only:
    st.info("No tickets need review.")
elif needs_clarification_only:
    st.info("No tickets need priority clarification.")
else:
    st.info("No tickets saved yet.")