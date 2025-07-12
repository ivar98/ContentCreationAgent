# 🤖 Concept to Creation Content Assistant

Ever stared at a blank page, not knowing where to start on your next blog post or video script? This project is your own personal AI creative team, designed to take a simple topic and turn it into a fully researched and polished piece of content.

You give it an idea, and a team of AI agents—a Researcher, a Writer, and a Critic—work together to build a complete content plan for you. Best of all, it learns your unique writing style over time!



## ✨ Features

*   **Your Own AI Creative Team**: A specialized team of AI agents collaborates to research, write, and edit your content.
*   **Built-in Quality Control**: A "Critic" agent reviews the script and sends it back for revisions until it meets quality standards.
*   **You're the Director**: Don't like the first draft? Give your own feedback and have the AI team regenerate the script based on your notes.
*   **Learns Your Style**: Save your favorite scripts to a "Style Guide," and the AI Writer will learn to mimic your preferred tone and structure in future projects.
*   **Simple & Fun to Use**: A clean web interface makes it easy for anyone to go from idea to finished script in minutes.

## 🤔 How It Works (The Simple Version)

Imagine you're the boss of a small creative studio. Your workflow looks like this:

1.  **You Give the Topic**: You start by telling your team what you want to create content about (e.g., "the benefits of bee-keeping").
2.  **The Researcher Gets to Work**: An AI agent scours the internet to gather all the important facts and notes.
3.  **The Writer Creates a Draft**: A second AI agent takes the research and writes an engaging script.
4.  **The Critic Reviews It**: A third AI agent acts as an editor. It checks the script for quality and accuracy. If there are problems, it sends the script back to the Writer for a re-do. This happens automatically!
5.  **You Get the Final Say**: The app presents the final script to you. You can either approve it or provide your own feedback and send it back for another revision.

## 🚀 Getting Started: Running The App on Your Computer

Follow these steps to get your own AI creative team up and running.

### Prerequisites

Before you start, you'll need two things installed on your computer. If you don't have them, just click the links to download and install them first.

*   **Python** (Version 3.9 or newer): [Download Python](https://www.python.org/downloads/)
*   **Git** (For copying the project files): [Download Git](https://git-scm.com/downloads)

---

### Step 1: Get the Project Code

First, you need to copy the project's code onto your computer.

Open your computer's **Terminal** (on Mac/Linux) or **Command Prompt/PowerShell** (on Windows) and run this command:

```bash
git clone https://github.com/ivar98/ivar98-contentcreationagent.git
```

This will create a new folder called `ivar98-contentcreationagent`. Now, navigate into that folder with this command:

```bash
cd ivar98-contentcreationagent```
> **Simpler Way:** If you're not comfortable with Git, you can just go to the [GitHub page](https://github.com/ivar98/ivar98-contentcreationagent) and click the green "Code" button, then "Download ZIP". Unzip the file and open the folder.

---

### Step 2: Set Up a "Virtual Workspace"

To keep this project's tools separate from your other computer files, we'll create a virtual workspace.

Run the following command in your terminal:

```bash
# For macOS/Linux
python3 -m venv venv

# For Windows
python -m venv venv
```

Now, **activate** this workspace. This is like "turning on" the project's private area.

```bash
# For macOS/Linux
source venv/bin/activate

# For Windows
.\venv\Scripts\activate
```

You'll know it worked if you see `(venv)` appear at the start of your terminal line.

---

### Step 3: Install All the Necessary Tools

Now, let's install all the Python libraries the project needs to function. It's just one simple command:

```bash
pip install -r requirements.txt
```

This will automatically read the `requirements.txt` file and install everything for you. Grab a cup of coffee, as this might take a few minutes!

---

### Step 4: Get Your Secret Keys (API Keys)

The app needs "keys" to connect to the AI services that power it. Think of these like special passwords. You'll need two free keys.

1.  **First, create a `.env` file** where you'll store your keys. Make a copy of the example file by running this command:

    ```bash
    # For macOS/Linux
    cp .env.example .env

    # For Windows
    copy .env.example .env
    ```

2.  **Now, get your keys:**
    *   **Google Gemini Key**: Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and create a free API key.
    *   **Tavily Search Key**: Go to the [Tavily API Dashboard](https://app.tavily.com/), sign up for a free account, and copy your API key.

3.  **Finally, edit the `.env` file** you created. Open it in a simple text editor (like Notepad) and paste your keys in. It should look like this:

    ```
    # Replace the placeholder text with your actual keys
    GOOGLE_API_KEY="AIzaSy...your...google...key...here..."
    TAVILY_API_KEY="tvly-...your...tavily...key...here..."
    ```

---

### Step 5: Run the App!

You're all set! Now for the fun part. Run the following command in your terminal (make sure your virtual workspace is still active!):

```bash
streamlit run app.py
```

Your web browser should automatically open a new tab with the application running.

Congratulations! You can now start creating content with your very own AI team.

## 📂 Project Files

For those who are curious, here's what the main files in the project do:

*   **`app.py`**: Runs the Streamlit web interface that you interact with.
*   **`content_graph.py`**: Defines the AI agent team and their workflow using LangGraph.
*   **`utils.py`**: Sets up the connection to the AI models and the vector database.
*   **`requirements.txt`**: A list of all the Python tools the project needs.
*   **`readme.md`**: This file!

## 📜 License

This project is open-source and available under the [MIT License](LICENSE). Feel free to use it, share it, and build upon it