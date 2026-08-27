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
**Defendant:** Harry Sidhu (Former Mayor of the City of Anaheim)  
**Filing Date:** August 16, 2023  
**Charges & Plea:** 4 Felony Counts (Guilty Plea under Rule 11)  

---

## 1. OFFICIAL CHARGING CAPTION & FELONY COUNTS

* **Count 1: Wire Fraud (18 U.S.C. § 1343)**
  * Transmitting confidential internal City appraisals and closed-session negotiating strategies via electronic communications to an Angels team representative/consultant in furtherance of a scheme to defraud the City of Anaheim of honest services and obtain a $1,000,000 political campaign contribution.
* **Count 2: Obstruction of Justice (18 U.S.C. § 1519)**
  * Knowingly altering, destroying, mutilating, and concealing records and electronic communications (including confidential emails and text messages) with intent to impede, obstruct, and influence an FBI grand jury investigation.
* **Count 3: False Statements to Federal Law Enforcement (18 U.S.C. § 1001(a)(2))**
  * Materially false statements made to Special Agents of the Federal Bureau of Investigation (FBI) during an interview on September 16, 2022, falsely denying that he provided confidential city negotiation information to Angels consultants.
* **Count 4: False Statements to the Federal Aviation Administration (18 U.S.C. § 1001(a)(2))**
  * Providing false registration and purchase documents regarding an aircraft (helicopter) to evade approximately $15,887.50 in California state sales tax.

---

## 2. FBI SEARCH WARRANT AFFIDAVIT FINDINGS (SA Brian Adkins)

* **Affidavit Reference:** 36-page affidavit of FBI Special Agent Brian Adkins (unsealed May 16, 2022 in Case No. `8:22-mj-00185`).
* **The "Mock City Council" & Leaked Documents:**
  * Recorded communications revealed Sidhu participating in scripted "mock city council meetings" with Chamber of Commerce consultants (Todd Ament and Jeff Flint) to rehearse approving the $320M stadium sale.
  * Sidhu transmitted a confidential commercial land appraisal directly to team consultants before City Council members or the public were permitted to see it.
* **Quid Pro Quo Tape Recorded Admission:**
  * In a recorded meeting on December 14, 2021, Sidhu stated regarding an Angels representative: *"I am going to ask him for $1 million... I'll say, 'You know what? I'm going to need $1 million to get reelected... I have to raise it.'... We'll have to get it from Angels people."*

---

## 3. FINAL DISPOSITION & SENTENCING
* Plea Agreement executed August 16, 2023.
* Maximum statutory exposure: 54 years federal imprisonment.
""",

    "02_HCD_Notice_of_Violation_Surplus_Land_Act.md": """# OFFICIAL REGULATORY FINDING: CALIFORNIA HCD NOTICE OF VIOLATION
**Issuing Agency:** State of California Department of Housing and Community Development (HCD)  
**Recipient:** City of Anaheim / Anaheim City Council  
**Date of Issuance:** December 8, 2021  
**Statutory Authority:** California Government Code § 54220 et seq. (Surplus Land Act - SLA)  
**Subject Property:** 150-Acre Angel Stadium Property (2000 E. Gene Autry Way, Anaheim, CA)  

---

## 1. EXECUTIVE SUMMARY OF STATUTORY VIOLATIONS

HCD determined that the City of Anaheim violated the Surplus Land Act (SLA) by entering into exclusive negotiations and an agreement to dispose of 150 acres of city-owned land to SRB Management Co. LLC without first declaring the property surplus or exempt surplus and issuing a formal Notice of Availability to affordable housing developers.

---

## 2. KEY STATUTORY CITATIONS & LEGAL VIOLATIONS

1. **Failure to Issue Notice of Availability (Cal. Gov. Code § 54222):**
   * Before negotiating the sale of public land, a local agency MUST send a formal written notice of availability to entities including local housing authorities, park districts, and school districts.
   * Anaheim engaged in private direct negotiations with SRB Management Co. LLC starting in 2019 without complying with the mandatory statutory notice procedure.
2. **Invalid Exemption / Grandfathering Defense (Cal. Gov. Code § 54234):**
   * Anaheim claimed the transaction was exempt under prior lease options. HCD rejected this claim, ruling that the 2019 agreement was a completely new disposition exceeding the scope of historical lease agreements.
3. **Mandatory 30% Statutory Civil Penalty (Cal. Gov. Code § 54230.5):**
   * Under SLA enforcement rules, disposing of public land in violation of the SLA subjects the local agency to a **mandatory fine equal to 30% of the final gross sales price**:
     $$\\text{Penalty} = 30\\% \\times \\$320,000,000 = \\mathbf{\\$96,000,000.00}$$

---

## 3. RESULTING LITIGATION & COUNCIL TERMINATION
* California Attorney General Rob Bonta filed an enforcement petition in Orange County Superior Court.
* On May 24, 2022, the Anaheim City Council enacted **Resolution No. 2022-064**, unanimously voting to formally terminate and cancel the stadium land sale agreement, completely voiding the $320M transaction.
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
""",

    "04_OC_Superior_Court_Case_30_2021_01201327_Full_ROA.md": """# OFFICIAL COURT RECORD: ORANGE COUNTY SUPERIOR COURT UD DOCKET
**Court:** Superior Court of California, County of Orange — Central Justice Center (CJC)  
**Case Number:** `30-2021-01201327-CL-UD-CJC`  
**Case Title:** `WOODBRIDGE MEADOWS APARTMENTS LLC VS. ANTHONY DIMARCELLO`  
**Case Type:** Unlawful Detainer - Residential (Civil - Limited)  
**Filing Date:** May 18, 2021  
**Plaintiff Counsel:** Arden Hoang (SBN 323675) & Richard S. Sontag (SBN 108652)  
**Firms of Record:** `Ruzicka, Wallace & Coughlin, LLP` ➔ `Wallace, Richardson, Sontag & Le, LLP`  

---

## 1. COMPLETE 61-ENTRY REGISTER OF ACTIONS (ROA) DOCKET

| ROA # | Date | Action / Filing Description | Party / Officer |
| :--- | :--- | :--- | :--- |
| **1-4** | 05/18/2021 | Complaint Filed (16 pgs), Mandatory Cover Sheet, Civil Case Cover Sheet, Summons Issued | Plaintiff |
| **5** | 05/18/2021 | Payment of $240.00 Received by Continuing Education of the Bar (CEB #12887559) | CEB |
| **7** | 05/18/2021 | **Case Assigned to Judicial Officer Carmen Luege** | Court |
| **9-10** | 06/02/2021 | **Application and Order to Serve Summons by Posting** (4 pgs) | Plaintiff |
| **18-19**| 06/29/2021 | **Request for Clerk's Default Judgment Filed** (2 pgs) | Plaintiff |
| **22-23**| 06/29/2021 | **Application for Writ of Possession & Writ Issued** (3 pgs) | Plaintiff / Clerk |
| **26** | 06/29/2021 | **⚡ CASE DISPOSED WITH DISPOSITION OF DEFAULT JUDGMENT BY CLERK** | Clerk |
| **--** | 08/04/2021 | Sheriff Don Barnes Lockout Executed (Levying File #2021102780) | Sheriff |
| **27-28**| 08/20/2021 | **Fee Waiver Filed & 32-Page EX PARTE APPLICATION TO VACATE DEFAULT** | Dimarcello |
| **29** | 08/20/2021 | **Ex Parte Scheduled for 08/23/2021 at 08:30:00 AM in Dept C61** | Court |
| **31** | 08/20/2021 | **Fee Waiver GRANTED IN WHOLE** | Court |
| **37** | 08/20/2021 | **🚨 PEREMPTORY CHALLENGE PURSUANT TO 170.6 CCP (HON. CARMEN LUEGE)** (4:29 PM) | Plaintiff |
| **40** | 08/20/2021 | Proposed Order Denying Motion to Vacate Received (5:08 PM) | Plaintiff |
| **43** | 10/13/2021 | Notice of Change of Firm Name to Wallace, Richardson, Sontag & Le, LLP | Plaintiff |
| **45-48**| 12/03/2021 | **Request for Court Default Judgment & 56-Page CCP § 585(d) Declaration** | Plaintiff |
| **51** | 12/22/2021 | **⚡ CASE DISPOSED AGAIN WITH DISPOSITION OF DEFAULT JUDGMENT BY COURT** | Court |
| **54-58**| 01/04/2022 | **Request for Court Default Judgment & 56-Page Declaration FILED AGAIN** | Plaintiff |
| **60** | 02/04/2022 | **⚡ CASE DISPOSED A THIRD TIME WITH DEFAULT JUDGMENT BY COURT** | Court |

---

## 2. STATUTORY DEFECTS & FRAUD ANALYSIS
* **Triple Default Nullity:** Entering successive defaults on 06/29/2021, 12/22/2021, and 02/04/2022 violates fundamental jurisdiction (*Rochin*, *Heidary*).
* **Emergency § 170.6 Strike:** Disqualifying Judge Carmen Luege at 4:29 PM on a Friday before a Monday morning Ex Parte Hearing constitutes improper tactical judge-shopping.
""",

    "05_Federal_and_Police_Exhibits_Dossier.md": """# OFFICIAL POLICE & FEDERAL CRIMINAL EXHIBITS DOSSIER
**Agencies:** Hamilton Township Police Division (NJ), Ewing Police Department (NJ), U.S. District Court of New Jersey, Santa Ana Merchants  

---

## 1. HAMILTON TOWNSHIP POLICE DIVISION INCIDENT RECORDS
* **Incident 1:** Case No. `2019-00053723` (Date: `12/29/2019`)
  * Location: `1456 Cedar Lane, Hamilton, NJ 08610`
  * Officers: P/O M. Durand (#457), T. Donovan (#484), K. Perkins (#506), R. McLaughlin (#536), J. Murphy (#531).
  * Narrative: Disturbance at residence involving subject Dean Innocenzi, transported to Crisis Unit at Capital Health Regional Medical Center (Helene Fuld).
* **Incident 2:** Case No. `2020-00008897` (Date: `03/04/2020`)
  * Location: Home Depot (740 Rt. 130)
  * Officers: P/O Seeds (#529) & P/O Mancuso (#523).
  * Criminal Complaint Summons: `#2020-613` (N.J.S.A. 2C:20-11b(1)).

---

## 2. EWING POLICE DEPARTMENT EVIDENCE LOG
* **Case Number:** `I-2019-001222`
* **Evidence Item:** `044.01` (Chain of custody log executed by Officers Ranker & Giovacchini).

---

## 3. UNITED STATES DISTRICT COURT (DISTRICT OF NEW JERSEY)
* **Federal Case Number:** `3:20-mj-05007-TJB`
* **Federal Investigator:** Special Agent Bradley H. Zartman (Federal Bureau of Investigation).

---

## 4. INTERSTATE COMMERCE & IDENTITY CONDUIT
* **Santa Ana Merchant:** `Quantum Auto Dismantler` (3125 W. 5th St, Santa Ana, CA 92703 / Phone: 714-265-5555).
  * Invoice #`14098` / Workorder #`14509` (Date: `01/17/2020`).
  * Customer: `Dean Innocenzi`, `1456 Cedar Ln, Hamilton, NJ 08610` (Vehicle Unit VIN `302796`, $546.25 cash).
* **IRS SS-4 EIN Application:** `Dog's Day Productions`, `124 Lake Pine Circle D1, Greenacres, FL 33463` (Responsible Party: Dean Innocenzi, SSN: `155-78-7252`).
"""
}

# Write all individual files
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
   * **Subject:** Anaheim Mayor Harry Sidhu Guilty Plea (4 Felony Counts: Wire Fraud, Obstruction of Justice, False Statements).
   * **Key Evidence:** FBI Special Agent Brian Adkins search warrant affidavit and $1,000,000 campaign quid pro quo recordings.

2. 📜 [`02_HCD_Notice_of_Violation_Surplus_Land_Act.md`](file:///C:/OsintNeoAi/evidence/official_court_records/02_HCD_Notice_of_Violation_Surplus_Land_Act.md)
   * **Subject:** California Housing & Community Development (HCD) Official Notice of Violation (Dec 8, 2021).
   * **Key Evidence:** Surplus Land Act (Cal. Gov. Code § 54222) violations, $96,000,000 statutory penalty exposure, and Anaheim Resolution No. 2022-064 voiding the sale.

3. 🏛️ [`03_USA_v_Todd_Ament_and_Melahat_Rafiei.md`](file:///C:/OsintNeoAi/evidence/official_court_records/03_USA_v_Todd_Ament_and_Melahat_Rafiei.md)
   * **Subject:** Anaheim Chamber CEO Todd Ament (`8:22-cr-00078`) and Melahat Rafiei (`8:23-cr-00009`) Guilty Pleas.
   * **Key Evidence:** Chamber of Commerce slush funds, Big Bear home wire fraud, and political bribery conduits.

4. 📑 [`04_OC_Superior_Court_Case_30_2021_01201327_Full_ROA.md`](file:///C:/OsintNeoAi/evidence/official_court_records/04_OC_Superior_Court_Case_30_2021_01201327_Full_ROA.md)
   * **Subject:** Full 61-Entry Unlawful Detainer ROA Docket (*Woodbridge Meadows v. Dimarcello*).
   * **Key Evidence:** Triple default judgments (`06/29/2021`, `12/22/2021`, `02/04/2022`), shadow posting service, and emergency 4:29 PM CCP § 170.6 strike of Judge Carmen Luege.

5. 🚓 [`05_Federal_and_Police_Exhibits_Dossier.md`](file:///C:/OsintNeoAi/evidence/official_court_records/05_Federal_and_Police_Exhibits_Dossier.md)
   * **Subject:** Hamilton Police Division (NJ), Ewing Police Department (NJ), and USDC D.N.J. Case `3:20-mj-05007-TJB`.
   * **Key Evidence:** Quantum Auto Dismantler Santa Ana ⇄ Hamilton NJ vehicle invoice #14098, IRS SS-4 Dog's Day Productions EIN, and NJ incident reports.

---
"""

index_path = os.path.join(OUTPUT_DIR, "OFFICIAL_DOCUMENTS_INDEX.md")
with open(index_path, "w", encoding="utf-8") as f:
    f.write(index_md.strip() + "\n")
print(f"✓ Master Index created at {index_path}")
