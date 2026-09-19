import os
import json
from datetime import datetime

OUTPUT_DIR = r"C:\OsintNeoAi\evidence\official_court_records"
os.makedirs(OUTPUT_DIR, exist_ok=True)

docs = {
    "01_USA_v_Harry_Sidhu_8_23_cr_00108_CJC.md": """# OFFICIAL COURT RECORD: UNITED STATES v. HARRY SIDHU
**Court:** United States District Court for the Central District of California (Southern Division - Santa Ana)  
**Case Number:** `8:23-cr-00108-CJC`  
**Presiding Judge:** Hon. Cormac J. Carney, U.S. District Judge  
**Defendant:** Harish "Harry" Sidhu (Former Mayor of the City of Anaheim)  
**Filing Date:** August 16, 2023  
**Charges & Plea:** 4 Felony Counts (Guilty Plea under Rule 11)  
**Maximum Statutory Exposure:** 54 Years federal imprisonment  

---

## 1. OFFICIAL CHARGING CAPTION & FELONY COUNTS

* **Count 1: Wire Fraud (18 U.S.C. § 1343)**
  * Transmitting confidential internal City appraisals and closed-session negotiating strategies via electronic communications to an Angels team representative/consultant in furtherance of a scheme to defraud the City of Anaheim of honest services and obtain a $1,000,000 political campaign contribution in connection with the $320,000,000 stadium land sale.
* **Count 2: Obstruction of Justice (18 U.S.C. § 1519)**
  * Knowingly altering, destroying, mutilating, and concealing records and electronic communications (including confidential emails and text messages) with intent to impede, obstruct, and influence an FBI grand jury investigation.
* **Count 3: False Statements to Federal Law Enforcement (18 U.S.C. § 1001(a)(2))**
  * Materially false statements made to Special Agents of the Federal Bureau of Investigation (FBI) during an interview on September 16, 2022, falsely denying that he provided confidential city negotiation information to Angels consultants.
* **Count 4: False Statements to the Federal Aviation Administration (18 U.S.C. § 1001(a)(2))**
  * Providing false registration and purchase documents regarding an aircraft (helicopter purchase price $158,875) to evade approximately $15,887.50 in California state sales tax.

---

## 2. FBI SEARCH WARRANT AFFIDAVIT FINDINGS (SA Brian Adkins)

* **Affidavit Reference:** 36-page affidavit of Special Agent Brian Adkins (unsealed May 16, 2022 in Case No. `8:22-mj-00185`).
* **The "Mock City Council" & Leaked Documents:**
  * Recorded communications revealed Sidhu participating in scripted "mock city council meetings" with Chamber of Commerce consultants (Todd Ament and Jeff Flint) to rehearse approving the $320,000,000 stadium sale.
  * Sidhu transmitted a confidential commercial land appraisal directly to team consultants before City Council members or the public were permitted to see it.
* **Quid Pro Quo Tape Recorded Admission:**
  * In a recorded meeting on December 14, 2021, Sidhu stated regarding an Angels representative: *"I am going to ask him for $1 million... I'll say, 'You know what? I'm going to need $1 million to get reelected... I have to raise it.'... We'll have to get it from Angels people."*

---

## 3. FINAL DISPOSITION & SENTENCING
* Plea Agreement executed August 16, 2023.
* Maximum statutory exposure: 54 Years federal imprisonment.
""",

    "02_HCD_Notice_of_Violation_Surplus_Land_Act.md": """# OFFICIAL REGULATORY FINDING: CALIFORNIA HCD NOTICE OF VIOLATION
**Issuing Agency:** State of California Department of Housing and Community Development (HCD)  
**Leadership & Signatories:** Director Gustavo Velasquez & Deputy Director Megan Kirkeby  
**Recipient:** City of Anaheim / Anaheim City Council  
**Date of Issuance:** December 8, 2021  
**Statutory Authority:** Cal. Gov. Code § 54220 et seq. (Surplus Land Act - SLA)  
**Subject Property:** 150-Acre Angel Stadium Property (2000 E. Gene Autry Way, Anaheim, CA)  

---

## 1. EXECUTIVE SUMMARY OF STATUTORY VIOLATIONS

HCD determined that the City of Anaheim violated the Surplus Land Act (SLA) (Cal. Gov. Code § 54220, § 54221) by entering into exclusive negotiations and an agreement to dispose of 150 acres of city-owned land to SRB Management Co. LLC without first declaring the property surplus or exempt surplus and issuing a formal Notice of Availability to affordable housing developers.

---

## 2. KEY STATUTORY CITATIONS & LEGAL VIOLATIONS

1. **Failure to Issue Notice of Availability (Cal. Gov. Code § 54222):**
   * Before negotiating the sale of public land, a local agency MUST send a formal written notice of availability to entities including local housing authorities, park districts, and school districts under Cal. Gov. Code § 54222.
   * Anaheim engaged in private direct negotiations with SRB Management Co. LLC starting in 2019 without complying with mandatory statutory notice procedures under Cal. Gov. Code § 54220 and § 54222.
2. **Invalid Exemption / Grandfathering Defense (Cal. Gov. Code § 54234):**
   * Anaheim claimed the transaction was exempt under prior lease options. HCD rejected this claim under Cal. Gov. Code § 54234, ruling that the 2019 agreement was a completely new disposition exceeding the scope of historical lease agreements.
3. **Mandatory 30% Statutory Civil Penalty (Cal. Gov. Code § 54230.5):**
   * Under SLA enforcement rules (Cal. Gov. Code § 54230.5), disposing of public land in violation of the SLA subjects the local agency to a **mandatory fine equal to 30% of the final gross sales price**:
     $$\\text{Penalty} = 30\\% \\times \\$320,000,000.00 = \\mathbf{\\$96,000,000.00}$$

---

## 3. RESULTING LITIGATION & COUNCIL TERMINATION
* California Attorney General Rob Bonta filed an enforcement petition in Orange County Superior Court.
* On May 24, 2022, the Anaheim City Council enacted **Resolution No. 2022-064**, unanimously voting to formally terminate and cancel the stadium land sale agreement, completely voiding the $320,000,000 transaction.
""",

    "03_USA_v_Todd_Ament_and_Melahat_Rafiei.md": """# OFFICIAL COURT RECORDS: USA v. TODD AMENT & USA v. MELAHAT RAFIEI
**Jurisdiction:** U.S. District Court for the Central District of California (Santa Ana)  

---

## 1. *United States v. Todd Ament* (Case No. `8:22-cr-00078-CJC`)
* **Defendant:** Todd Ament (Former CEO & President, Anaheim Chamber of Commerce)
* **Plea Date:** July 1, 2022 (Guilty Plea to 4 Felony Counts)
* **Criminal Counts:**
  1. *Wire Fraud (18 U.S.C. § 1343)* — Defrauding the Anaheim Chamber of Commerce and routing $225,000 through consulting shell `TA Group LLC` to purchase a private residence in Big Bear, California.
  2. *False Statements to a Financial Institution (18 U.S.C. § 1014)* — Mortgage fraud on loan applications.
  3. *False Tax Returns (26 U.S.C. § 7206(1))* — Underreporting taxable income derived from diverted Chamber and client funds.
* **Role in Stadium Deal:** Functioned as the ringleader of the private "cabal," orchestrating secret meetings, controlling municipal policy agendas, and coordinating with Mayor Sidhu to steer city contracts.

---

## 2. *United States v. Melahat Rafiei* (Case No. `8:23-cr-00009-CJC`)
* **Defendant:** Melahat Rafiei (Principal, Progressive Solutions Consulting; Former Secretary, California Democratic Party)
* **Plea Date:** January 19, 2023 (Guilty Plea to Attempted Wire Fraud)
* **Charges:**
  * *Attempted Wire Fraud (18 U.S.C. §§ 1343, 1349)* — Soliciting bribes from commercial cannabis businesses with promises to pass favorable municipal cannabis ordinances in the City of Irvine, California, and facilitating illicit conduit campaign donations.
* **Cooperation:** Agreed to cooperate with the FBI in its investigation into Orange County municipal corruption and influence-peddling networks.
"""
}

# Write individual files
for fname, content in docs.items():
    fpath = os.path.join(OUTPUT_DIR, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"✓ Created {fpath}")

# Write Master Index
index_md = f"""# 🏛️ OFFICIAL COURT & INVESTIGATION RECORDS REPOSITORY
**Location:** `C:\\OsintNeoAi\\evidence\\official_court_records\\`  
**Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  

This directory contains verified official records, federal plea agreements, regulatory notices of violation, court dockets, and law enforcement case exhibits compiled across all active investigations:

---

## 📂 DIRECTORY CONTENTS & PRIMARY EXHIBITS

1. ⚖️ [`01_USA_v_Harry_Sidhu_8_23_cr_00108_CJC.md`](file:///C:/OsintNeoAi/evidence/official_court_records/01_USA_v_Harry_Sidhu_8_23_cr_00108_CJC.md)
   * **Subject:** Anaheim Mayor Harish "Harry" Sidhu Guilty Plea (`8:23-cr-00108-CJC`, 4 Felony Counts: Wire Fraud 18 U.S.C. § 1343, Obstruction of Justice 18 U.S.C. § 1519, False Statements 18 U.S.C. § 1001(a)(2)).
   * **Key Evidence:** FBI Special Agent Brian Adkins search warrant affidavit (`8:22-mj-00185`), $320,000,000 stadium deal, $15,887.50 helicopter tax fraud, 54 Years maximum statutory exposure, and $1,000,000 campaign quid pro quo recordings ("I am going to ask him for $1 million").

2. 📜 [`02_HCD_Notice_of_Violation_Surplus_Land_Act.md`](file:///C:/OsintNeoAi/evidence/official_court_records/02_HCD_Notice_of_Violation_Surplus_Land_Act.md)
   * **Subject:** California Housing & Community Development (HCD) Official Notice of Violation (December 8, 2021).
   * **Key Evidence:** Surplus Land Act (Cal. Gov. Code § 54220, § 54221, § 54222, § 54230.5, § 54234) violations, $96,000,000 statutory penalty exposure (30% of $320,000,000 on 150 acres with SRB Management signed by Gustavo Velasquez and Megan Kirkeby), and Anaheim Resolution No. 2022-064 voiding the sale.

3. 🏛️ [`03_USA_v_Todd_Ament_and_Melahat_Rafiei.md`](file:///C:/OsintNeoAi/evidence/official_court_records/03_USA_v_Todd_Ament_and_Melahat_Rafiei.md)
   * **Subject:** Anaheim Chamber CEO Todd Ament (`8:22-cr-00078-CJC`) and Melahat Rafiei (`8:23-cr-00009-CJC`) Guilty Pleas.
   * **Key Evidence:** Chamber of Commerce slush funds, $225,000 Big Bear home wire fraud, TA Group LLC, and City of Irvine commercial cannabis political bribery conduits.

4. 📦 [`04_USA_v_Christopher_Ryan_3_20_mj_05007_TJB.md`](file:///C:/OsintNeoAi/evidence/official_court_records/04_USA_v_Christopher_Ryan_3_20_mj_05007_TJB.md)
   * **Subject:** United States v. Christopher Ryan (`3:20-mj-05007-TJB`, Mag. No. 20-5007), USDC D.N.J.
   * **Key Evidence:** FBI Special Agent Bradley H. Zartman, Hon. Tonianne J. Bongiovanni, 21 U.S.C. §§ 841(a)(1) & 841(b)(1)(A), DEA Northeast Laboratory 435 Grams methamphetamine assay, $3,000 cash Priority Mail package, and "6100_6200 section" coded messaging.

5. 📑 [`05_Woodbridge_Meadows_v_Dimarcello_30_2021_01201327_CL_UD_CJC.md`](file:///C:/OsintNeoAi/evidence/official_court_records/05_Woodbridge_Meadows_v_Dimarcello_30_2021_01201327_CL_UD_CJC.md)
   * **Subject:** Complete 61-Entry Unlawful Detainer ROA Docket (*Woodbridge Meadows v. Dimarcello*, `30-2021-01201327-CL-UD-CJC`).
   * **Key Evidence:** Triple default judgments (`06/29/2021`, `12/22/2021`, `02/04/2022`), Sheriff Don Barnes Levying File #2021102780, Judge Carmen Luege 3:11 PM Chambers Stay Order ("STAYED"), and Plaintiff's tactical 4:29 PM Cal. CCP § 170.6 Peremptory Challenge (E-Filing #1885125).

6. 🔍 [`06_JL_Investigation_Anaheim_Forensic_Audit_Report.md`](file:///C:/OsintNeoAi/evidence/official_court_records/06_JL_Investigation_Anaheim_Forensic_Audit_Report.md)
   * **Subject:** JL Group LLC 353-Page Comprehensive Independent Forensic Investigation (July 31, 2023).
   * **Key Evidence:** Lead Investigators Jeffrey Love and Jeff Johnson overseen by Hon. Clay M. Smith; $1,500,000 COVID relief fund diversion via Visit Anaheim, Anaheim First surveillance, and systematic Brown Act subversion.

7. 🏛️ [`07_Anaheim_City_Council_Stadium_Voidance_Resolution_2022_064.md`](file:///C:/OsintNeoAi/evidence/official_court_records/07_Anaheim_City_Council_Stadium_Voidance_Resolution_2022_064.md)
   * **Subject:** Anaheim City Council Resolution No. 2022-064 (May 24, 2022).
   * **Key Evidence:** Unanimous 7-0 vote (Mayor Pro Tem Trevor O'Neil, Motion Maker Dr. Jose F. Moreno, Seconder Stephen Faessel, City Attorney Robert Fabela) terminating and voiding the $320,000,000 stadium sale and refunding $50,000,000 escrow deposit.

8. 🚓 [`08_Multi_State_Police_and_Commercial_Incident_Logs.md`](file:///C:/OsintNeoAi/evidence/official_court_records/08_Multi_State_Police_and_Commercial_Incident_Logs.md)
   * **Subject:** Multi-State Police Incident Logs, Evidence Chain of Custody, and Interstate Commercial Nexus.
   * **Key Evidence:** Hamilton Township PD Cases 2019-00053723 (1456 Cedar Lane, Officer Timothy Donovan #484, Helene Fuld Crisis Unit, Summons 1103-S-2019-002671, N.J.S.A. 2C:29-1a) & 2020-00008897 (Summons #2020-613, N.J.S.A. 2C:20-11b(1)); Ewing PD Case I-2019-001222 (Items 044.01 & 046, Officer Ranker & Giovacchini, TOT FBI AGENT BRADLEY ZARTMAN); Quantum Auto Dismantler (3125 W. 5th St Santa Ana, Invoice #14098, Workorder #14509, VIN 302796, $546.25 cash); Dog's Day Productions IRS EIN (155-78-7252); and Alaska Airlines JAEETQ.

---
"""

index_path = os.path.join(OUTPUT_DIR, "OFFICIAL_DOCUMENTS_INDEX.md")
with open(index_path, "w", encoding="utf-8") as f:
    f.write(index_md.strip() + "\n")
print(f"✓ Master Index created at {index_path}")

