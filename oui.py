import csv

def load_oui() -> dict[str, str]:
    oui_db = {}

    with open("oui.csv", "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            assignment = row["Assignment"].strip().upper()
            organization = row["Organization Name"].strip()
            oui_db[assignment] = organization
            
    return oui_db

def get_fabricante(mac: str, oui_db: dict[str, str]) -> str:
    assignment = mac.replace(":", "").upper()[:6]

    return oui_db.get(assignment, "Desconhecido")