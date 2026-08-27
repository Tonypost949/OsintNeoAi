$testResults = @()

function Test-Requirement {
    param([string]$Doc, [string]$File, [string]$Pattern, [string]$Desc)
    $content = Get-Content -Raw -Path $File
    $matched = [regex]::IsMatch($content, $Pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    $obj = [PSCustomObject]@{
        Document = $Doc
        Requirement = $Desc
        Status = if ($matched) { "PASS" } else { "FAIL" }
    }
    return $obj
}

$f2 = "C:\OsintNeoAi\evidence\official_court_records\02_HCD_Notice_of_Violation_Surplus_Land_Act.md"
$f6 = "C:\OsintNeoAi\evidence\official_court_records\06_JL_Investigation_Anaheim_Forensic_Audit_Report.md"
$f7 = "C:\OsintNeoAi\evidence\official_court_records\07_Anaheim_City_Council_Stadium_Voidance_Resolution_2022_064.md"

# Tests for 02_HCD_Notice_of_Violation_Surplus_Land_Act.md
$testResults += Test-Requirement "Exhibit 02 (HCD)" $f2 "54220" "Surplus Land Act § 54220"
$testResults += Test-Requirement "Exhibit 02 (HCD)" $f2 "54221" "Declaration Requirement § 54221"
$testResults += Test-Requirement "Exhibit 02 (HCD)" $f2 "54222" "Notice of Availability § 54222"
$testResults += Test-Requirement "Exhibit 02 (HCD)" $f2 "54234" "Rejection of Grandfathering § 54234"
$testResults += Test-Requirement "Exhibit 02 (HCD)" $f2 "54230\.5" "Civil Penalty Statute § 54230.5"
$testResults += Test-Requirement "Exhibit 02 (HCD)" $f2 "96,000,000" "$96M Civil Penalty Calculation"
$testResults += Test-Requirement "Exhibit 02 (HCD)" $f2 "60-day" "60-Day Cure Requirement"
$testResults += Test-Requirement "Exhibit 02 (HCD)" $f2 "Megan Kirkeby" "Signatory Officer Megan Kirkeby"

# Tests for 07_Anaheim_City_Council_Stadium_Voidance_Resolution_2022_064.md
$testResults += Test-Requirement "Exhibit 07 (Res 2022-064)" $f7 "Resolution No\. 2022-064" "Resolution No. 2022-064"
$testResults += Test-Requirement "Exhibit 07 (Res 2022-064)" $f7 "May 24, 2022" "May 24, 2022 Enactment Date"
$testResults += Test-Requirement "Exhibit 07 (Res 2022-064)" $f7 "Unanimous" "Unanimous Roll Call Vote"
$testResults += Test-Requirement "Exhibit 07 (Res 2022-064)" $f7 "320,000,000" "$320M Transaction Voidance"
$testResults += Test-Requirement "Exhibit 07 (Res 2022-064)" $f7 "50,000,000" "$50M Escrow Deposit Refund"
$testResults += Test-Requirement "Exhibit 07 (Res 2022-064)" $f7 "SRB Management" "SRB Management Co. LLC"
$testResults += Test-Requirement "Exhibit 07 (Res 2022-064)" $f7 "Brown Act" "Brown Act Violations"
$testResults += Test-Requirement "Exhibit 07 (Res 2022-064)" $f7 "54952\.2" "Serial Meetings § 54952.2"

# Tests for 06_JL_Investigation_Anaheim_Forensic_Audit_Report.md
$testResults += Test-Requirement "Exhibit 06 (JL Audit)" $f6 "JL Group" "JL Group LLC"
$testResults += Test-Requirement "Exhibit 06 (JL Audit)" $f6 "353 Pages" "353-Page Report Scope"
$testResults += Test-Requirement "Exhibit 06 (JL Audit)" $f6 "Clay M\. Smith" "Hon. Clay M. Smith Oversight"
$testResults += Test-Requirement "Exhibit 06 (JL Audit)" $f6 "1,500,000" "$1.5M COVID Relief / AEDF Diversion"
$testResults += Test-Requirement "Exhibit 06 (JL Audit)" $f6 "Anaheim Economic Development Foundation" "AEDF Entity"
$testResults += Test-Requirement "Exhibit 06 (JL Audit)" $f6 "Anaheim First" "Anaheim First Data-Mining Program"
$testResults += Test-Requirement "Exhibit 06 (JL Audit)" $f6 "250,000" "$250k/yr Program Funding"
$testResults += Test-Requirement "Exhibit 06 (JL Audit)" $f6 "cover story" "Fraudulent Cover Story"
$testResults += Test-Requirement "Exhibit 06 (JL Audit)" $f6 "Public Records Act|CPRA" "CPRA Evidence Destruction"

$testResults | Format-Table -AutoSize
