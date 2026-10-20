# ⚡ Microsoft Graph Explorer & Entra ID Integration Guide
## Connecting Microsoft 365, Entra ID, Power Platform & Security APIs into OSINT Neo AI

---

### I. OVERVIEW & CAPABILITIES

**Microsoft Graph Explorer** ([`developer.microsoft.com/en-us/graph/graph-explorer`](https://developer.microsoft.com/en-us/graph/graph-explorer)) is Microsoft's official REST API workspace for testing and executing queries across the entire Microsoft Cloud ecosystem.

When connected to your Microsoft 365 / Entra ID tenant, Graph Explorer lets you query, inspect, and automate:
1. **Entra ID (Azure AD):** Users, Groups, App Registrations, Service Principals, and Directory Roles.
2. **Security & Identity Protection:** Security Alerts (`/v1.0/security/alerts_v2`), Risky Sign-ins, Audit Logs (`/v1.0/auditLogs/directoryAudits`).
3. **Power Platform & Dataverse:** Environments, Custom Connectors, and Power Automate Flows.
4. **Cloud Storage & Collaboration:** OneDrive files, SharePoint document libraries, Teams messages, and Outlook emails.

```
+---------------------------------------------------------------------------------------------------------+
|                               MICROSOFT GRAPH × OSINT NEO AI ARCHITECTURE                               |
+---------------------------------------------------------------------------------------------------------+
|                                                                                                         |
|   Microsoft Graph API             Graph Explorer (Web UI)            OSINT Neo AI Core                  |
|  [graph.microsoft.com]  =======>  [Bearer Access Token]   =======>  [nodes.json & edges.json]           |
|                                                                                                         |
|           ||                                                                   ||                       |
|           \/                                                                   \/                       |
|  Entra ID & Azure AD           Power Platform Connectors             Tactical GIS Hub & AI Chat         |
|  (Users, Audits, Roles)        (Custom API & Automate Flows)         (Correlate & Investigate)          |
|                                                                                                         |
+---------------------------------------------------------------------------------------------------------+
```

---

### II. ESSENTIAL GRAPH API QUERIES FOR OSINT & SECURITY

#### 1. Identity, Tenant & Directory Auditing
```http
### Get Current Authenticated Profile
GET https://graph.microsoft.com/v1.0/me

### List All Users in Tenant (with properties)
GET https://graph.microsoft.com/v1.0/users?$select=displayName,userPrincipalName,id,accountEnabled,jobTitle,department

### List App Registrations (Service Principals)
GET https://graph.microsoft.com/v1.0/applications?$select=id,appId,displayName,createdDateTime

### List Directory Roles & Admin Permissions
GET https://graph.microsoft.com/v1.0/directoryRoles
```

#### 2. Security Alerts & Audit Logs (Entra ID)
```http
### Query Live Security Alerts v2 (Defender / Sentinel)
GET https://graph.microsoft.com/v1.0/security/alerts_v2?$top=25&$orderby=createdDateTime desc

### Query Directory Audit Logs
GET https://graph.microsoft.com/v1.0/auditLogs/directoryAudits?$top=50&$orderby=activityDateTime desc

### Query Risky Users & Identity Anomalies
GET https://graph.microsoft.com/v1.0/identityProtection/riskyUsers
```

#### 3. Power Platform & SharePoint Evidence Document Search
```http
### Search Files in OneDrive & SharePoint for Case Keywords
GET https://graph.microsoft.com/v1.0/me/drive/root/search(q='Warner')?$select=name,id,webUrl,size

### List SharePoint Sites
GET https://graph.microsoft.com/v1.0/sites?search=*
```

---

### III. PYTHON SCRIPT TO INGEST GRAPH API DATA INTO OSINT NEO AI

You can extract your **Bearer Access Token** directly from the Graph Explorer UI (under the *Access token* tab) and run the following Python ingest script:

```python
# scripts/microsoft_graph_client.py
import requests
import json
import os

GRAPH_API_URL = "https://graph.microsoft.com/v1.0"

def fetch_graph_users(token):
    """
    Fetches Entra ID directory objects and formats them as graph nodes.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 1. Fetch Users
    resp = requests.get(f"{GRAPH_API_URL}/users?$select=displayName,userPrincipalName,id,jobTitle", headers=headers)
    if resp.status_code != 200:
        print(f"[-] Graph Error {resp.status_code}: {resp.text}")
        return []
    
    users = resp.json().get("value", [])
    print(f"[+] Ingested {len(users)} Entra ID user objects.")
    return users

if __name__ == "__main__":
    token = os.environ.get("MS_GRAPH_TOKEN")
    if not token:
        print("[!] Set MS_GRAPH_TOKEN environment variable with Bearer token from Graph Explorer.")
    else:
        users = fetch_graph_users(token)
        print(json.dumps(users[:3], indent=2))
```

---

### IV. INTEGRATION WITH POWER APPS & AZURE APP SERVICE

1. **Power Apps Connector:** Our repository includes [`powerplatform/powerapps_custom_connector.json`](file:///C:/Users/Amd949609/OsintNeoAi-1/powerplatform/powerapps_custom_connector.json) which can be registered in Power Apps to call our live Azure API (`https://osintneoai-app-949.azurewebsites.net`).
2. **Continuous Monitoring:** Power Automate flows (`powerplatform/flows/public_notice_keyword_watcher.json`) can use Microsoft Graph triggers (e.g. new email received or new file created) to automatically feed data into our local and Azure servers.
