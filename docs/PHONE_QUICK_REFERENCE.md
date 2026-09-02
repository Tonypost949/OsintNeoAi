# PHONE QUICK REFERENCE — OsintNeoAi VM & Services
## Open this on phone: `https://github.com/Tonypost949/OsintNeoAi/blob/main/docs/PHONE_QUICK_REFERENCE.md`

---

## VM Access (Termius SSH)
| Field | Value |
|-------|-------|
| **Host** | `osint-cli-vm` |
| **IP** | `20.10.48.11` |
| **Port** | `22` |
| **User** | `azureuser` |
| **Key** | `~/.ssh/id_rsa` (import into Termius) |
| **OS** | Ubuntu 22.04 |
| **Size** | Standard_D2s_v3 (2 vCPU 8GB) |
| **Location** | East US 2 |
| **Resource Group** | `osint-cli-rg2` |
| **Subscription** | `f055033f` (Azure Students $100/mo) |
| **Auto-shutdown** | 02:00 UTC daily (7pm PT) |

### Start/Stop VM (from phone Azure app or shell.azure.com)
```bash
az vm start -g osint-cli-rg2 -n osint-cli-vm
az vm deallocate -g osint-cli-rg2 -n osint-cli-vm   # stops billing
az vm auto-shutdown -g osint-cli-rg2 -n osint-cli-vm --time 0200
```

---

## Web Dashboards (phone browser, no VM needed)
| URL | What |
|-----|------|
| `https://osintneoai-app-949.azurewebsites.net/` | Main dashboard |
| `https://osintneoai-app-949.azurewebsites.net/gods-eye-max` | Gods Eye Max 3D (2261 nodes) |
| `https://osintneoai-app-949.azurewebsites.net/syncfusion` | Syncfusion Grid ($9,995 licensed) |
| `https://osintneoai-app-949.azurewebsites.net/tasks` | Kanban Task Board (52 tasks) |
| `https://osintneoai-app-949.azurewebsites.net/mobile` | Mobile PWA HUD |
| `https://osintneoai-app-949.azurewebsites.net/api/tasks` | Tasks API (JSON) |
| `https://osintneoai-app-949.azurewebsites.net/api/scan` | Scanner API |
| `https://osintneoai-app-949.azurewebsites.net/api/maps` | Maps API |
| `https://shell.azure.com` | Azure Cloud Shell (free, instant) |
| `https://portal.azure.com` | Azure Portal |
| `https://dev.azure.com/anthonydimarcello` | Azure DevOps |
| `https://mcp.dev.azure.com/anthonydimarcello` | Azure DevOps MCP |

---

## CLIs on VM (run via Termius SSH)
### Internal
| CLI | Command | Purpose |
|-----|---------|---------|
| OSINTNeoAi Core | `python OsintNeoAi/cli/cli.py` | Interactive OSINT agent |
| Master Hub | `python OsintNeoAi/OSINTNeoAiCLI.py` | Hub server :5052 |
| Sentinel Edition | `python OsintNeoAi/opencode_work/sentinel-edition/cli.py` | Autonomous monitor |

### Google Cloud (GCP)
| CLI | Command | Purpose |
|-----|---------|---------|
| gcloud | `gcloud --version` | GCP management |
| bq | `bq version` | BigQuery |
| gsutil | `gsutil version` | Cloud Storage |
| firebase | `firebase --version` | Firebase |
| dataform | `dataform --version` | Data pipelines |

### Azure
| CLI | Command | Purpose |
|-----|---------|---------|
| az | `az --version` | Azure management |
| gh | `gh --version` | GitHub |

### Multi-Cloud & Infra
| CLI | Command | Purpose |
|-----|---------|---------|
| terraform | `terraform version` | IaC |
| kubectl | `kubectl version --client` | Kubernetes |
| helm | `helm version` | K8s packages |
| rclone | `rclone version` | Cloud sync |
| docker | `docker --version` | Containers |

### AI & LLM Agents
| CLI | Command | Purpose |
|-----|---------|---------|
| agy/gemini | `gemini --version` | Google AI agent |
| claude | `claude --version` | Anthropic AI agent |
| ollama | `ollama --version` | Local LLMs |
| openai | `openai --version` | OpenAI API |
| huggingface | `huggingface-cli version` | HF models |

### OSINT & Forensics
| CLI | Command | Purpose |
|-----|---------|---------|
| nmap | `nmap --version` | Network scanner |
| exiftool | `exiftool -ver` | Image/PDF metadata |
| ffmpeg | `ffmpeg -version` | Media forensics |
| yt-dlp | `yt-dlp --version` | Video extractor |
| shodan | `shodan version` | IoT search |
| sherlock | `sherlock --version` | Username hunter |
| whois | `whois --version` | Domain lookup |

### Dev & Runtimes
| CLI | Command | Purpose |
|-----|---------|---------|
| git | `git --version` | Version control |
| python3 | `python3 --version` | Python runtime |
| node/npm | `node -v && npm -v` | JavaScript |
| cargo | `cargo --version` | Rust |
| go | `go version` | Go |
| dotnet | `dotnet --version` | .NET |
| uv | `uv --version` | Fast pip |

---

## VSDE Benefits ($14k+ free, no card)
| Benefit | How to claim |
|---------|-------------|
| Syncfusion $9,995 | `https://my.visualstudio.com/benefits` → Syncfusion → Key: `Ngo9Big...` |
| JetBrains $779 | VSDE → JetBrains → License |
| Pluralsight $600 | VSDE → Pluralsight → 6 months |
| DataCamp $300 | VSDE → DataCamp → 3 months |
| LinkedIn Premium $300 | VSDE → LinkedIn → 6 months |
| Parasoft $1,200 | VSDE → Parasoft → 1 year |
| Termius Pro $1,200 | VSDE → Termius → phone SSH app |
| Atlas/Datadog $500 | GitHub Student Pack → education.github.com |
| GitHub Copilot | GitHub Settings → Copilot → Free for students |

---

## Credentials (store in phone password manager)
| Service | Account | Notes |
|---------|---------|-------|
| Azure | `anthony.dimarcello@students.post.edu` | $100/mo Students |
| GitHub | `Tonypost949` | `Tonypost949/OsintNeoAi` |
| Azure DevOps | `anthonydimarcello` | `osintneoai` project |
| BigQuery | `noble-beanbag-497411-m4` | `onedrive_forensics`, `national_audits` |
| Azure OpenAI | `opencode-ai-8609-a7f40` | `gpt-5-mini`, `gpt-4.1-mini` |
| Syncfusion | Order `W753756` | License key in `data/syncfusion_license.key` |

---

## Quick Commands (copy-paste into Termius)
```bash
# Clone repo
git clone https://github.com/Tonypost949/OsintNeoAi.git && cd OsintNeoAi

# Start hub
python OSINTNeoAiCLI.py

# Start OSINT agent
python cli/cli.py

# Run full scan
python cli/cli.py chat

# Azure status
az account show

# Docker containers
docker ps -a

# Pull latest
git pull origin main

# View tasks
cat data/tasks.json | python3 -m json.tool | head -100
```
