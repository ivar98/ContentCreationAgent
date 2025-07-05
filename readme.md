````markdown

# 🤖 Concept to Creation Content Assistant

This is an AI-powered creative partner that helps content creators (YouTubers, bloggers, podcasters) go from a vague idea to a fully structured content plan. The user provides a simple topic, and a team of AI agents autonomously researches, writes, critiques, and finalizes a script, learning your preferred style over time.

This project is a practical implementation of a multi-agent collaborative workflow using **LangGraph**, external tools for research, a vector database for memory, and a Streamlit UI for interaction.

## ✨ Features

*   **Multi-Agent Collaboration**: Utilizes a `Researcher`, `Writer`, and `Critic` agent, orchestrated by LangGraph, to mimic a real creative team.
*   **Autonomous Web Research**: The `Researcher` agent uses the Tavily Search API to gather up-to-date information on any topic.
*   **Self-Correction Loop**: The `Writer` and `Critic` agents work in a loop, refining the draft based on constructive feedback until it meets quality standards.
*   **Dual-Memory System**:
    *   **Short-Term "Research Desk"**: A ChromaDB collection stores research for the current project.
    *   **Long-Term "Style Memory"**: A persistent ChromaDB collection stores final, user-approved scripts to help the AI learn the user's preferred style.
*   **Interactive UI**: A simple and clean dashboard built with Streamlit allows users to input topics, watch the agents' progress in real-time, and view the final content plan.

## ⚙️ Tech Stack

*   **Language**: Python
*   **Core Framework**: LangGraph, LangChain
*   **LLM**: Google Gemini Pro (via `langchain-google-genai`)
*   **Web Search Tool**: Tavily Search API
*   **Embedding Model**: `all-MiniLM-L6-v2` (from Hugging Face SentenceTransformers)
*   **Vector Database**: ChromaDB (local & persistent)
*   **Frontend**: Streamlit

## 🚀 Setup and Installation

Follow these steps to set up and run the application on your local machine.

### 1. Prerequisites

*   Python 3.9+
*   Git

### 2. Clone the Repository

```bash
git clone https://github.com/your-username/concept-to-creation.git
cd concept-to-creation
```

### 3. Set Up a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

### 4. Install Dependencies

Install all the required Python packages from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 5. Configure API Keys

The application requires API keys for Google Gemini and Tavily Search.

1.  **Copy the example file**:
    ```bash
    cp .env.example .env
    ```

2.  **Edit the `.env` file**: Open the newly created `.env` file in a text editor and add your API keys.
    *   `GOOGLE_API_KEY`: Get yours from [Google AI Studio](https://aistudio.google.com/app/apikey).
    *   `TAVILY_API_KEY`: Get yours from the [Tavily API dashboard](https://app.tavily.com/).

## ▶️ How to Run the Application

Once the setup is complete, you can start the Streamlit application with a single command:

```bash
streamlit run app.py
```

Your web browser should automatically open to the application's URL (usually `http://localhost:8501`).

## 🛠️ How It Works (Architecture)

The application's logic is orchestrated by a LangGraph state machine.

1.  **User Input**: The user provides a topic in the Streamlit UI.
2.  **Researcher**: The graph starts with the `researcher` node. This agent uses the Tavily tool to search the web for information on the topic and saves its findings.
3.  **Writer**: The `writer` node takes the research notes and queries the "Style Guide" vector DB for examples of past successful scripts. It then synthesizes this information into a first draft.
4.  **Critic**: The `critic` node reviews the draft for quality, accuracy, and structure. It provides feedback.
5.  **Conditional Edge (The Loop)**: The graph reaches a decision point.
    *   If the critic provides feedback (i.e., not "NO NOTES"), the graph routes back to the `writer` node for a revision.
    *   If the critic approves the draft ("NO NOTES") or the revision limit (2) is reached, the graph proceeds.
6.  **Finalizer**: The `finalizer` node takes the approved script and generates creative suggestions like titles and visual ideas.
7.  **Output**: The final script and creative suggestions are displayed in the UI. The user has the option to save the script to the "Style Guide" for future use.

## 📂 Project Structure

```
concept-to-creation/
├── .gitignore          # Excludes unnecessary files from git
├── .env.example        # Template for API keys
├── requirements.txt    # Project dependencies
├── utils.py            # Handles setup of LLM, tools, and DBs
├── content_graph.py    # Defines the LangGraph agent workflow
└── app.py              # The Streamlit frontend application
```

---

## 💡 Suggestions for Modifications & Improvements

The current application is a solid foundation. Here are some ways it could be extended or improved:

1.  **Add More Specialized Agents**:
    *   **`SEO_Optimizer` Agent**: An agent that takes the final script and suggests keywords, meta descriptions, and structural changes to improve search engine ranking.
    *   **`Visualizer` Agent**: An agent that generates specific prompts for image generation models (like DALL-E 3 or Midjourney) based on the script content.
    *   **`Fact-Checker` Agent**: A dedicated agent that re-runs targeted web searches to verify specific claims made in the draft, increasing the final output's reliability.

2.  **Enhance User Interaction**:
    *   **Intermediate Editing**: Allow the user to view and *edit* the draft after each critique. This would involve using Streamlit's `st.session_state` more deeply and modifying the graph to accept user overrides.
    *   **Tone & Style Selection**: Add UI elements (e.g., dropdowns, sliders) to let the user specify the desired tone (`Formal`, `Witty`, `Casual`) or content format (`Blog Post`, `YouTube Script`, `Podcast Outline`) before starting the generation. This information could be passed to the `writer`'s prompt.

3.  **More Sophisticated Memory**:
    *   **Summarized Style Profiles**: Instead of just retrieving raw scripts, create a process that periodically summarizes the "Style Guide" into a concise "style profile" document. The `writer` could use this summary for more consistent style adoption.
    *   **Knowledge Graph for Research**: For complex, multi-project topics, use a knowledge graph instead of a simple vector store for research. This would allow the agents to understand relationships between entities and build a deeper domain understanding over time.

4.  **Deployment and Scalability**:
    *   **Deploy to Streamlit Community Cloud**: The app is well-suited for deployment on Streamlit's free hosting platform.
    *   **Asynchronous Execution**: For very long content generation tasks, convert the graph execution to an asynchronous process using `graph.astream()` and manage the background task so the user doesn't have to keep the browser tab open.

5.  **Robustness and Error Handling**:
    *   Implement more explicit `try...except` blocks around all API calls (LLM, Tavily) and database interactions to handle network errors, rate limits, or API downtime gracefully, providing clearer error messages to the user.
````