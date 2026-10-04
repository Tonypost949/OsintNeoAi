import os
import json
import g4f

class OSINTAgent:
    def __init__(self):
        # Maintain conversation history
        sys_prompt = """You are OSINTNeoAi, an autonomous intelligence agent.
You have access to Maltego Transforms to gather information.
If the user asks you to look up, scan, or investigate a target, you MUST output a tool execution command in this exact format:
<EXECUTE>TransformName TargetValue</EXECUTE>

CRITICAL RULES:
1. If the user provides an ambiguous keyword (e.g., "HBNC") and you don't know what it is, DO NOT execute a tool immediately.
2. Instead, provide 3 guesses of what the keyword might mean, and explicitly tell the user: "Hit ENTER to just perform a general web search."
3. If the user replies with "[USER HIT ENTER]", you must immediately execute a general web search on their last ambiguous keyword using:
<EXECUTE>WebSearch Keyword</EXECUTE>

Wait for the system to reply with the tool results before answering the user. If you already have the results, summarize them directly."""
        self.history = [{"role": "system", "content": sys_prompt}]

    def is_configured(self):
        return True # Always configured with g4f free backend

    def generate_response(self, user_input, graph_context, tools_file="data/tools.json"):
        tools_context = "No tools loaded."
        if os.path.exists(tools_file):
            try:
                with open(tools_file, "r", encoding="utf-8") as f:
                    tools_data = json.load(f)
                    tools_list = tools_data.get("tools", [])
                    tools_context = f"Available OSINT Tools: {len(tools_list)}\n"
                    # Include a sample of top 50
                    for t in tools_list[:50]:
                        tools_context += f"- {t.get('name')} ({t.get('category')}): {t.get('description')}\n"
            except Exception as e:
                tools_context = f"Error loading tools: {e}"

        # Serialize graph context
        graph_str = "Empty"
        if graph_context:
            graph_str = "\n".join([f"- [{e.type}] {e.value}" for e in graph_context])

        system_instruction = f"""
[SYSTEM DATA]
Current Investigation Graph:
{graph_str}

{tools_context}
"""
        # We only pass system_instruction as a system message once if needed, but since we append to history,
        # we will just format the user's prompt nicely.
        prompt = f"{system_instruction}\n\nUser: {user_input}"
        self.history.append({"role": "user", "content": prompt})

        try:
            response = g4f.ChatCompletion.create(
                model=g4f.models.default,
                messages=self.history,
            )
            # If it's a string, we append it directly
            self.history.append({"role": "assistant", "content": response})
            return response
        except Exception as e:
            return f"AI Error: {e}"

    def send_system_message(self, message):
        """Used to feed tool execution results back to the AI without user visibility."""
        self.history.append({"role": "user", "content": f"[SYSTEM TOOL RESULT]\n{message}\nAnalyze and summarize the above results for the user."})
        try:
            response = g4f.ChatCompletion.create(
                model=g4f.models.default,
                messages=self.history,
            )
            self.history.append({"role": "assistant", "content": response})
            return response
        except Exception as e:
            return f"AI Error: {e}"