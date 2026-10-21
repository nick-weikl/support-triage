import streamlit as st
from triage import triage_ticket
from storage import initialize_database, save_ticket, load_tickets

initialize_database()

st.title("Support Ticket Triage")

message = st.text_area("Report Issue")

if st.button("Analyze Ticket"):
    if message.strip():
        with st.spinner("Analyzing ticket..."):
            result = triage_ticket(message.strip())
            ticket_id = save_ticket(message.strip(), result)
            st.session_state.latest_result = result
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