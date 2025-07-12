import json
from typing import TypedDict, List, Dict, Optional
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langgraph.graph import StateGraph, END

from utils import llm, tavily_tool, research_retriever, style_guide_retriever, research_vector_store

# --- 1. Define the State ---
class ContentCreationState(TypedDict):
    topic: str
    research_notes: List[str]
    draft: str
    criticism: str
    revision_number: int
    final_script: str
    creative_suggestions: Dict
    user_feedback: Optional[str]

# --- 2. Define Agent Nodes and Prompts ---

# Node 2.1: Researcher
research_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a world-class researcher. Your goal is to find diverse and interesting information on a given topic. You are not a writer. Your sole job is to research. Break the topic down into 3-5 sub-queries and use your search tool for each. Synthesize the results into a list of key points and facts. Do not write paragraphs or a narrative."),
    ("human", "Research the topic: {topic}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
researcher_agent = create_tool_calling_agent(llm, [tavily_tool], research_prompt)
researcher_executor = AgentExecutor(agent=researcher_agent, tools=[tavily_tool], verbose=True)

def research_node(state: ContentCreationState):
    print("---NODE: RESEARCHER---")
    topic = state['topic']
    research_result = researcher_executor.invoke({"topic": topic})
    research_notes_list = research_result['output'].split('\n') if research_result['output'] else []
    if research_vector_store:
        research_vector_store.add_texts(research_notes_list, metadatas=[{"source": "researcher"} for _ in research_notes_list])
    return {
        "research_notes": research_notes_list,
        "revision_number": 0,
        "user_feedback": None
    }

# Node 2.2: Writer (WITH A MUCH MORE ROBUST PROMPT)
writer_prompt_template = """
## YOUR TASK
You are an expert content writer. Your task is to generate a well-structured and engaging script based *only* on the provided research notes.

## SCRIPT REQUIREMENTS
- **Structure:** Must have a clear hook, 3-4 main points, and a strong conclusion.
- **Tone:** Conversational and easy to understand.
- **Priority:** If user feedback is provided, it is your HIGHEST priority. Address it directly. If internal criticism is provided, address that next.
- **Source of Truth:** Base the script **only** on the provided "RESEARCH NOTES". Do not invent facts or use outside knowledge.
- **Style:** If "STYLE EXAMPLES" are given, try to match their tone and structure.

## CONTENT TO USE
---
**TOPIC:**
{topic}

**USER FEEDBACK (Address This First):**
{user_feedback}

**INTERNAL CRITICISM (Address This Next):**
{criticism}

**RESEARCH NOTES (Your Source of Truth):**
{notes}

**STYLE EXAMPLES (Learn from these):**
{style_examples}
---

## YOUR SCRIPT:
"""
writer_prompt = ChatPromptTemplate.from_template(writer_prompt_template)
writer_runnable = writer_prompt | llm

def write_node(state: ContentCreationState):
    if state.get("user_feedback"):
        print(f"---NODE: WRITER (Revising based on USER FEEDBACK)---")
        revision_num = 1
    else:
        revision_num = state.get("revision_number", 0) + 1
        print(f"---NODE: WRITER (Internal Revision {revision_num})---")

    style_docs = style_guide_retriever.invoke(state['topic']) if style_guide_retriever else []
    formatted_examples = "\n---\n".join([doc.page_content for doc in style_docs]) if style_docs else "N/A"
    formatted_notes = "\n".join(state['research_notes'])

    writer_input = {
        "topic": state['topic'],
        "notes": formatted_notes,
        "style_examples": formatted_examples,
        "criticism": state.get("criticism", "N/A"),
        "user_feedback": state.get("user_feedback", "N/A")
    }
    draft_content = writer_runnable.invoke(writer_input)
    return {
        "draft": draft_content.content,
        "revision_number": revision_num
    }

# Node 2.3: Critic
critic_prompt_template = """
You are a sharp but fair content critic. Your job is to review a script and provide concise, actionable feedback.

**Instructions:**
1.  **Review the Draft:** Read the script below carefully.
2.  **Evaluate:** Judge it on clarity, engagement, structure, and accuracy based on the research notes.
3.  **Provide Feedback:** Give one key point of constructive feedback to improve the script. Be specific.
4.  **Approval:** If the script is excellent and needs no changes, respond with only the words: "NO NOTES".

**Content to Review:**
---
**Topic:**
{topic}

**Research Notes (for accuracy check):**
{notes}

**Draft Script:**
{draft}
---
"""
critic_prompt = ChatPromptTemplate.from_template(critic_prompt_template)
critic_runnable = critic_prompt | llm

def critic_node(state: ContentCreationState):
    print("---NODE: CRITIC---")
    formatted_notes = "\n".join(state['research_notes'])
    critic_input = {"topic": state['topic'], "notes": formatted_notes, "draft": state['draft']}
    criticism = critic_runnable.invoke(critic_input).content
    print(f"Critic's Feedback: {criticism}")
    return {"criticism": criticism, "user_feedback": None}

# Node 2.4: Finalizer
finalizer_prompt_template = """
You are a creative director. The main script is complete. Your job is to provide creative suggestions to enhance the final content.

Based on the final script below, generate a JSON object with suggestions for:
1.  `title_suggestions`: 3-5 catchy titles for the content.
2.  `visual_ideas`: A list of 3-4 ideas for visuals (e.g., "An animated diagram of the Krebs cycle", "A slow-motion shot of a water droplet").
3.  `sound_effects`: A list of 2-3 sound effect ideas (e.g., "Upbeat synth music during intro", "A 'ding' sound when a key term is defined").

**Final Script:**
---
{final_script}
---
"""
finalizer_prompt = ChatPromptTemplate.from_template(finalizer_prompt_template)
finalizer_runnable = finalizer_prompt | llm

def finalize_node(state: ContentCreationState):
    print("---NODE: FINALIZER---")
    finalizer_input = {"final_script": state['draft']}
    creative_suggestions_raw = finalizer_runnable.invoke(finalizer_input).content
    try:
        json_string = creative_suggestions_raw.strip().replace("```json", "").replace("```", "")
        creative_suggestions = json.loads(json_string)
    except json.JSONDecodeError:
        creative_suggestions = {"error": "Failed to parse creative suggestions.", "raw_output": creative_suggestions_raw}
    return {
        "final_script": state['draft'],
        "creative_suggestions": creative_suggestions,
        "research_notes": state['research_notes']
    }


# --- 3. Define the Graph Edges ---

def decide_to_revise(state: ContentCreationState):
    print("---EDGE: DECISION---")
    criticism = state.get("criticism", "").strip().upper()
    revision_num = state.get("revision_number", 0)
    if "NO NOTES" in criticism or revision_num >= 2:
        print("Decision: Draft approved by critic. Finalizing.")
        return "finalize"
    else:
        print("Decision: Draft needs internal revision.")
        return "revise"

def route_start(state: ContentCreationState):
    if state.get("user_feedback"):
        print("---ROUTING: User feedback provided. Skipping research.---")
        return "writer"
    else:
        print("---ROUTING: New topic. Starting with research.---")
        return "researcher"

# --- 4. Assemble the Graph ---
builder = StateGraph(ContentCreationState)

builder.add_node("researcher", research_node)
builder.add_node("writer", write_node)
builder.add_node("critic", critic_node)
builder.add_node("finalizer", finalize_node)

builder.set_conditional_entry_point(
    route_start,
    {
        "researcher": "researcher",
        "writer": "writer",
    }
)

builder.add_edge("researcher", "writer")
builder.add_edge("writer", "critic")
builder.add_conditional_edges(
    "critic",
    decide_to_revise,
    {
        "revise": "writer",
        "finalize": "finalizer"
    }
)
builder.add_edge("finalizer", END)

content_creation_graph = builder.compile()