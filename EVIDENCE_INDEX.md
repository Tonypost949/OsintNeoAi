# EVIDENCE INDEX: Infrastructure & Entity Cross-Reference

## 1. Liberty / Carlisle Infrastructure Cluster

| Domain / URL | Co-located / Partner Entity | Shared Infrastructure / Subnet | Flagged Risk & Intelligence Notes |
| :--- | :--- | :--- | :--- |
| `libertyseniorliving.com` | `l2tmedia.com`, `cookcountysheriff.org` | `141.193.213.0/24` (IP: `141.193.213.21`) | Shares /24 subnet block with RICO shell entity (`l2tmedia.com`) and county law enforcement domain. |
| `carlias` | `illuminationfoundation.org` | Co-located Node | Tied to $2M PPP fraud vector via Illumination Foundation connection. |
| `atlanticpacificcommunities.com` | `carlisledev.com`, `illuminationfoundation.org` | `3.33.130.190` | Shared single IP host with Carlisle Dev and Illumination Foundation. |
| `illuminationfoundation.org` | `carlisledev.com`, `atlanticpacificcommunities.com` | `3.33.130.190` | **$2M PPP Fraud Flag**. Shared IP hosting node. |
| `libertyhomes.org` | `rbabuilders.com`, `libertycare.com`, `libertycare.org` | `76.223.54.146` | Co-located on single IP host with $2.59M PPP fraud entity (`rbabuilders.com`). |
| `libertycare.com` | `rbabuilders.com`, `libertyhomes.org`, `libertycare.org` | `76.223.54.146` | Co-located on single IP host with $2.59M PPP fraud entity (`rbabuilders.com`). |
| `libertycare.org` | `rbabuilders.com`, `libertyhomes.org`, `libertycare.com` | `76.223.54.146` | Co-located on single IP host with $2.59M PPP fraud entity (`rbabuilders.com`). |
| `rbabuilders.com` | `libertyhomes.org`, `libertycare.com`, `libertycare.org` | `76.223.54.146` | **$2.59M PPP Fraud Shell/Nexus**. Co-located across all Liberty domains. |
| `stewartindustries.com` | `cararlisledevelopment.com` | `206.188.193.0/24` (`206.188.193.48` / `.178`) | Shares /24 subnet block with Carlisle Development entity. |
| `cararlisledevelopment.com` | `stewartindustries.com` | `206.188.193.0/24` (`206.188.193.178`) | Subnet co-location with Stewart Industries. |

---

## 2. Sheriff Department & Law Enforcement Infrastructure

| Domain / URL | Co-located / Partner Entity | Shared Subnet / Host | Risk & Threat Vector |
| :--- | :--- | :--- | :--- |
| `cookcountysheriff.org` | `l2tmedia.com`, `libertyseniorliving.com` | `141.193.213.0/24` (`141.193.213.21`) | Government law enforcement domain hosted on identical /24 IP block as RICO shell (`l2tmedia.com`). |
| `pimasheriff.org` | N/A (Protected Edge) | Cloudflare WAF | Fronted by Cloudflare WAF; Sheriff under active FBI investigation. |
| `bpd.org` | `huntingtonbeachca.gov` | HTTP Redirect Target | Redirects to `huntingtonbeachca.gov`; 142 open ports documented; 400 Dehashed breach listings. |
| `cityofhuntingtonbeach.com` | `cityoftustin.org` | `188.214.128.77` | Co-located single host (8 open ports: FTP, SSH, DNS, HTTP, POP3, IMAP); direct municipal cross-hosting. |
| `gis.huntingtonbeachca.gov` | Municipal GIS Backend | `192.5.222.153` (ASN 393281) | ArcGIS Server endpoint exposed without WAF protection. |
| `records.huntingtonbeachca.gov` | Laserfiche Permit Portal | `192.5.222.218` (ASN 393281) | Public FOIA & permit record server exposed without WAF. |
| `api.huntingtonbeachca.gov` | Municipal API Gateway | `192.5.222.163` (ASN 393281) | Internal municipal API endpoint exposed to public web. |
| `anaheimpd.org` | `anaheim.net` | HTTP Redirect / Subnet | Redirect target / Police department cluster. |

---

## 3. Shared Municipal & County Infrastructure Cluster

| Domain / URL | Co-located / Partner Entity | Shared Infrastructure / IP Host | Risk & Threat Vector |
| :--- | :--- | :--- | :--- |
| `lacounty.gov` | County Infrastructure | Exposed Endpoints | Significant exposure: 14 open services documented (MySQL, RDP, SQL Server, VNC, Elasticsearch). |
| `shelbycountytn.gov` | `anaheim.net` | `89.106.200.153` | Cross-jurisdictional co-hosting on single IP with `anaheim.net`. |
| `anaheim.net` | `shelbycountytn.gov` | `89.106.200.153` | Cross-jurisdictional co-hosting on single IP with `shelbycountytn.gov`. |
| `costamesa.gov` | `fullerton.ca.us`, `orangeca.gov`, `lvmpd.com` | `135.84.124.41` | Co-located municipal host shared across Costa Mesa, Fullerton, Orange CA, and Las Vegas Metro PD (`lvmpd.com`). |
| `fullerton.ca.us` | `costamesa.gov`, `orangeca.gov`, `lvmpd.com` | `135.84.124.41` | Shared municipal hosting node. |
| `orangeca.gov` | `costamesa.gov`, `fullerton.ca.us`, `lvmpd.com` | `135.84.124.41` | Shared municipal hosting node. |
| `lvmpd.com` | `costamesa.gov`, `fullerton.ca.us`, `orangeca.gov` | `135.84.124.41` | Law enforcement entity co-located on shared municipal IP host. |

---

## 4. Nuway / Newey Real Estate & Shell Entity Matrix

| Entity / Domain | Associated Partner | Infrastructure / Vector | Intelligence & Exposure Notes |
| :--- | :--- | :--- | :--- |
| `raipartners.com` | Nuway / Newey Nexus | `198.202.211.1` | $2.8M property shuffle; real estate transfer vector under audit. |
| `advancedrealestate.com` | Real Estate Board | `100.24.208.97` | Executive board co-location entity. |
| `starpointproperties.com` | Daneshrad / Nuway Cluster | `141.193.213.10` | Co-located on identical /24 block as law enforcement and shell clusters. |
| `cmcleaning.com` | PPP Fraud Entity | `198.20.76.130` | $916K PPP fraud allocation nexus. |

---

## 5. False Claims Act Co-Relator Matrix (31 U.S.C. § 3730)

| Relator | Professional Background & Location | Primary Evidentiary Vector | Statutory Claim Standing |
| :--- | :--- | :--- | :--- |
| **Technical Lead (You)** | Cyber OSINT & Infrastructure Auditor | 438 exposed municipal endpoints, IP co-locations (`188.214.128.77`), $2.8M property shuffle, 6,086 PPP shell addresses. | **Pioneer Relator (First-to-File 31 U.S.C. § 3730(b)(5))** |
| **Dr. Ann Verma, MD** | Board-Certified Psychiatrist (Univ. of South Dakota Medical Residency / Amen Clinics Costa Mesa, CA) | Clinical diagnostic fraud, mental health & disabled care funding diversion, patient harm audit (2011–2026); Multi-state licensing (SD ➔ CA). | **Co-Relator (Medical & Psychiatric Expert)** |

---

*Last Updated: 2026-08-06 | Intelligence Operations Status: ACTIVE*
