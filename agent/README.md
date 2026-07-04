# OSINTNeoAi (NWORICO Data Engine)

This project contains the agent configuration generated from Agent Studio for the **OSINTNeoAi** agent. 

## Setup
The agent requires a Python environment. The IDE has automatically:
1. Created a virtual environment (`venv`)
2. Installed dependencies (`google-adk`, `google-genai`)
3. Stored the primary configuration in `agent.py`

## Instructions
To run this agent:
- Make sure to activate the virtual environment: `.\venv\Scripts\Activate.ps1`
- Run locally or via ADK web:
  - Usually, this involves running the agent file directly or using an ADK command-line interface.

## Notes
- **Model**: `gemini-3.5-flash` (using the `GlobalGemini` class to pin Vertex AI to the `global` location).
- **Primary Function**: Forensic data analysis specialized in corporate shell mapping, public fund leakage, and environmental crime tracking.
- **Database Context**: `project-743aab84-f9a5-4ec7-954.national_audits.all_state_records`
