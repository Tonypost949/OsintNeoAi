# GRAPHICAL VISUALIZATION PROMPT
## Copy this entire document to another AI/program

---

## WHAT TO CREATE

I need you to create graphical visualizations of a RICO criminal enterprise infrastructure map. The data is in my repository. Here is exactly what to look for and how to visualize it.

---

## DATA SOURCES — READ THESE FILES FIRST

### Evidence Package Location
All evidence files are at: C:\migrate opencode\OSINTNEOAI\evidence\
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\EVIDENCE_INDEX_CLEAN.md

### Master Matrix
Full filepath: C:\migrate opencode\OSINTNEOAI\reports\RICO_NATIONWIDE_INFRASTRUCTURE_MATRIX.md

### Port Scan Results
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\port_scans\lacounty.gov.txt
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\port_scans\libertyseniorliving.com.txt
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\port_scans\cookcountysheriff.org.txt
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\port_scans\pimasheriff.org.txt
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\port_scans\hbpd.org.txt

### HTTP Header Captures
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\http_headers\libertyseniorliving.com.txt
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\http_headers\cookcountysheriff.org.txt
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\http_headers\lacounty.gov.txt
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\http_headers\pimasheriff.org.txt

### Web Content Captures
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\web_content\libertyseniorliving.com_wp-admin_v2.txt
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\web_content\lacounty.gov_.txt
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\web_content\pimasheriff.org_.txt

### WHOIS Records
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\whois\libertyseniorliving.com.txt
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\whois\carlisledev.com.txt
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\whois\atlanticpacificcommunities.com.txt
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\whois\illuminationfoundation.org.txt
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\whois\libertyhomes.org.txt
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\whois\rbabuilders.com.txt
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\whois\cookcountysheriff.org.txt
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\whois\shelbycountytn.gov.txt
Full filepath: C:\migrate opencode\OSINTNEOAI\evidence\whois\anaheim.net.txt

---

## VISUALIZATION 1: IP CLUSTER MAP

Create a node-link diagram showing which domains share the same IP addresses.

### Nodes (color code by type)
RED nodes = RICO shell companies: l2tmedia.com, rbabuilders.com, stewartindustries.com
ORANGE nodes = Liberty-branded entities: libertyseniorliving.com, libertyhomes.org, libertycare.com, libertycare.org
GREEN nodes = Carlisle/Atlantic Pacific entities: carlisledev.com, carlisledevelopment.com, atlanticpacificcommunities.com, atlanticpacific.com
YELLOW nodes = Nonprofit fronts: illuminationfoundation.org, mercyhouse.org, covenanthouseca.org, waymakers.org
BLUE nodes = Government/Sheriff: cookcountysheriff.org, pimasheriff.org, hbpd.org, shelbycountytn.gov, lacounty.gov, anaheim.net, anaheimpd.org
GRAY nodes = Other: starpointproperties.com, advancedrealestate.com, raipartners.com, ocgov.com

### Links (edges)
Draw lines between domains that share the same IP address or same /24 subnet.

### IP Addresses to show
141.193.213.10 — hosts libertyseniorliving.com
141.193.213.21 — hosts l2tmedia.com AND cookcountysheriff.org
3.33.130.190 — hosts carlisledev.com, atlanticpacificcommunities.com, illuminationfoundation.org
76.223.54.146 — hosts libertyhomes.org, libertycare.com, libertycare.org, rbabuilders.com
89.106.200.153 — hosts shelbycountytn.gov AND anaheim.net
206.188.193.48 — hosts stewartindustries.com
206.188.193.178 — hosts carlisledevelopment.com
135.84.124.41 — hosts costamesa.gov, fullerton.ca.us, orangeca.gov, lvmpd.com

---

## VISUALIZATION 2: PORT EXPOSURE HEATMAP

Create a heatmap or table showing open ports for each critical target.

### Targets (rows)
lacounty.gov
libertyseniorliving.com
pimasheriff.org
cookcountysheriff.org
hbpd.org
shelbycountytn.gov
anaheim.net

### Ports (columns)
21 (FTP), 25 (SMTP), 80 (HTTP), 110 (POP3), 143 (IMAP), 443 (HTTPS), 993 (IMAPS), 995 (POP3S), 1433 (MSSQL), 3306 (MySQL), 3389 (RDP), 5432 (PostgreSQL), 5900 (VNC), 8080 (HTTP-Alt), 8443 (HTTPS-Alt), 9200 (Elasticsearch)

### Data for heatmap
lacounty.gov: 21=OPEN, 25=CLOSED, 80=OPEN, 110=OPEN, 143=OPEN, 443=OPEN, 993=OPEN, 995=OPEN, 1433=OPEN, 3306=OPEN, 3389=OPEN, 5432=CLOSED, 5900=OPEN, 8080=OPEN, 8443=OPEN, 9200=OPEN
libertyseniorliving.com: 80=OPEN, 443=OPEN, 8080=OPEN, 8443=OPEN
pimasheriff.org: 80=OPEN, 443=OPEN, 8080=OPEN, 8443=OPEN
cookcountysheriff.org: 80=OPEN, 443=OPEN, 8080=OPEN, 8443=OPEN
hbpd.org: 80=CLOSED, 443=OPEN
shelbycountytn.gov: 80=OPEN, 443=OPEN
anaheim.net: 80=OPEN, 443=OPEN

Color code: GREEN = closed/filtered, YELLOW = open but low risk, ORANGE = open medium risk, RED = open high risk (databases, remote access)

---

## VISUALIZATION 3: RICO ENTERPRISE FLOW DIAGRAM

Create a flowchart showing how the criminal enterprise operates.

### Pipeline 1: PPP Fraud
Start: Small business owners in Orange County
Flow: Apply for PPP loan using fake business address -> Receive funds -> Wire to shell company -> Shell company wires to personal accounts
Entities involved: l2tmedia.com, rbabuilders.com, stewartindustries.com, advancedrealestate.com, raipartners.com

### Pipeline 2: Nonprofit Money Laundering
Start: HUD/COC/ESG government grants
Flow: Government grant -> Nonprofit receives funds -> Nonprofit pays management fees to shell company -> Shell company pays personal accounts
Entities involved: illuminationfoundation.org, mercyhouse.org, covenanthouseca.org, waymakers.org

### Pipeline 3: IV-E Medicaid Billing
Start: Foster children in group homes
Flow: Children placed in group home -> Group home bills Medicaid -> Medicaid pays group home -> Group home pays management fees to parent company -> Parent company pays personal accounts
Entities involved: libertyhomes.org, libertycare.com, libertycare.org, libertyseniorliving.com

### The Liberty Connection
Show how Liberty Housing Services Inc (Santa Ana + Tustin) connects to Liberty City Miami housing fraud ($35M HUD grant, $20M squandered, 1,811 ghost employees)
Show how Carlisle Development Group ($26M fraud, CEO pleaded guilty) connects to Atlantic Pacific Communities (absorbed all Carlisle assets and personnel)

---

## VISUALIZATION 4: GEOGRAPHIC MAP

Create a map of the United States showing:
- Red pins for RICO-connected cities in Orange County, CA (Huntington Beach, Anaheim, Fullerton, Costa Mesa, Santa Ana, Tustin, Orange)
- Orange pins for Liberty-branded entities (Huntington Beach, Santa Ana, Tustin, Long Beach, Winnetka)
- Blue pins for Sheriff departments under investigation (Cook County IL, Pima County AZ, Shelby County TN, Los Angeles County CA)
- Yellow pins for PPP fraud clusters across 39 states

---

## VISUALIZATION 5: EVIDENCE TIMELINE

Create a timeline showing:
- 2020-2021: PPP loans disbursed ($3.1B+ in Orange County alone)
- 2021-2022: shell companies formed
- 2022-2023: nonprofits receive HUD/COC grants
- 2023-2024: group homes bill Medicaid
- 2024-2025: FBI investigates, indictments begin
- 2025-2026: Digital infrastructure reveals connections

---

## VISUALIZATION 6: SHERIFF DEPARTMENT RISK MATRIX

Create a table showing risk levels for each sheriff department.

### Columns
Department Name, State, Population Served, Open Ports, WAF Status, Infrastructure Risk, Investigation Status

### Data
Cook County Sheriff, Illinois, 5.2M, 4, Cloudflare WAF, HIGH (same /24 as RICO shell), Active federal investigation
Pima County Sheriff, Arizona, 1.0M, 4, Cloudflare WAF, MEDIUM (FBI civil asset forfeiture probe), FBI investigation, perjury allegations
Los Angeles County Sheriff, California, 10.0M, 13, NO WAF, CRITICAL (MySQL, RDP, PostgreSQL, VNC, Elasticsearch exposed), Unknown
Shelby County Sheriff, Tennessee, 930K, 2, NO WAF, HIGH (same IP as RICO city), Unknown
HB Police Department, California, 200K, 1, Cloudflare WAF, MEDIUM (142 ports from previous scan), 400 Dehashed breach listings
Las Vegas Metro Police, Nevada, 2.3M, 1, Cloudflare WAF, LOW, Unknown
Anaheim Police, California, 350K, 2, Cloudflare WAF, HIGH (same IP as shelbycountytn.gov), Unknown

---

## WHAT TO OUTPUT

Create these files:
1. cluster_map.html — Interactive node-link diagram (use D3.js or vis.js)
2. port_heatmap.html — Interactive heatmap table
3. rico_flow.html — Flowchart diagram
4. geo_map.html — United States map with pins
5. timeline.html — Interactive timeline
6. risk_matrix.html — Sortable table

Save all files to: C:\migrate opencode\OSINTNEOAI\evidence\visualizations\

Use full filepaths in all output. No shortcodes. No hyperlinks. Every URL must be complete.
