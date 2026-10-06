# IMMEDIATE WORKAROUND: ORACLE CLOUD FREE TIER (Always Free ARM VMs)

## 1. SIGN UP (5 min, different email than Azure)
https://cloud.oracle.com/free

## 2. CREATE VM (Always Free eligible)
- **Shape**: VM.Standard.A1.Flex (Ampere ARM)
- **OCPUs**: 4 (max free)
- **Memory**: 24 GB (max free)
- **OS**: Ubuntu 22.04
- **SSH Key**: paste your `~/.ssh/id_ed25519.pub`

## 3. AFTER CREATE
- Add ingress rules: 22 (SSH), 5052 (CLI hub), 10000 (Map), 8080/8443
- Save private IP, note public IP

## 4. AUTOMATED SETUP (run once on VM after SSH)

```bash
#!/bin/bash
# Run on new Oracle VM after SSH in
set -euo pipefail

# Update & install basics
sudo apt update && sudo apt install -y \
  docker.io docker-compose-v2 python3-pip git \
  google-cloud-cli gnupg curl jq

# Add user to docker group
sudo usermod -aG docker $USER

# Install gcloud (for BigQuery)
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | \
  sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
  sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
sudo apt update && sudo apt install -y google-cloud-cli

# Auth gcloud (run once, then use ADC)
# gcloud auth application-default login

# Clone repo
cd /home/ubuntu
git clone https://github.com/Tonypost949/OsintNeoAi.git
cd OsintNeoAi

# Start local services via docker-compose
cat > docker-compose.yml << 'COMPOSE_EOF'
version: '3.8'
services:
  cli-hub:
    build: .
    ports: ["5052:5052", "10000:10000"]
    volumes: [".:/workspace"]
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - GOOGLE_APPLICATION_CREDENTIALS=/workspace/credentials.json
    command: python -m app.server
    restart: unless-stopped
  map-server:
    image: nginx:alpine
    ports: ["10000:80"]
    volumes: ["./public:/usr/share/nginx/html:ro"]
    restart: unless-stopped
COMPOSE_EOF

# Start services
docker compose up -d

echo "=== DONE ==="
echo "CLI Hub: http://<PUBLIC_IP>:5052"
echo "Map Server: http://<PUBLIC_IP>:10000"
```

## 5. ALTERNATIVE: USE EXISTING GCP VM (ALREADY RUNNING)

```bash
# SSH to your existing GCP VM (already UP!)
gcloud compute ssh osint-cloud --zone=us-central1-a

# Or run BigQuery from local with ADC
gcloud auth application-default login
bq query --project=noble-beanbag-497411-m4 "YOUR QUERY"
```

## 5. QUICK LOCAL STACK (NO CLOUD NEEDED)

```bash
# Start local stack with Docker
cd C:\OsintNeoAi
cat > docker-compose.local.yml << 'EOF'
version: '3.8'
services:
  cli-hub:
    build: .
    ports: ["5052:5052", "10000:10000"]
    volumes: [".:/workspace"]
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    command: python -m app.server
    restart: unless-stopped
  map-server:
    image: nginx:alpine
    ports: ["10000:80"]
    volumes: ["./public:/usr/share/nginx/html:ro"]
    restart: unless-stopped
EOF

docker compose -f docker-compose.local.yml up -d

# Access: http://localhost:5052 and http://localhost:10000
```

## 6. ORACLE CLOUD SIGNUP LINKS
- **Primary**: https://cloud.oracle.com/free
- **Alternative**: https://www.oracle.com/cloud/free/

## 7. WHAT YOU GET FREE FOREVER (ORACLE)

| Resource | Free Tier Limit |
|----------|-----------------|
| Ampere ARM VMs | 4 OCPUs / 24 GB RAM |
| AMD EPYC VMs | 2 VMs (1/8 OCPU, 1 GB each) |
| Block Storage | 200 GB |
| Object Storage | 10 GB |
| Outbound Data | 10 TB/month |
| Load Balancer | 1 |
| Autonomous DB | 2 (20 GB each) |

## 7. NEXT STEPS (DO NOW)

1. **Right now**: Use GCP VM `osint-cloud` (already UP)
   ```bash
   gcloud compute ssh osint-cloud --zone=us-central1-a
   ```

2. **Today**: Sign up Oracle Cloud Free Tier (different email)

3. **This week**: Migrate persistent workloads to Oracle ARM VM

4. **Parallel**: Contact school IT for Azure for Students re-verification

---

**Bottom line: You have 3 working compute paths RIGHT NOW without Azure:**
1. **GCP VM** (already running) → BigQuery, Gemini, persistent
2. **Local Docker** (ports 5052, 10000) → CLI hub, Map server
3. **Oracle Free Tier** (after signup) → 4 ARM OCPUs forever free