import streamlit as st
from content_graph import content_creation_graph
from utils import style_guide_vector_store, check_api_keys

# --- Page Configuration ---
st.set_page_config(
    page_title="Concept to Creation Assistant",
    page_icon="🤖",
    layout="wide"
)

# --- App Header ---
st.title("🤖 Concept to Creation Content Assistant")
st.markdown("""
Welcome! This AI-powered creative partner helps you go from a simple topic to a fully structured content plan.
Provide a topic, and the multi-agent team will work on it. You'll then have the chance to approve it or request revisions.
""")

st.divider()

# --- Initialize Session State ---
if 'run_complete' not in st.session_state:
    st.session_state.run_complete = False
    st.session_state.final_script = ""
    st.session_state.creative_suggestions = None
    st.session_state.research_notes = []
    st.session_state.topic = ""

# --- API Key Check ---
missing_keys = check_api_keys()
if missing_keys:
    st.error(f"Missing required API keys: {', '.join(missing_keys)}. Please set them in your .env file.")
    st.stop()

# --- Main Application ---
st.header("1. Start or Revise a Content Project")

# Input field for the topic
topic_input = st.text_input("Enter your content topic (e.g., 'the basics of photosynthesis'):", value=st.session_state.topic)

if st.button("✨ Generate Content Plan", type="primary"):
    if not topic_input:
        st.warning("Please enter a topic to begin.")
    else:
        st.session_state.topic = topic_input
        st.session_state.run_complete = False  # Reset on new generation
        final_state = None
        try:
            with st.status("Agents are collaborating...", expanded=True) as status:
                graph_input = {"topic": st.session_state.topic}

                for state_update in content_creation_graph.stream(graph_input):
                    node_that_ran = list(state_update.keys())[0]

                    if node_that_ran == "researcher":
                        status.update(label="🔬 Agent 'Researcher' is gathering information...")
                    elif node_that_ran == "writer":
                        revision_num = state_update[node_that_ran].get('revision_number', 1)
                        status.update(label=f"✍️ Agent 'Writer' is crafting draft #{revision_num}...")
                    elif node_that_ran == "critic":
                        status.update(label="🧐 Agent 'Critic' is reviewing the draft...")

                    if '__end__' not in state_update:
                        final_state = state_update[node_that_ran]

                status.update(label="✅ Collaboration complete! Awaiting your review.", state="complete")

            st.session_state.run_complete = True
            st.session_state.final_script = final_state.get("final_script")
            st.session_state.creative_suggestions = final_state.get("creative_suggestions")
            st.session_state.research_notes = final_state.get("research_notes")
            st.rerun() # Rerun the script to display the results and buttons

        except Exception as e:
            st.error(f"An error occurred during content generation: {e}")
            st.stop()

# --- Display Results and Get User Feedback ---
if st.session_state.run_complete:
    st.divider()
    st.header("2. Review Your Content Plan")

    st.subheader("📜 Final Script")
    st.markdown(st.session_state.final_script)

    st.subheader("💡 Creative Suggestions")
    st.json(st.session_state.creative_suggestions)

    st.divider()
    st.header("3. What's Next?")

    # --- Approval Path ---
    st.subheader("Option A: Approve and Save")
    if st.button("👍 Looks good! Save to my Style Guide"):
        if style_guide_vector_store is not None:
            try:
                style_guide_vector_store.add_texts([st.session_state.final_script])
                st.success("Successfully saved to your Style Guide! The agents will remember this style.")
                # Reset state for a new project
                st.session_state.run_complete = False
                st.session_state.final_script = ""
            except Exception as e:
                st.error(f"An error occurred while saving: {e}")
        else:
            st.error("Could not save to Style Guide because the vector store is not available.")

    # --- Rejection and Revision Path ---
    st.subheader("Option B: Request Revisions")
    st.markdown("If the script isn't quite right, provide feedback below.")
    user_feedback = st.text_area("Your feedback for the Writer agent:", key="user_feedback_area",
                                 placeholder="e.g., 'Make the tone more casual and add a section about its impact on marine life.'")

    if st.button("🔁 Regenerate with My Feedback"):
        if not user_feedback:
            st.warning("Please provide feedback before regenerating.")
        else:
            final_state = None
            try:
                with st.status("Agents are revising based on your feedback...", expanded=True) as status:
                    # Re-run the graph, but this time with the original research and the user's feedback
                    graph_input = {
                        "topic": st.session_state.topic,
                        "research_notes": st.session_state.research_notes,
                        "user_feedback": user_feedback,
                    }

                    for state_update in content_creation_graph.stream(graph_input):
                        node_that_ran = list(state_update.keys())[0]

                        if node_that_ran == "writer":
                            revision_num = state_update[node_that_ran].get('revision_number', 1)
                            status.update(label=f"✍️ Agent 'Writer' is revising based on your notes (Draft #{revision_num})...")
                        elif node_that_ran == "critic":
                            status.update(label="🧐 Agent 'Critic' is reviewing the new revision...")

                        if '__end__' not in state_update:
                            final_state = state_update[node_that_ran]

                    status.update(label="✅ Revision complete! Awaiting your review.", state="complete")

                # Update the session state with the new results
                st.session_state.final_script = final_state.get("final_script")
                st.session_state.creative_suggestions = final_state.get("creative_suggestions")
                st.rerun() # Rerun to display the updated script

            except Exception as e:
                st.error(f"An error occurred during revision: {e}")
                st.stop()