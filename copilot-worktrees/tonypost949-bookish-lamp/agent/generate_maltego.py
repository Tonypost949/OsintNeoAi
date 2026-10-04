import csv
import os

# Define the artifact directory
artifact_dir = r"C:\Users\HP\.gemini\antigravity-ide\brain\3166e8b4-ddb0-4b7a-86f2-58e38034981c"
output_file = os.path.join(artifact_dir, "RICO_HBNC_Maltego_Import.csv")

# Data structure: Source Entity, Source Type, Link Label, Target Entity, Target Type
maltego_data = [
    # The Shelter & Lawsuit
    ["Jesse Knabb", "maltego.Person", "Plaintiff In", "Huntington Beach Navigation Center Toxic Exposure Lawsuit", "maltego.Document"],
    ["Jesse Knabb", "maltego.Person", "Former Resident Of", "Huntington Beach Navigation Center", "maltego.Location"],
    ["Huntington Beach Navigation Center Toxic Exposure Lawsuit", "maltego.Document", "Defendant", "City of Huntington Beach", "maltego.Organization"],
    ["Huntington Beach Navigation Center", "maltego.Location", "Located At", "17642 Beach Boulevard", "maltego.Location"],
    ["Huntington Beach Navigation Center", "maltego.Location", "Located At", "17631 Cameron Lane", "maltego.Location"],
    
    # Contracts & Fraud
    ["City of Huntington Beach", "maltego.Organization", "Approved Contract ($2.2M)", "RPM Team", "maltego.Organization"],
    ["City of Huntington Beach", "maltego.Organization", "Approved Operator Contract", "Mercy House", "maltego.Organization"],
    ["RPM Team", "maltego.Organization", "Managed Construction", "Huntington Beach Navigation Center", "maltego.Location"],
    ["Orange County Public Works", "maltego.Organization", "Overseer", "Huntington Beach Navigation Center", "maltego.Location"],
    ["City of Huntington Beach", "maltego.Organization", "Filed Fraudulent CEQA Exemption", "CEQA Notice of Exemption (Class 1)", "maltego.Document"],
    ["CEQA Notice of Exemption (Class 1)", "maltego.Document", "Bypassed Environmental Laws For", "Huntington Beach Navigation Center", "maltego.Location"],
    
    # The Broader RICO / VAS / Vanguard Network
    ["Andrew Do", "maltego.Person", "County Supervisor", "Orange County", "maltego.Organization"],
    ["Andrew Do", "maltego.Person", "Directed Funds To", "Viet America Society (VAS)", "maltego.Organization"],
    ["Viet America Society (VAS)", "maltego.Organization", "Associated With", "Vanguard of the Old", "maltego.Organization"],
    
    # The UFC Plot Arrests
    ["Vanguard of the Old", "maltego.Organization", "Member", "Tycen C. Proper", "maltego.Person"],
    ["Vanguard of the Old", "maltego.Organization", "Member", "Bryan Omar Roa", "maltego.Person"],
    ["Vanguard of the Old", "maltego.Organization", "Member", "Michael Alan Thomas", "maltego.Person"],
    ["Vanguard of the Old", "maltego.Organization", "Member", "Daniel K. Eskridge", "maltego.Person"],
    ["Vanguard of the Old", "maltego.Organization", "Member", "Abraham Hermosillo Alvarez", "maltego.Person"],
    
    # Connections to locations
    ["Tycen C. Proper", "maltego.Person", "Resides In", "Danville, Ohio", "maltego.Location"],
    ["Bryan Omar Roa", "maltego.Person", "Resides In", "Calimesa, California", "maltego.Location"],
    ["Michael Alan Thomas", "maltego.Person", "Resides In", "Pinon Hills, California", "maltego.Location"],
    ["Daniel K. Eskridge", "maltego.Person", "Resides In", "Kidder, Missouri", "maltego.Location"],
    ["Abraham Hermosillo Alvarez", "maltego.Person", "Resides In", "Omaha, Nebraska", "maltego.Location"],
]

with open(output_file, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    # Header row for Maltego Import Wizard
    writer.writerow(["Source", "Source.Type", "Link.Label", "Target", "Target.Type"])
    for row in maltego_data:
        writer.writerow(row)

print(f"Successfully generated Maltego CSV import file at: {output_file}")
