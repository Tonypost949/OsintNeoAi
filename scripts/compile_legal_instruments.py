import os
import json
from datetime import datetime

BRIEFINGS_DIR = r"C:\OsintNeoAi\briefings"
EVIDENCE_DIR = r"C:\OsintNeoAi\evidence"
os.makedirs(BRIEFINGS_DIR, exist_ok=True)
os.makedirs(EVIDENCE_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. EMAIL EVIDENTIARY CHRONOLOGY & COURT DOCKET CROSS-MATCH INDEX
# -------------------------------------------------------------
email_index_md = f"""# 📧 EMAIL EVIDENTIARY CHRONOLOGY & DOCKET CROSS-MATCH INDEX
**Case Docket:** `30-2021-01201327-CL-UD-CJC` (*Woodbridge Meadows Apartments LLC v. Anthony Dimarcello*)  
**Court:** Superior Court of California, County of Orange — Central Justice Center  
**Audit Standard:** Extrinsic Fraud & Due Diligence Rebuttal (Cal. CCP § 473.5 / § 473(d))  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  

---

## 1. EXECUTIVE PURPOSE: PROVING EXTRINSIC FRAUD

To obtain an **Order to Serve Summons by Posting** (ROA #9, 06/02/2021), Plaintiff counsel (`Arden Hoang` / `Ruzicka, Wallace & Coughlin LLP`) submitted a declaration asserting under penalty of perjury that Defendant could not be located or served despite "diligent efforts."

The contemporaneous email record directly rebuts this sworn assertion, proving that:
1. Management (`Vichal Nunen`), leasing staff, and counsel possessed active, functioning direct email channels with Defendant.
2. Defendant was actively communicating regarding tenancy, habitability, and COVID-19 relief during the exact periods Plaintiff claimed "inability to locate."
3. Bypassing personal service was a deliberate tactic to engineer a **shadow default** and avoid judicial scrutiny of COVID-19 moratorium defenses.

---

## 2. CHRONOLOGICAL CROSS-MATCH MATRIX

| Date Window | Contemporaneous Email / Protected Activity | Corresponding Court Docket Action (ROA #) | Evidentiary Impact & Fraud Hook |
| :--- | :--- | :--- | :--- |
| **March 2021 – May 2021** | Emails exchanged regarding tenancy, habitability grievances, and COVID-19 financial distress declarations. | **05/18/2021 (ROA #1-4):** Plaintiff files Unlawful Detainer Complaint. | Proves Plaintiff had active email contact info prior to filing suit. |
| **May 19 – June 2, 2021** | Written inquiries and correspondence regarding lease terms and rental assistance status. | **06/02/2021 (ROA #9-10):** Plaintiff files *Application & Order to Serve by Posting*. | **SMOKING GUN (EXTRINSIC FRAUD):** Plaintiff falsely claimed Defendant could not be reached, concealing active email communications from the court. |
| **June 3 – June 29, 2021** | Emails regarding ongoing rental operations and occupancy. | **06/29/2021 (ROA #18-26):** Plaintiff rushes *Clerk's Default Judgment* and *Writ of Possession*. | Deprived Defendant of actual notice and 5-day statutory response window (Cal. CCP § 1167). |
| **July – August 2021** | Written objections sent to management regarding premature lockout threats and lack of hearing. | **08/04/2021:** Sheriff Lockout executed; **08/20/2021 (ROA #28):** Defendant files 32-page *Ex Parte Application to Vacate Default*. | Established retaliatory animus under Cal. Civ. Code § 1942.5. |
| **August 20, 2021 (4:29 PM)** | Defendant serves Ex Parte Application for August 23 hearing in Dept C61. | **08/20/2021 (ROA #37):** Plaintiff files emergency **CCP § 170.6 Peremptory Challenge striking Judge Carmen Luege**. | Tactical bad-faith judge disqualification to prevent adjudication of the motion to vacate. |
| **Dec 2021 – Feb 2022** | Ongoing dispute correspondence regarding property and tenancy status. | **12/03/2021 (ROA #45-51) & 01/04/2022 (ROA #54-60):** Plaintiff files back-to-back duplicate Court Default Judgments. | **VOID AB INITIO:** Re-entering defaults on an already-disposed case without notice constitutes ongoing fraud on the tribunal. |

---

## 3. STATUTORY SUMMARY OF PROVED DEFECTS

* **Extrinsic Fraud Established:** Under *In re Marriage of Stevenot* (1984) 154 Cal.App.3d 1051, concealing the opposing party's known communication channels to obtain service by posting is classic extrinsic fraud requiring complete vacatur.
* **Per Se Retaliation (Cal. Civ. Code § 1942.5):** The close proximity between written complaints and eviction filings creates an unrebutted statutory presumption of retaliatory motive.
"""

# -------------------------------------------------------------
# 2. FORMAL NOTICE OF MOTION AND MOTION TO VACATE VOID JUDGMENTS (CCP § 473(d))
# -------------------------------------------------------------
motion_md = f"""# ⚖️ NOTICE OF MOTION AND MOTION TO VACATE VOID DEFAULT JUDGMENTS
**Court:** Superior Court of California, County of Orange — Central Justice Center  
**Case Number:** `30-2021-01201327-CL-UD-CJC`  
**Plaintiff:** WOODBRIDGE MEADOWS APARTMENTS LLC DBA WOODBRIDGE  
**Defendant:** ANTHONY DIMARCELLO  
**Statutory Basis:** California Code of Civil Procedure § 473(d), § 473.5, and the Inherent Inherent Power of the Court  

---

```
SUPERIOR COURT OF CALIFORNIA, COUNTY OF ORANGE
CENTRAL JUSTICE CENTER

WOODBRIDGE MEADOWS APARTMENTS LLC,  )  Case No.: 30-2021-01201327-CL-UD-CJC
                                   )  
            Plaintiff,             )  NOTICE OF MOTION AND MOTION TO
                                   )  VACATE VOID CLERK DEFAULT JUDGMENT
    vs.                            )  AND DUPLICATE COURT DEFAULT
                                   )  JUDGMENTS; MEMORANDUM OF POINTS
ANTHONY DIMARCELLO, and DOES 1-5,  )  AND AUTHORITIES; DECLARATION
                                   )  
            Defendants.            )  [Cal. Code Civ. Proc. §§ 473(d), 473.5]
___________________________________)
```

## TO PLAINTIFF AND ITS ATTORNEYS OF RECORD:
**PLEASE TAKE NOTICE** that on [Date], at [Time], or as soon thereafter as the matter may be heard in Department C61 of the above-entitled Court, located at 700 Civic Center Drive West, Santa Ana, CA 92701, Defendant **ANTHONY DIMARCELLO** will and hereby does move this Court for an Order **VACATING, EXPUNGING, AND SETTING ASIDE**:
1. The *Clerk's Default Judgment* entered on **June 29, 2021** (ROA #26);
2. The *Court Default Judgment* entered on **December 22, 2021** (ROA #51);
3. The *Second Court Default Judgment* entered on **February 4, 2022** (ROA #60); and
4. The underlying *Order to Serve Summons by Posting* entered on **June 02, 2021** (ROA #10).

---

## MEMORANDUM OF POINTS AND AUTHORITIES

### I. THE JUDGMENTS ARE VOID ON THE FACE OF THE RECORD (CCP § 473(d))
California Code of Civil Procedure § 473(d) provides that the court may, on motion of either party or on its own motion, *"set aside any void judgment or order."*

A judgment is void on its face when the court lacked fundamental jurisdiction over the subject matter or parties. In *Heidary v. Yadollahi* (2002) 99 Cal.App.4th 857, the Court of Appeal established that once a court enters a final default judgment, its jurisdiction over that claim is exhausted (*functus officio*). 

Here, the official Register of Actions demonstrates a fatal jurisdictional defect: Plaintiff obtained a Clerk Default Judgment disposing of the action on **June 29, 2021** (ROA #26), and thereafter, without moving to set aside that judgment, submitted successive applications for *Court Default Judgments* on **December 03, 2021** (ROA #45) and **January 04, 2022** (ROA #54). The entry of multiple conflicting default judgments on the exact same cause of action is a fundamental nullity rendering all subsequent orders **void ab initio** (*Rochin v. Pat Johnson Manufacturing Co.* (1998) 67 Cal.App.4th 1228).

---

### II. EXTRINSIC FRAUD IN SERVICE BY POSTING (CCP § 473.5)
Under California Code of Civil Procedure § 473.5, when service of a summons has not resulted in actual notice in time to defend, the defendant is entitled to have the default set aside.

Plaintiff secured an *Order to Serve Summons by Posting* (ROA #9-10) by submitting declarations claiming Defendant could not be located. However, contemporaneous email records establish that Plaintiff's property manager (`Vichal Nunen`) and leasing staff were in active, regular email communication with Defendant throughout May and June 2021. Concealing known electronic communication channels from the court to obtain an ex parte posting order constitutes **extrinsic fraud on the tribunal** (*In re Marriage of Stevenot* (1984) 154 Cal.App.3d 1051; *Greene v. Lindsey* (1982) 456 U.S. 444).

---

### III. VIOLATION OF COVID-19 TENANT RELIEF ACT (CAL. CCP § 1179.03)
The action was initiated during the statutory protections of the California COVID-19 Tenant Relief Act (AB 3088 / SB 91). Plaintiff failed to strictly comply with the mandatory 15-day statutory notice and declaration filing requirements, rendering the court without jurisdiction to enter default.

---

### IV. CONCLUSION
For the foregoing reasons, Defendant respectfully requests that the Court enter an Order vacating all default entries and default judgments, quashing the writ of possession, and restoring the matter for full adjudication on the merits.

Dated: {datetime.now().strftime('%B %d, %Y')}

Respectfully submitted,

_____________________________
ANTHONY DIMARCELLO, Defendant in Pro Per
"""

# -------------------------------------------------------------
# 3. CIVIL RICO & WHISTLEBLOWER RETALIATION COMPLAINT OUTLINE (18 U.S.C. § 1964 / 18 U.S.C. § 1512)
# -------------------------------------------------------------
rico_md = f"""# ⚖️ CIVIL RICO & WHISTLEBLOWER RETALIATION COMPLAINT DRAFT
**Jurisdiction:** United States District Court for the Central District of California (Southern Division - Santa Ana)  
**Governing Law:** Racketeer Influenced and Corrupt Organizations Act (18 U.S.C. §§ 1961–1968), Federal False Claims Act Whistleblower Protection (31 U.S.C. § 3730(h)), California Whistleblower Protection Act (Cal. Labor Code § 1102.5 / Gov. Code § 12653)  
**Relator / Plaintiff:** ANTHONY DIMARCELLO  
**Defendants:** WOODBRIDGE MEADOWS APARTMENTS LLC; RUZICKA, WALLACE & COUGHLIN, LLP (n/k/a WALLACE, RICHARDSON, SONTAG & LE, LLP); ARDEN HOANG, ESQ.; RICHARD S. SONTAG, ESQ.; VICHAL NUNEN; HELPING OF MENTALLY ILL EXPERIENC (HOMI); MHI REAL COMPANY; MERCY HOUSE LIVING CENTERS; and DOES 1–100, inclusive.  

---

## 1. STATEMENT OF JURISDICTION & VENUE
1. This action arises under the laws of the United States, specifically **18 U.S.C. § 1964(c) (Civil RICO)**, **18 U.S.C. § 1962 (Racketeering)**, and **31 U.S.C. § 3730(h) (False Claims Act Anti-Retaliation)**.
2. Supplemental jurisdiction over state law claims exists pursuant to **28 U.S.C. § 1367**.
3. Venue is proper in the Central District of California pursuant to **18 U.S.C. § 1965** and **28 U.S.C. § 1391(b)** because the Defendants reside, operate, and executed the racketeering acts within the County of Orange.

---

## 2. THE ASSOCIATION-IN-FACT ENTERPRISE (18 U.S.C. § 1961(4))
The Defendants functioned as an ongoing, structured **Association-in-Fact Enterprise** ("The Orange County Municipal & Real Estate Conduit Enterprise") with a shared purpose to:
* Extract municipal, non-profit, and residential equity through fraudulent conveyances and tax-exempt shell entities (`HOMI` / `1601 Dove St`);
* Secure uncontested unlawful detainer judgments and evictions through shadow process and fraudulent court declarations; and
* Systematically intimidate, tamper with, and retaliate against tenant-whistleblowers who questioned or exposed municipal irregularities, environmental hazards, or non-profit self-dealing.

---

## 3. PREDICATE ACTS OF RACKETEERING (18 U.S.C. § 1961(1))

### PREDICATE ACT 1: RETALIATORY WITNESS TAMPERING & INTIMIDATION (18 U.S.C. § 1512(d))
* Defendants engaged in intentional, retaliatory conduct designed to harass, intimidate, and prevent Plaintiff from providing information to federal and state authorities regarding non-profit misuse and municipal housing violations.
* When Plaintiff documented protected grievances via email, Defendants retaliated by filing a fraudulent eviction, obtaining void shadow defaults, executing an unauthorized lockout, and striking assigned judges at 4:29 PM (ROA #37).

### PREDICATE ACT 2: WIRE FRAUD (18 U.S.C. § 1343 / § 1346)
* Transmitting fraudulent electronic court filings, falsified due diligence declarations via CEB/OneLegal portals, and routing municipal funds through consulting shells.

### PREDICATE ACT 3: MAIL FRAUD (18 U.S.C. § 1341)
* Utilizing the U.S. Postal Service to execute fraudulent statutory notices, summons postings, and IRS tax filings (`Dog's Day Productions SS-4`).

### PREDICATE ACT 4: MONEY LAUNDERING (18 U.S.C. §§ 1956, 1957)
* Structuring monetary transactions derived from unlawful non-profit inurement into residential property flips exceeding $1,215,000 at `8 Lakeview, Irvine`.

---

## 4. CAUSES OF ACTION

### COUNT I: SUBSTANTIVE CIVIL RICO (18 U.S.C. § 1962(c))
* Defendants conducted and participated in the conduct of the enterprise through a continuous pattern of racketeering activity comprising multiple predicate acts over a multi-year period, proximately causing severe injury to Plaintiff's property and business.

### COUNT II: RICO CONSPIRACY (18 U.S.C. § 1962(d))
* Defendants knowingly agreed and conspired to facilitate the commission of the predicate acts of mail fraud, wire fraud, money laundering, and witness tampering.

### COUNT III: FEDERAL FALSE CLAIMS ACT WHISTLEBLOWER RETALIATION (31 U.S.C. § 3730(h))
* Defendants harassed, displaced, and retaliated against Plaintiff because of lawful acts in furtherance of investigating public funding and municipal program violations.

### COUNT IV: CALIFORNIA WHISTLEBLOWER RETALIATION (CAL. LABOR CODE § 1102.5 / GOV. CODE § 12653)
* Retaliatory adverse actions taken against Plaintiff for disclosing violations of state and federal statutes to public authorities.

### COUNT V: STATUTORY RETALIATORY EVICTION (CAL. CIV. CODE § 1942.5)
* Instituting and maintaining an eviction action within 180 days of Plaintiff exercising protected rights under California law.

---

## 5. PRAYER FOR RELIEF
WHEREFORE, Plaintiff prays for judgment against Defendants, jointly and severally, as follows:
1. **Treble Damages (3x):** An award of three times actual property and economic damages pursuant to **18 U.S.C. § 1964(c)**;
2. **Double Damages:** An award of 200% damages pursuant to **31 U.S.C. § 3730(h)**;
3. **Statutory & Punitive Damages:** Punitive damages under California Civil Code § 1942.5 and Civil Code § 3294;
4. **Mandatory Attorney's Fees & Costs:** Full reimbursement of litigation costs and attorney's fees;
5. **Injunctive Relief:** An order declaring all state court default judgments void and expunging all records of the unlawful detainer; and
6. Such other and further relief as the Court deems just and proper.

Dated: {datetime.now().strftime('%B %d, %Y')}

Respectfully submitted,

_____________________________
ANTHONY DIMARCELLO, Plaintiff in Pro Per
"""

# Write all three files
with open(os.path.join(EVIDENCE_DIR, "EMAIL_EVIDENTIARY_CHRONOLOGY_INDEX.md"), "w", encoding="utf-8") as f:
    f.write(email_index_md)
print("✓ Created evidence/EMAIL_EVIDENTIARY_CHRONOLOGY_INDEX.md")

with open(os.path.join(BRIEFINGS_DIR, "FORMAL_MOTION_TO_VACATE_VOID_JUDGMENT_CCP_473D.md"), "w", encoding="utf-8") as f:
    f.write(motion_md)
print("✓ Created briefings/FORMAL_MOTION_TO_VACATE_VOID_JUDGMENT_CCP_473D.md")

with open(os.path.join(BRIEFINGS_DIR, "CIVIL_RICO_AND_WHISTLEBLOWER_COMPLAINT_DRAFT.md"), "w", encoding="utf-8") as f:
    f.write(rico_md)
print("✓ Created briefings/CIVIL_RICO_AND_WHISTLEBLOWER_COMPLAINT_DRAFT.md")
