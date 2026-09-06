# AnythingLLM Custom Agent Skill: OsintNeoAi LightBox EDR Engine

This custom agent skill integrates the **OsintNeoAi LightBox & EDR Master Environmental Intelligence Engine** ([lightbox_edr_engine.py](file:///C:/OsintNeoAi/lightbox_edr_engine.py)) into AnythingLLM desktop and server deployments.

## Setup & Deployment

1. Copy the `osintneoai_lightbox` folder into AnythingLLM skills directory:
   * **Desktop (Windows)**: `%APPDATA%\anythingllm-desktop\storage\plugins\agent-skills\osintneoai_lightbox\`
   * **Docker**: `/app/server/storage/plugins/agent-skills/osintneoai_lightbox/`
2. Enable the skill in your AnythingLLM Workspace settings.

## Supported Commands
* `search_edr_records`: Search 156 local cached EDR environmental audit records.
* `parcel_by_address`: Query parcel details by street address via LightBox API.
* `edr_sites_by_radius`: Audit contaminated sites within spatial radius.
