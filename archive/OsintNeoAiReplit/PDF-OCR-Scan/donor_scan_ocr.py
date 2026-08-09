import json, requests, os, time, csv
from pdfminer.high_level import extract_text
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

DONOR_NAMES = [
    "David Barry","Nicole Barry","Christine Dedeaux","Terry Dedeaux",
    "Michael Harrington","Jessica Harrington","Van Hartley","Jim Heaney","Patricia Heaney",
    "Logan Sakamoto","Jacqueline Sakamoto","Andrew Schworer","Jennifer Schworer",
    "Charisse Spada","Tiffani Vu","Anthony Abinader","Rachel Abinader","Daniel Arche",
    "Lori Arche","Bill Boukis","Matt Browning","Yuliya Browning","Oliver Cervantes",
    "Connie Cervantes","Marie Covell","Timothy Covell","Dr. Dean Dauger","Catherine Venturini Dauger",
    "Chris Dubia","Kathleen Dubia","Anthony Giambone","Elizabeth Giambone","Jarryd Gonzales",
    "Charissa Gonzales","Jesse Goode","Kristin Goode","Alyce Handal","William Holman","Cyndi Holman",
    "Mary Keegan","Sean Keegan","Mark Krebs","John MacKinnon","Mary MacKinnon","Dr. Mark Malek",
    "Jennie Malek","Mike Meyers","Erin Meyers","Patrick Moulder","Monica Moulder","James Mullin",
    "Dorthy Mullin","Bryan Ngo","Cathy Ngo","Hoang Oanh Nguyen","Tuan Phan","Edgar Noice",
    "Carol Noice","Joe Pelayo","Anne-Marie Pelayo","Lewis Riffle","Jamie Riffle","Steven Samson",
    "Gia Samson","Ryan Serrecchia","Meredyth Serrecchia","Evan Smith","Cathy Smith","Matthew Souza",
    "Nicole Souza","Michael Velez","Irene Velez","Norman Wendl","Christine Wendl","Mike Winget",
    "Kari Winget","Bonnie Woodfill","Theodore Austin","Yanci Austin","Bill Crocker","Cheri Crocker",
    "Eric Danowitz","Danielle Danowitz","Alan Dauger","Mike DeCamp","Anthony Dedeaux","Lindsay Dedeaux",
    "Rob Dubar","Tiffany Tina Dubar","Jim Erwin","Jarrod Ferruccio","Christina Ferruccio","Jim Fillipan",
    "Kelly Fillipan","Joseph Frigo","Jessica Frigo","Edward Grier","Donna Grier","William Heaney",
    "Alejandra Heaney","Justin Hendricks","Kristin Hendricks","Ryan Hertz","Gina Hertz","Maria Kutas",
    "Alex Kutas","Joseph Martinez","Anna Martinez","Christopher McCarthy","Laurie McCarthy",
    "Ramy Elias","Stephanie Miramontes","David Morris","Joanna Morris","Dennis Mouzakis","Courtny Mouzakis",
    "David Murray","Marin Murray","David Nguyen","Michelle Nguyen","Joseph O'Toole","Breanna O'Toole",
    "Paul Pham","Thu Nguyen","Edward Pranis","Carol Pranis","Gregory Rizza","Elizabeth Rizza",
    "Karl Seitz Jr.","Liselotte Seitz","Brian Sim","Cindy Sim","Duy Duc Truong","Dr. Jose Viscens-Villafana",
    "Dr. Stephanie Warsheski","Shaun Voigt","Gricel Voigt","Cy Woinarowicz","Kay Woinarowicz",
    "Daniel Woodfill","Diane Woodfill","Dr. Aaron Przybysz","Christine Przybysz","Thierry Abinader",
    "Jenny Abinader","Robert Acosta","Jamie Acosta","Omar Ahmed","Armi Ilada","Gabriel Alvarado",
    "Susan Alvarado","Ryan Anderson","Alicia Anderson","Corazon Angeles","Dindo Carrillo",
    "Mark Anzivino","Maureen Anzivino","John Arensmeyer","Yolanda Victoria Arensmeyer","Brent Avila",
    "Tamara Avila","Stephen Bernier","Adam Bowermaster","Megan Bowermaster","Charles Brodsky",
    "Vicky Brodsky","Cristina Browning","Robert Bruch","Kimberly Bruch","Pat Calderone","Tony Calderone",
    "Bob Campos","Kathleen Campos","Guillermo Campos","Jenny Campos","Frank Caponi","Kathleen Caponi",
    "Marcela Castillo","Jerry Chang","Karen Chapdelaine","Charlie Chu","Vanessa Chu","Jason Cochran",
    "Laura Cochran","Carlos Contreras","Alejandra Contreras","Michael Coulson","Donna Coulson",
    "Philip Dailey","Amelia Tran","Doug deHeras","Nikki deHeras","Ryan Dudek","Katie Dudek",
    "Andrew Ellison","Randi Ellison","Daniel Fletcher","Shikera Fletcher","Chris Frei","Vanessa Frei",
    "Tammi Fronek","Greg Fronek","Keith Fulthrop","Carol Menard","Brian Gabel","Kim Gabel","Stephan Gabriel",
    "Tina Gabriel","Raymond Gonzales","Stephanie Gonzales","Eric Graboff","Samantha Graboff","Shauna Grover",
    "Vickie Hamilton","James Hennessy","Marina Hernandez","Phillip Hernandez","Cameron Hernandez",
    "Jonathan Hornberger","Rebecca Hornberger","Wesley Hunnicutt","Melissa Hunnicutt","Celeste Hybki",
    "Bob Hybki","Peter Jakubowski","Donna Jakubowski","Lisa Jones","Brian Kent","Katie Kent","Kirk Kovaleff",
    "Deborah Kovaleff","Robert Kraig","Noreen Kraig","John Kustura","Kathy Kustura","Michael Lalonde",
    "Molly Lalonde","Aaron Lopez","Natalie Lopez","Kris Ludington","Brian Lutz","Dawn Lutz","Kandy Luzzi",
    "Marcos Magar","Christine Magar","Michael McAndrews","Barry McCormick","Mangia McCormick","Caleb McFerran",
    "Allyson McFerran","Kathleen Moore","Joseph Moore","Joel Moradkhani","Jessica Rayhanabad","Matt Morgan",
    "Amy Morgan","Sharon Morgan","Rene Moya III","Michelle Moya","David Murow","Danielle Murow","Anthony Napoli",
    "Duc Nguyen","Thanh Nguyen","Thuy Nguyen","Teresa Nguyen","Tiffany Nguyen","Ryan O'Gorman",
    "Christin O'Gorman","Jason Pagano","Erin Pagano","Sally Pallach","Delin Parada","Kimberly Parada",
    "Jay Parungao","Cherry Parungao","Luke Peters","Mariella Peters","Hunter Pollard","James Pugeda",
    "Michelle Le-Pugeda","Yousef Qelene","Jehan Soliman","Alvaro Pineiro Ramos","Steven Ruiz","Shannon Ruiz",
    "Anthony Sabatino","Julie Sabatino","Tony Santibanez","Bernadette Vargas","Weston Seipp","Sharlene Seipp",
    "Michael William Smith","Steven Smith","Mary Lee Smith","Michael Storm","Thuy Storm","Robert Thorne",
    "Nancy Thorne","Trang Tran","Clark Duey","Van Tran-Duey","John Tumino","Tiffany Tumino","Daniel Untalan",
    "Rochelle Untalan","Dr. Jeremy Vistica","Dr. Yuka Vistica","Abe Vogel","Sarah Vogel","Martin Vogel",
    "Kathryn Vogel","Jim Wallace","Marjorie Wallace","Rick Wolfe","Jennifer Wolfe","Herbert Wong","Casey Wong",
    "Chap Yam","Katie Yam","Michael Yip","Ellen Yip","Joseph Zeimen","Richard Zimmer","Kelly Ann Sloan",
    "Steven Zuniga Jr.","Lindsay Zuniga"
]

PDF_DIR = "pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

# Real browser headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://projects.propublica.org/nonprofits/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

def download_pdf(url, path):
    """Download a PDF with proper headers. Returns True if successful."""
    try:
        session = requests.Session()
        r = session.get(url, headers=HEADERS, allow_redirects=True, timeout=60)
        if r.status_code != 200:
            print(f"    [HTTP {r.status_code}] {os.path.basename(path)}")
            return False
        # Check if it's actually a PDF
        if r.content[:4] != b"%PDF":
            # Might be Brotli compressed HTML
            content_type = r.headers.get("content-type", "").lower()
            print(f"    [NOT PDF] {os.path.basename(path)} — content-type: {content_type}, size: {len(r.content)}, first 4 bytes: {r.content[:4]}")
            return False
        with open(path, "wb") as f:
            f.write(r.content)
        return True
    except Exception as e:
        print(f"    [ERROR downloading] {os.path.basename(path)}: {e}")
        return False

def extract_with_ocr_fallback(path):
    try:
        text = extract_text(path)
        if text and len(text.strip()) > 100:
            return text.lower()
        # Blank or near-blank — fall back to OCR
        print(f"    [OCR] {os.path.basename(path)}")
        pages = convert_from_path(path, dpi=200)
        ocr_text = ""
        for page in pages:
            ocr_text += pytesseract.image_to_string(page) + "\n"
        return ocr_text.lower()
    except Exception as e:
        print(f"    [ERROR] {os.path.basename(path)}: {e}")
        return ""

with open("huntington_beach_pdfs.json") as f:
    filings = json.load(f)

print(f"Loaded {len(filings)} filings. Starting OCR-enabled scan...")
matches = []
scanned = 0
errors = 0

for filing in filings:
    org = filing.get("organization", "Unknown")
    ein = filing.get("ein", "")
    year = filing.get("tax_year", "?")
    pdf_url = filing.get("pdf_url")
    if not pdf_url:
        continue

    filename = f"{ein}_{year}.pdf"
    path = os.path.join(PDF_DIR, filename)

    # Download if not cached
    if not os.path.exists(path):
        if not download_pdf(pdf_url, path):
            errors += 1
            continue
    else:
        # Verify cached file is actually a PDF
        with open(path, "rb") as f:
            if f.read(4) != b"%PDF":
                print(f"    [CACHED NOT PDF] {filename}")
                os.remove(path)
                if not download_pdf(pdf_url, path):
                    errors += 1
                    continue

    text = extract_with_ocr_fallback(path)

    if text:
        for name in DONOR_NAMES:
            if name.lower() in text:
                matches.append({"name": name, "organization": org, "ein": ein, "year": year, "pdf": filename})
                print(f"  [HIT] {name} | {org} | {year}")
    else:
        errors += 1

    scanned += 1
    if scanned % 25 == 0:
        print(f"  [{scanned}/{len(filings)}] scanned | {len(matches)} hits | {errors} errors")

with open("donor_matches_ocr.json", "w") as f:
    json.dump(matches, f, indent=2)

if matches:
    with open("donor_matches_ocr.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=matches[0].keys())
        w.writeheader()
        w.writerows(matches)

print(f"\n=== DONE ===")
print(f"Scanned: {scanned} | Errors: {errors} | Matches: {len(matches)}")
if matches:
    print("\n=== ALL HITS ===")
    for m in matches:
        print(f"  {m['name']} | {m['organization']} | {m['year']}")
