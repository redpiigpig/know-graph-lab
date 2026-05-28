import json
import urllib.parse
import sys
from collections import defaultdict

# Read input JSONL
input_file = r'c:\tmp\episcopal_batches\batch_175.jsonl'
output_file = r'c:\tmp\episcopal_batches\batch_175_haiku.json'

entries = []
with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        # Skip line number prefix
        parts = line.split('\t', 1)
        if len(parts) == 2:
            try:
                entry = json.loads(parts[1])
                entries.append(entry)
            except json.JSONDecodeError:
                pass

# Define slug alternatives for each person
slug_candidates = {
    "b142792c-807b-4b4b-bc8d-9eaa7f903a62": [  # Gregory Palamas (transit)
        "Gregory_Palamas",
        "Gregory_of_Palamas",
    ],
    "25d0d5ab-3692-4105-b542-14bcad16e4a8": [  # John de Thoresby
        "John_Thoresby",
        "John_de_Thoresby",
        "John_of_Thoresby",
    ],
    "b7f8dcc7-b902-4271-a19f-71a39cd1ade1": [  # Roberto di San Giovanni (Palermo)
        "Roberto_di_San_Giovanni",
        "Henry_Mignano",
        "Enrico_Miniano",
    ],
    "7632f193-ce2a-46f2-8993-1a17e23e32a2": [  # Nikolaus de Matarelis
        "Nikolaus_Matarelis",
        "Nicholas_Matarelis",
        "Nicholas_de_Matarelis",
    ],
    "69b46569-9243-4d0f-89fc-2419068dd538": [  # Estêvão da Guarda (Lisbon)
        "Estevao_da_Guarda",
        "Stephen_of_Guarda",
    ],
    "ed54cb88-e4de-42cd-b197-d66d18288cad": [  # John de St Paul II (Dublin)
        "John_de_St_Paul",
        "John_Saint_Paul",
        "John_of_Saint_Paul",
    ],
    "ab480bcb-2bd2-42b5-8093-e3110b8add06": [  # Ugolino Sciaffini (Pisa)
        "Ugolino_Sciaffini",
        "Ugolino_Pisa",
    ],
    "3a3bf907-2434-4d61-872a-1fc315d3b52d": [  # Pierre de la Trau (Bordeaux)
        "Pierre_de_la_Trau",
        "Peter_Trau",
    ],
    "49d10334-3e2e-4a86-852f-9504e34740ab": [  # Gregory Palamas (Thessalonica)
        "Gregory_Palamas",
        "Gregory_of_Palamas",
    ],
    "b023fc5b-c1ff-4838-91e5-c85871b73b6a": [  # Ernst of Pardubice (Prague)
        "Ernst_of_Pardubice",
        "Ernest_Pardubice",
        "Ernest_of_Pardubice",
    ],
    "7a04b54e-4ad2-4339-8672-95ad872e742d": [  # William de la Zouche (York)
        "William_de_la_Zouche",
        "William_Zouche",
    ],
    "495d2e2c-aa6d-4d8a-9622-934dda783803": [  # Jan van Arkel (Utrecht)
        "Jan_van_Arkel",
        "John_van_Arkel",
    ],
    "706c1056-7c73-4e9a-9af7-bbccafb34c79": [  # Jarosław Bogoria Skotnicki (Gniezno)
        "Jaroslaw_Bogoria_Skotnicki",
        "Jaroslav_Bogoria",
    ],
    "94d74fc0-23e8-468b-8c3a-9901be7cd3c2": [  # Hemming Nilsson (Uppsala)
        "Hemming_Nilsson",
        "Hemming_Nilsson_Uppsala",
    ],
    "2d697332-ab88-4ee2-bf90-2b122bc37a5f": [  # Geremia da Montagnone (Ravenna)
        "Geremia_da_Montagnone",
        "Jeremy_Montagnone",
    ],
    "774c2ae5-fa1b-4ea8-b5be-81535666309c": [  # Hugh de Fagio (Split)
        "Hugh_de_Fagio",
        "Hugh_Fagio",
    ],
    "7d635c59-59fb-45a2-8f6a-0895177720e7": [  # Joanikije II (Serbian)
        "Joanikije_II",
        "Joanikije_of_Serbia",
    ],
    "24d05bb2-5364-4219-b1f3-6c5d4bf08096": [  # Hemming Henrikkinen (Turku)
        "Hemming_Henrikkinen",
        "Hemming_Turku",
    ],
    "ea1c2f98-7ff7-40b6-b6fe-d594f78fca03": [  # Joachim III (Turnovo)
        "Joachim_III",
        "Joachim_Turnovo",
    ],
    "957aa45f-2278-4339-97c0-4eb55343e5f8": [  # Joanikije II (Pech/Pec)
        "Joanikije_II",
        "Joanikije_of_Serbia",
    ],
    "8cf62ff9-29d6-4015-8609-3b7fe725fbd9": [  # Denha II
        "Denha_II",
        "Denha_the_Great",
    ],
    "47cb7844-ade3-4b79-892e-ff4e60b901b0": [  # Jan Doliwita (Poznan)
        "Jan_Doliwita",
        "John_Doliwita",
    ],
    "208e9f5f-cbb4-435c-a548-c1e389366b94": [  # Mar Kirillos of Zaiton (Quanzhou)
        "Mar_Kirillos",
        "Kirillos_Zaiton",
    ],
    "3cf6d6b7-fa1b-4bf4-96ce-211823d2a5fd": [  # Bertram of St. Genesius (Aquileia)
        "Bertram_of_Saint_Genesius",
        "Bertram_Aquileia",
    ],
    "7b9d54ba-f5fc-4317-9b63-a0d9ad1eca9d": [  # Theognostus (Vladimir)
        "Theognostus",
        "Theognostus_of_Kiev",
    ],
}

# Prepare output
results = []
for entry in entries:
    result = {
        "id": entry.get("id"),
        "name_zh": entry.get("name_zh"),
        "name_en": entry.get("name_en"),
        "slug": None,
        "portrait_url": None,
        "status": "PENDING",
        "note": None
    }
    results.append(result)

# Write stub output
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Stub output written to {output_file}")
print(f"Total entries: {len(entries)}")
