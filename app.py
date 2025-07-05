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
Just provide a topic, and the multi-agent team will research, write, critique, and refine a script for you.
""")

st.divider()

# --- API Key Check ---
missing_keys = check_api_keys()
if missing_keys:
    st.error(f"Missing required API keys: {', '.join(missing_keys)}. Please set them in your .env file.")
    st.stop()

# --- Main Application ---
st.header("1. Start a New Content Project")

# Input field for the topic
topic = st.text_input("Enter your content topic (e.g., 'the basics of photosynthesis'):", key="topic_input")

if st.button("✨ Generate Content Plan", type="primary"):
    if not topic:
        st.warning("Please enter a topic to begin.")
    else:
        final_state = None
        try:
            with st.status("Agents are collaborating...", expanded=True) as status:
                graph_input = {"topic": topic}
                
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

                status.update(label="✅ Collaboration complete!", state="complete")

        except Exception as e:
            st.error(f"An error occurred during content generation: {e}")
            st.stop()

        st.divider()
        st.header("2. Your Final Content Plan")

        if final_state:
            st.subheader("📜 Final Script")
            st.markdown(final_state.get("final_script", "No script was generated."))

            st.subheader("💡 Creative Suggestions")
            st.json(final_state.get("creative_suggestions", "No creative suggestions were generated."))
            
            st.session_state.final_script_for_saving = final_state.get("final_script")

# --- Save to Style Guide Section ---
if 'final_script_for_saving' in st.session_state and st.session_state.final_script_for_saving:
    st.divider()
    st.header("3. Improve Future Content")
    st.markdown("Saving this script to your Style Guide will help the Writer agent learn your preferred tone and structure for future projects.")

    if st.button("👍 Looks good! Save to my Style Guide"):
        if style_guide_vector_store is not None:
            try:
                style_guide_vector_store.add_texts([st.session_state.final_script_for_saving])
                st.success("Successfully saved to your Style Guide! The agents will remember this style.")
                del st.session_state.final_script_for_saving
            except Exception as e:
                st.error(f"An error occurred while saving: {e}")
        else:
            st.error("Could not save to Style Guide because the vector store is not available.")
