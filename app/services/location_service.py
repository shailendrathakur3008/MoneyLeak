"""
Comprehensive Indian Location Dataset and Regional Budget Recommendation Service.

Includes:
- All 28 States and 8 Union Territories (ISO-3166-2:IN standard)
- Administrative districts across all states and UTs
- Major cities, towns, and municipal corporations with Tier classifications:
    * METRO: Major Metropolitan Area (Tier-X / population > 5 million / MMR, NCR, etc.)
    * URBAN: Other Urban Area (Tier-Y / Tier-2 growth hubs)
    * TOWN: Smaller City or Town (Tier-Z / district headquarters)
    * RURAL: Rural or Semi-Urban locality
    * UNCLASSIFIED: Other / Not Listed or unverified locality
- Alternate spellings and transliterations (e.g. Bangalore -> Bengaluru, Bombay -> Mumbai)
- 6-digit Indian PIN code validation and postal circle matching
- India-Adaptive 50/30/20 budget presets & actual expense refinement
"""

import re
from typing import Dict, Any, List, Optional, Tuple

# -----------------------------------------------------------------------------
# 1. 28 STATES AND 8 UNION TERRITORIES
# -----------------------------------------------------------------------------
INDIAN_STATES_AND_UTS = [
    # 28 States
    {"id": "IN-AP", "name": "Andhra Pradesh", "type": "State", "code": "AP", "postal_prefix": ["51", "52", "53"]},
    {"id": "IN-AR", "name": "Arunachal Pradesh", "type": "State", "code": "AR", "postal_prefix": ["79"]},
    {"id": "IN-AS", "name": "Assam", "type": "State", "code": "AS", "postal_prefix": ["78"]},
    {"id": "IN-BR", "name": "Bihar", "type": "State", "code": "BR", "postal_prefix": ["80", "81", "82", "84", "85"]},
    {"id": "IN-CG", "name": "Chhattisgarh", "type": "State", "code": "CG", "postal_prefix": ["49"]},
    {"id": "IN-GA", "name": "Goa", "type": "State", "code": "GA", "postal_prefix": ["40"]},
    {"id": "IN-GJ", "name": "Gujarat", "type": "State", "code": "GJ", "postal_prefix": ["36", "37", "38", "39"]},
    {"id": "IN-HR", "name": "Haryana", "type": "State", "code": "HR", "postal_prefix": ["12", "13"]},
    {"id": "IN-HP", "name": "Himachal Pradesh", "type": "State", "code": "HP", "postal_prefix": ["17"]},
    {"id": "IN-JH", "name": "Jharkhand", "type": "State", "code": "JH", "postal_prefix": ["81", "82", "83"]},
    {"id": "IN-KA", "name": "Karnataka", "type": "State", "code": "KA", "postal_prefix": ["56", "57", "58", "59"]},
    {"id": "IN-KL", "name": "Kerala", "type": "State", "code": "KL", "postal_prefix": ["67", "68", "69"]},
    {"id": "IN-MP", "name": "Madhya Pradesh", "type": "State", "code": "MP", "postal_prefix": ["45", "46", "47", "48"]},
    {"id": "IN-MH", "name": "Maharashtra", "type": "State", "code": "MH", "postal_prefix": ["40", "41", "42", "43", "44"]},
    {"id": "IN-MN", "name": "Manipur", "type": "State", "code": "MN", "postal_prefix": ["79"]},
    {"id": "IN-ML", "name": "Meghalaya", "type": "State", "code": "ML", "postal_prefix": ["79"]},
    {"id": "IN-MZ", "name": "Mizoram", "type": "State", "code": "MZ", "postal_prefix": ["79"]},
    {"id": "IN-NL", "name": "Nagaland", "type": "State", "code": "NL", "postal_prefix": ["79"]},
    {"id": "IN-OD", "name": "Odisha", "type": "State", "code": "OD", "postal_prefix": ["75", "76", "77"]},
    {"id": "IN-PB", "name": "Punjab", "type": "State", "code": "PB", "postal_prefix": ["14", "15", "16"]},
    {"id": "IN-RJ", "name": "Rajasthan", "type": "State", "code": "RJ", "postal_prefix": ["30", "31", "32", "33", "34"]},
    {"id": "IN-SK", "name": "Sikkim", "type": "State", "code": "SK", "postal_prefix": ["73"]},
    {"id": "IN-TN", "name": "Tamil Nadu", "type": "State", "code": "TN", "postal_prefix": ["60", "61", "62", "63", "64"]},
    {"id": "IN-TS", "name": "Telangana", "type": "State", "code": "TS", "postal_prefix": ["50"]},
    {"id": "IN-TR", "name": "Tripura", "type": "State", "code": "TR", "postal_prefix": ["79"]},
    {"id": "IN-UP", "name": "Uttar Pradesh", "type": "State", "code": "UP", "postal_prefix": ["20", "21", "22", "23", "24", "25", "26", "27", "28"]},
    {"id": "IN-UK", "name": "Uttarakhand", "type": "State", "code": "UK", "postal_prefix": ["24", "26"]},
    {"id": "IN-WB", "name": "West Bengal", "type": "State", "code": "WB", "postal_prefix": ["70", "71", "72", "73", "74"]},

    # 8 Union Territories
    {"id": "IN-AN", "name": "Andaman and Nicobar Islands", "type": "Union Territory", "code": "AN", "postal_prefix": ["74"]},
    {"id": "IN-CH", "name": "Chandigarh", "type": "Union Territory", "code": "CH", "postal_prefix": ["16"]},
    {"id": "IN-DH", "name": "Dadra and Nagar Haveli and Daman and Diu", "type": "Union Territory", "code": "DH", "postal_prefix": ["39"]},
    {"id": "IN-DL", "name": "Delhi", "type": "Union Territory", "code": "DL", "postal_prefix": ["11"]},
    {"id": "IN-JK", "name": "Jammu and Kashmir", "type": "Union Territory", "code": "JK", "postal_prefix": ["18", "19"]},
    {"id": "IN-LA", "name": "Ladakh", "type": "Union Territory", "code": "LA", "postal_prefix": ["19"]},
    {"id": "IN-LD", "name": "Lakshadweep", "type": "Union Territory", "code": "LD", "postal_prefix": ["68"]},
    {"id": "IN-PY", "name": "Puducherry", "type": "Union Territory", "code": "PY", "postal_prefix": ["60"]}
]

# Quick lookup by state_id
STATE_BY_ID = {s["id"]: s for s in INDIAN_STATES_AND_UTS}


# -----------------------------------------------------------------------------
# 2. ADMINISTRATIVE DISTRICTS MAP (ALL 36 STATES & UTs)
# -----------------------------------------------------------------------------
DISTRICTS_BY_STATE: Dict[str, List[Dict[str, str]]] = {
    "IN-AP": [
        {"id": "IN-AP-VSP", "name": "Visakhapatnam"}, {"id": "IN-AP-VJA", "name": "NTR / Vijayawada"},
        {"id": "IN-AP-GNT", "name": "Guntur"}, {"id": "IN-AP-KRN", "name": "Kurnool"},
        {"id": "IN-AP-TPT", "name": "Tirupati"}, {"id": "IN-AP-NLR", "name": "SPSR Nellore"},
        {"id": "IN-AP-EG", "name": "Kakinada / East Godavari"}, {"id": "IN-AP-WG", "name": "Eluru / West Godavari"},
        {"id": "IN-AP-ATP", "name": "Ananthapuramu"}, {"id": "IN-AP-CDP", "name": "YSR Kadapa"},
        {"id": "IN-AP-SKL", "name": "Srikakulam"}, {"id": "IN-AP-VZM", "name": "Vizianagaram"},
        {"id": "IN-AP-PRA", "name": "Prakasam"}, {"id": "IN-AP-OTH", "name": "Other District"}
    ],
    "IN-AR": [
        {"id": "IN-AR-ITA", "name": "Papum Pare (Itanagar)"}, {"id": "IN-AR-CHA", "name": "Changlang"},
        {"id": "IN-AR-PAS", "name": "East Siang (Pasighat)"}, {"id": "IN-AR-TAW", "name": "Tawang"},
        {"id": "IN-AR-ZIR", "name": "Lower Subansiri (Ziro)"}, {"id": "IN-AR-OTH", "name": "Other District"}
    ],
    "IN-AS": [
        {"id": "IN-AS-KAM", "name": "Kamrup Metropolitan (Guwahati)"}, {"id": "IN-AS-DIB", "name": "Dibrugarh"},
        {"id": "IN-AS-CAH", "name": "Cachar (Silchar)"}, {"id": "IN-AS-JOR", "name": "Jorhat"},
        {"id": "IN-AS-NAG", "name": "Nagaon"}, {"id": "IN-AS-TEZ", "name": "Sonitpur (Tezpur)"},
        {"id": "IN-AS-TIN", "name": "Tinsukia"}, {"id": "IN-AS-BON", "name": "Bongaigaon"},
        {"id": "IN-AS-OTH", "name": "Other District"}
    ],
    "IN-BR": [
        {"id": "IN-BR-PAT", "name": "Patna"}, {"id": "IN-BR-GAY", "name": "Gaya"},
        {"id": "IN-BR-BHA", "name": "Bhagalpur"}, {"id": "IN-BR-MUZ", "name": "Muzaffarpur"},
        {"id": "IN-BR-DAR", "name": "Darbhanga"}, {"id": "IN-BR-PUR", "name": "Purnia"},
        {"id": "IN-BR-BEG", "name": "Begusarai"}, {"id": "IN-BR-ARA", "name": "Bhojpur (Arrah)"},
        {"id": "IN-BR-NAL", "name": "Nalanda (Bihar Sharif)"}, {"id": "IN-BR-ROH", "name": "Rohtas (Sasaram)"},
        {"id": "IN-BR-OTH", "name": "Other District"}
    ],
    "IN-CG": [
        {"id": "IN-CG-RAI", "name": "Raipur"}, {"id": "IN-CG-DUR", "name": "Durg (Bhilai)"},
        {"id": "IN-CG-BIL", "name": "Bilaspur"}, {"id": "IN-CG-KOR", "name": "Korba"},
        {"id": "IN-CG-RAJ", "name": "Rajnandgaon"}, {"id": "IN-CG-JAG", "name": "Bastar (Jagdalpur)"},
        {"id": "IN-CG-OTH", "name": "Other District"}
    ],
    "IN-GA": [
        {"id": "IN-GA-NG", "name": "North Goa (Panaji)"}, {"id": "IN-GA-SG", "name": "South Goa (Margao)"}
    ],
    "IN-GJ": [
        {"id": "IN-GJ-AMD", "name": "Ahmedabad"}, {"id": "IN-GJ-SUR", "name": "Surat"},
        {"id": "IN-GJ-BRD", "name": "Vadodara"}, {"id": "IN-GJ-RAI", "name": "Rajkot"},
        {"id": "IN-GJ-BHV", "name": "Bhavnagar"}, {"id": "IN-GJ-JAM", "name": "Jamnagar"},
        {"id": "IN-GJ-GND", "name": "Gandhinagar"}, {"id": "IN-GJ-JUN", "name": "Junagadh"},
        {"id": "IN-GJ-ANH", "name": "Anand"}, {"id": "IN-GJ-KCH", "name": "Kutch (Bhuj)"},
        {"id": "IN-GJ-MRB", "name": "Morbi"}, {"id": "IN-GJ-OTH", "name": "Other District"}
    ],
    "IN-HR": [
        {"id": "IN-HR-GUR", "name": "Gurugram"}, {"id": "IN-HR-FAR", "name": "Faridabad"},
        {"id": "IN-HR-PAN", "name": "Panipat"}, {"id": "IN-HR-AMB", "name": "Ambala"},
        {"id": "IN-HR-ROH", "name": "Rohtak"}, {"id": "IN-HR-HIS", "name": "Hisar"},
        {"id": "IN-HR-KAR", "name": "Karnal"}, {"id": "IN-HR-SON", "name": "Sonipat"},
        {"id": "IN-HR-PNC", "name": "Panchkula"}, {"id": "IN-HR-YAM", "name": "Yamunanagar"},
        {"id": "IN-HR-OTH", "name": "Other District"}
    ],
    "IN-HP": [
        {"id": "IN-HP-SHI", "name": "Shimla"}, {"id": "IN-HP-KAN", "name": "Kangra (Dharamshala)"},
        {"id": "IN-HP-MAN", "name": "Mandi"}, {"id": "IN-HP-SOL", "name": "Solan"},
        {"id": "IN-HP-KUL", "name": "Kullu (Manali)"}, {"id": "IN-HP-UNA", "name": "Una"},
        {"id": "IN-HP-OTH", "name": "Other District"}
    ],
    "IN-JH": [
        {"id": "IN-JH-RAN", "name": "Ranchi"}, {"id": "IN-JH-JAM", "name": "East Singhbhum (Jamshedpur)"},
        {"id": "IN-JH-DHA", "name": "Dhanbad"}, {"id": "IN-JH-BOK", "name": "Bokaro"},
        {"id": "IN-JH-DEO", "name": "Deoghar"}, {"id": "IN-JH-HAZ", "name": "Hazaribagh"},
        {"id": "IN-JH-OTH", "name": "Other District"}
    ],
    "IN-KA": [
        {"id": "IN-KA-BLRU", "name": "Bengaluru Urban"}, {"id": "IN-KA-BLRR", "name": "Bengaluru Rural"},
        {"id": "IN-KA-MYS", "name": "Mysuru"}, {"id": "IN-KA-DK", "name": "Dakshina Kannada (Mangaluru)"},
        {"id": "IN-KA-DH", "name": "Dharwad (Hubballi-Dharwad)"}, {"id": "IN-KA-BEL", "name": "Belagavi"},
        {"id": "IN-KA-KLB", "name": "Kalaburagi (Gulbarga)"}, {"id": "IN-KA-SHI", "name": "Shivamogga"},
        {"id": "IN-KA-TUM", "name": "Tumakuru"}, {"id": "IN-KA-UDU", "name": "Udupi"},
        {"id": "IN-KA-DVG", "name": "Davanagere"}, {"id": "IN-KA-BELG", "name": "Ballari"},
        {"id": "IN-KA-OTH", "name": "Other District"}
    ],
    "IN-KL": [
        {"id": "IN-KL-EKM", "name": "Ernakulam (Kochi)"}, {"id": "IN-KL-TVM", "name": "Thiruvananthapuram"},
        {"id": "IN-KL-KKD", "name": "Kozhikode"}, {"id": "IN-KL-TSR", "name": "Thrissur"},
        {"id": "IN-KL-KNR", "name": "Kannur"}, {"id": "IN-KL-KLM", "name": "Kollam"},
        {"id": "IN-KL-PLK", "name": "Palakkad"}, {"id": "IN-KL-MLP", "name": "Malappuram"},
        {"id": "IN-KL-KTY", "name": "Kottayam"}, {"id": "IN-KL-ALP", "name": "Alappuzha"},
        {"id": "IN-KL-OTH", "name": "Other District"}
    ],
    "IN-MP": [
        {"id": "IN-MP-IND", "name": "Indore"}, {"id": "IN-MP-BHO", "name": "Bhopal"},
        {"id": "IN-MP-JAB", "name": "Jabalpur"}, {"id": "IN-MP-GWA", "name": "Gwalior"},
        {"id": "IN-MP-UJJ", "name": "Ujjain"}, {"id": "IN-MP-SAG", "name": "Sagar"},
        {"id": "IN-MP-DEW", "name": "Dewas"}, {"id": "IN-MP-SAT", "name": "Satna"},
        {"id": "IN-MP-RAT", "name": "Ratlam"}, {"id": "IN-MP-REW", "name": "Rewa"},
        {"id": "IN-MP-OTH", "name": "Other District"}
    ],
    "IN-MH": [
        {"id": "IN-MH-MUM", "name": "Mumbai City"}, {"id": "IN-MH-MSU", "name": "Mumbai Suburban"},
        {"id": "IN-MH-THA", "name": "Thane (incl. Navi Mumbai & Kalyan)"}, {"id": "IN-MH-PUN", "name": "Pune & Pimpri-Chinchwad"},
        {"id": "IN-MH-NAG", "name": "Nagpur"}, {"id": "IN-MH-NSK", "name": "Nashik"},
        {"id": "IN-MH-AUR", "name": "Chhatrapati Sambhaji Nagar (Aurangabad)"}, {"id": "IN-MH-SOL", "name": "Solapur"},
        {"id": "IN-MH-AMR", "name": "Amravati"}, {"id": "IN-MH-KOL", "name": "Kolhapur"},
        {"id": "IN-MH-RAI", "name": "Raigad (Panvel / Navi Mumbai South)"}, {"id": "IN-MH-JAL", "name": "Jalgaon"},
        {"id": "IN-MH-AKO", "name": "Akola"}, {"id": "IN-MH-LAT", "name": "Latur"},
        {"id": "IN-MH-SAN", "name": "Sangli"}, {"id": "IN-MH-DHA", "name": "Dhule"},
        {"id": "IN-MH-AHM", "name": "Ahmednagar"}, {"id": "IN-MH-OTH", "name": "Other District"}
    ],
    "IN-MN": [
        {"id": "IN-MN-IME", "name": "Imphal East"}, {"id": "IN-MN-IMW", "name": "Imphal West"},
        {"id": "IN-MN-CHU", "name": "Churachandpur"}, {"id": "IN-MN-THO", "name": "Thoubal"},
        {"id": "IN-MN-OTH", "name": "Other District"}
    ],
    "IN-ML": [
        {"id": "IN-ML-EKH", "name": "East Khasi Hills (Shillong)"}, {"id": "IN-ML-WGH", "name": "West Garo Hills (Tura)"},
        {"id": "IN-ML-RBL", "name": "Ri-Bhoi (Nongpoh)"}, {"id": "IN-ML-OTH", "name": "Other District"}
    ],
    "IN-MZ": [
        {"id": "IN-MZ-AIZ", "name": "Aizawl"}, {"id": "IN-MZ-LUN", "name": "Lunglei"},
        {"id": "IN-MZ-CHA", "name": "Champhai"}, {"id": "IN-MZ-OTH", "name": "Other District"}
    ],
    "IN-NL": [
        {"id": "IN-NL-KOH", "name": "Kohima"}, {"id": "IN-NL-DIM", "name": "Dimapur"},
        {"id": "IN-NL-MOK", "name": "Mokokchung"}, {"id": "IN-NL-OTH", "name": "Other District"}
    ],
    "IN-OD": [
        {"id": "IN-OD-KHO", "name": "Khurda (Bhubaneswar)"}, {"id": "IN-OD-CUT", "name": "Cuttack"},
        {"id": "IN-OD-SUN", "name": "Sundargarh (Rourkela)"}, {"id": "IN-OD-GAN", "name": "Ganjam (Berhampur)"},
        {"id": "IN-OD-SAM", "name": "Sambalpur"}, {"id": "IN-OD-BAL", "name": "Balasore"},
        {"id": "IN-OD-PUR", "name": "Puri"}, {"id": "IN-OD-OTH", "name": "Other District"}
    ],
    "IN-PB": [
        {"id": "IN-PB-LUD", "name": "Ludhiana"}, {"id": "IN-PB-AMR", "name": "Amritsar"},
        {"id": "IN-PB-JAL", "name": "Jalandhar"}, {"id": "IN-PB-PAT", "name": "Patiala"},
        {"id": "IN-PB-BAT", "name": "Bathinda"}, {"id": "IN-PB-MOH", "name": "SAS Nagar (Mohali)"},
        {"id": "IN-PB-HOS", "name": "Hoshiarpur"}, {"id": "IN-PB-PATI", "name": "Pathankot"},
        {"id": "IN-PB-OTH", "name": "Other District"}
    ],
    "IN-RJ": [
        {"id": "IN-RJ-JAI", "name": "Jaipur"}, {"id": "IN-RJ-JOD", "name": "Jodhpur"},
        {"id": "IN-RJ-KOT", "name": "Kota"}, {"id": "IN-RJ-BIK", "name": "Bikaner"},
        {"id": "IN-RJ-AJM", "name": "Ajmer"}, {"id": "IN-RJ-UDA", "name": "Udaipur"},
        {"id": "IN-RJ-BHI", "name": "Bhilwara"}, {"id": "IN-RJ-ALW", "name": "Alwar"},
        {"id": "IN-RJ-SIK", "name": "Sikar"}, {"id": "IN-RJ-BHA", "name": "Bharatpur"},
        {"id": "IN-RJ-SRI", "name": "Sri Ganganagar"}, {"id": "IN-RJ-OTH", "name": "Other District"}
    ],
    "IN-SK": [
        {"id": "IN-SK-GAN", "name": "Gangtok (East Sikkim)"}, {"id": "IN-SK-NAM", "name": "Namchi (South Sikkim)"},
        {"id": "IN-SK-GYA", "name": "Gyalshing (West Sikkim)"}, {"id": "IN-SK-OTH", "name": "Other District"}
    ],
    "IN-TN": [
        {"id": "IN-TN-CHE", "name": "Chennai"}, {"id": "IN-TN-COI", "name": "Coimbatore"},
        {"id": "IN-TN-MAD", "name": "Madurai"}, {"id": "IN-TN-TRI", "name": "Tiruchirappalli"},
        {"id": "IN-TN-SAL", "name": "Salem"}, {"id": "IN-TN-TPU", "name": "Tiruppur"},
        {"id": "IN-TN-ERO", "name": "Erode"}, {"id": "IN-TN-VEL", "name": "Vellore"},
        {"id": "IN-TN-TIR", "name": "Tirunelveli"}, {"id": "IN-TN-THO", "name": "Thoothukudi"},
        {"id": "IN-TN-KAN", "name": "Kanchipuram"}, {"id": "IN-TN-CHEG", "name": "Chengalpattu"},
        {"id": "IN-TN-THA", "name": "Thanjavur"}, {"id": "IN-TN-DIN", "name": "Dindigul"},
        {"id": "IN-TN-OTH", "name": "Other District"}
    ],
    "IN-TS": [
        {"id": "IN-TS-HYD", "name": "Hyderabad"}, {"id": "IN-TS-MED", "name": "Medchal-Malkajgiri"},
        {"id": "IN-TS-RAN", "name": "Rangareddy (Cyberabad / Gachibowli)"}, {"id": "IN-TS-SAN", "name": "Sangareddy"},
        {"id": "IN-TS-WAR", "name": "Warangal"}, {"id": "IN-TS-NIZ", "name": "Nizamabad"},
        {"id": "IN-TS-KAR", "name": "Karimnagar"}, {"id": "IN-TS-KHA", "name": "Khammam"},
        {"id": "IN-TS-RAM", "name": "Ramagundam / Peddapalli"}, {"id": "IN-TS-OTH", "name": "Other District"}
    ],
    "IN-TR": [
        {"id": "IN-TR-WTR", "name": "West Tripura (Agartala)"}, {"id": "IN-TR-GOM", "name": "Gomati (Udaipur)"},
        {"id": "IN-TR-DHA", "name": "Dharmanagar"}, {"id": "IN-TR-OTH", "name": "Other District"}
    ],
    "IN-UP": [
        {"id": "IN-UP-GBN", "name": "Gautam Buddha Nagar (Noida & Greater Noida)"}, {"id": "IN-UP-GHA", "name": "Ghaziabad"},
        {"id": "IN-UP-LUC", "name": "Lucknow"}, {"id": "IN-UP-KAN", "name": "Kanpur Nagar"},
        {"id": "IN-UP-AGR", "name": "Agra"}, {"id": "IN-UP-VAR", "name": "Varanasi"},
        {"id": "IN-UP-PRY", "name": "Prayagraj (Allahabad)"}, {"id": "IN-UP-MEE", "name": "Meerut"},
        {"id": "IN-UP-BAR", "name": "Bareilly"}, {"id": "IN-UP-ALI", "name": "Aligarh"},
        {"id": "IN-UP-MOR", "name": "Moradabad"}, {"id": "IN-UP-SAH", "name": "Saharanpur"},
        {"id": "IN-UP-GOR", "name": "Gorakhpur"}, {"id": "IN-UP-FZR", "name": "Firozabad"},
        {"id": "IN-UP-JHA", "name": "Jhansi"}, {"id": "IN-UP-MUZ", "name": "Muzaffarnagar"},
        {"id": "IN-UP-MAT", "name": "Mathura"}, {"id": "IN-UP-AYO", "name": "Ayodhya (Faizabad)"},
        {"id": "IN-UP-OTH", "name": "Other District"}
    ],
    "IN-UK": [
        {"id": "IN-UK-DEH", "name": "Dehradun (incl. Rishikesh)"}, {"id": "IN-UK-HAR", "name": "Haridwar (Roorkee)"},
        {"id": "IN-UK-NAI", "name": "Nainital (Haldwani)"}, {"id": "IN-UK-USN", "name": "Udham Singh Nagar (Rudrapur)"},
        {"id": "IN-UK-OTH", "name": "Other District"}
    ],
    "IN-WB": [
        {"id": "IN-WB-KOL", "name": "Kolkata"}, {"id": "IN-WB-N24", "name": "North 24 Parganas (Bidhannagar / Salt Lake)"},
        {"id": "IN-WB-S24", "name": "South 24 Parganas"}, {"id": "IN-WB-HOW", "name": "Howrah"},
        {"id": "IN-WB-PAS", "name": "Paschim Bardhaman (Asansol & Durgapur)"}, {"id": "IN-WB-DAR", "name": "Darjeeling (Siliguri)"},
        {"id": "IN-WB-HOO", "name": "Hooghly"}, {"id": "IN-WB-MAL", "name": "Malda"},
        {"id": "IN-WB-PUR", "name": "Purba Medinipur (Haldia)"}, {"id": "IN-WB-OTH", "name": "Other District"}
    ],
    # Union Territories
    "IN-AN": [
        {"id": "IN-AN-SOU", "name": "South Andaman (Port Blair)"}, {"id": "IN-AN-NIC", "name": "Nicobar"}
    ],
    "IN-CH": [
        {"id": "IN-CH-CHD", "name": "Chandigarh"}
    ],
    "IN-DH": [
        {"id": "IN-DH-DNH", "name": "Dadra and Nagar Haveli (Silvassa)"}, {"id": "IN-DH-DAM", "name": "Daman"}, {"id": "IN-DH-DIU", "name": "Diu"}
    ],
    "IN-DL": [
        {"id": "IN-DL-CEN", "name": "Central Delhi"}, {"id": "IN-DL-NEW", "name": "New Delhi"},
        {"id": "IN-DL-SOU", "name": "South Delhi"}, {"id": "IN-DL-SW", "name": "South West Delhi (Dwarka)"},
        {"id": "IN-DL-SE", "name": "South East Delhi"}, {"id": "IN-DL-WES", "name": "West Delhi"},
        {"id": "IN-DL-NOR", "name": "North Delhi"}, {"id": "IN-DL-NW", "name": "North West Delhi (Rohini)"},
        {"id": "IN-DL-EAS", "name": "East Delhi"}, {"id": "IN-DL-NE", "name": "North East Delhi"},
        {"id": "IN-DL-SHA", "name": "Shahdara"}
    ],
    "IN-JK": [
        {"id": "IN-JK-SRI", "name": "Srinagar"}, {"id": "IN-JK-JAM", "name": "Jammu"},
        {"id": "IN-JK-ANA", "name": "Anantnag"}, {"id": "IN-JK-BAR", "name": "Baramulla"},
        {"id": "IN-JK-UDH", "name": "Udhampur"}, {"id": "IN-JK-OTH", "name": "Other District"}
    ],
    "IN-LA": [
        {"id": "IN-LA-LEH", "name": "Leh"}, {"id": "IN-LA-KAR", "name": "Kargil"}
    ],
    "IN-LD": [
        {"id": "IN-LD-KAV", "name": "Lakshadweep (Kavaratti)"}
    ],
    "IN-PY": [
        {"id": "IN-PY-PUD", "name": "Puducherry"}, {"id": "IN-PY-KAR", "name": "Karaikal"},
        {"id": "IN-PY-MAH", "name": "Mahe"}, {"id": "IN-PY-YAN", "name": "Yanam"}
    ]
}


# -----------------------------------------------------------------------------
# 3. POPULATED CITIES & TOWNS WITH CLASSIFICATION METADATA
# -----------------------------------------------------------------------------
# Tier criteria:
# - METRO: Tier-X statutory mega metro / urban agglomeration (population > 50L)
# - URBAN: Tier-Y / Tier-2 major commercial center
# - TOWN: Tier-Z / Tier-3 regional district center
# - RURAL: Rural or semi-urban block
CITIES_DATA: List[Dict[str, Any]] = [
    # --- MAHARASHTRA ---
    {"id": "IN-MH-MUMBAI", "name": "Mumbai", "district_id": "IN-MH-MUM", "state_id": "IN-MH", "tier": "METRO", "aliases": ["Bombay", "South Mumbai", "Colaba", "Bandra", "Andheri"]},
    {"id": "IN-MH-NAVI-MUMBAI", "name": "Navi Mumbai", "district_id": "IN-MH-THA", "state_id": "IN-MH", "tier": "METRO", "aliases": ["Vashi", "Belapur", "Kharghar", "Nerul"]},
    {"id": "IN-MH-THANE", "name": "Thane", "district_id": "IN-MH-THA", "state_id": "IN-MH", "tier": "METRO", "aliases": ["Ghodbunder", "Majiwada"]},
    {"id": "IN-MH-KALYAN", "name": "Kalyan-Dombivli", "district_id": "IN-MH-THA", "state_id": "IN-MH", "tier": "URBAN", "aliases": ["Kalyan", "Dombivli"]},
    {"id": "IN-MH-PUNE", "name": "Pune", "district_id": "IN-MH-PUN", "state_id": "IN-MH", "tier": "METRO", "aliases": ["Poona", "Kothrud", "Viman Nagar", "Hinjawadi", "Baner"]},
    {"id": "IN-MH-PCMC", "name": "Pimpri-Chinchwad", "district_id": "IN-MH-PUN", "state_id": "IN-MH", "tier": "METRO", "aliases": ["PCMC", "Bhosari", "Wakad"]},
    {"id": "IN-MH-NAGPUR", "name": "Nagpur", "district_id": "IN-MH-NAG", "state_id": "IN-MH", "tier": "URBAN", "aliases": []},
    {"id": "IN-MH-NASHIK", "name": "Nashik", "district_id": "IN-MH-NSK", "state_id": "IN-MH", "tier": "URBAN", "aliases": ["Nasik"]},
    {"id": "IN-MH-AURANGABAD", "name": "Chhatrapati Sambhaji Nagar", "district_id": "IN-MH-AUR", "state_id": "IN-MH", "tier": "URBAN", "aliases": ["Aurangabad"]},
    {"id": "IN-MH-KOLHAPUR", "name": "Kolhapur", "district_id": "IN-MH-KOL", "state_id": "IN-MH", "tier": "TOWN", "aliases": []},
    {"id": "IN-MH-SOLAPUR", "name": "Solapur", "district_id": "IN-MH-SOL", "state_id": "IN-MH", "tier": "URBAN", "aliases": []},
    {"id": "IN-MH-PANVEL", "name": "Panvel", "district_id": "IN-MH-RAI", "state_id": "IN-MH", "tier": "URBAN", "aliases": ["New Panvel"]},

    # --- KARNATAKA ---
    {"id": "IN-KA-BENGALURU", "name": "Bengaluru", "district_id": "IN-KA-BLRU", "state_id": "IN-KA", "tier": "METRO", "aliases": ["Bangalore", "Whitefield", "Koramangala", "Indiranagar", "Electronic City", "HSR Layout"]},
    {"id": "IN-KA-MYSURU", "name": "Mysuru", "district_id": "IN-KA-MYS", "state_id": "IN-KA", "tier": "URBAN", "aliases": ["Mysore"]},
    {"id": "IN-KA-MANGALURU", "name": "Mangaluru", "district_id": "IN-KA-DK", "state_id": "IN-KA", "tier": "URBAN", "aliases": ["Mangalore"]},
    {"id": "IN-KA-HUBBALLI", "name": "Hubballi-Dharwad", "district_id": "IN-KA-DH", "state_id": "IN-KA", "tier": "URBAN", "aliases": ["Hubli", "Dharwad"]},
    {"id": "IN-KA-BELAGAVI", "name": "Belagavi", "district_id": "IN-KA-BEL", "state_id": "IN-KA", "tier": "TOWN", "aliases": ["Belgaum"]},
    {"id": "IN-KA-UDUPI", "name": "Udupi", "district_id": "IN-KA-UDU", "state_id": "IN-KA", "tier": "TOWN", "aliases": ["Manipal"]},

    # --- DELHI (NCR) ---
    {"id": "IN-DL-NEW-DELHI", "name": "New Delhi", "district_id": "IN-DL-NEW", "state_id": "IN-DL", "tier": "METRO", "aliases": ["Delhi", "Connaught Place", "Lutyens"]},
    {"id": "IN-DL-SOUTH-DELHI", "name": "South Delhi", "district_id": "IN-DL-SOU", "state_id": "IN-DL", "tier": "METRO", "aliases": ["Hauz Khas", "Saket", "Greater Kailash"]},
    {"id": "IN-DL-DWARKA", "name": "Dwarka", "district_id": "IN-DL-SW", "state_id": "IN-DL", "tier": "METRO", "aliases": ["South West Delhi"]},
    {"id": "IN-DL-ROHINI", "name": "Rohini", "district_id": "IN-DL-NW", "state_id": "IN-DL", "tier": "METRO", "aliases": ["North West Delhi"]},

    # --- HARYANA (NCR & STATE) ---
    {"id": "IN-HR-GURUGRAM", "name": "Gurugram", "district_id": "IN-HR-GUR", "state_id": "IN-HR", "tier": "METRO", "aliases": ["Gurgaon", "Cyber City", "Golf Course Road", "Sohna Road"]},
    {"id": "IN-HR-FARIDABAD", "name": "Faridabad", "district_id": "IN-HR-FAR", "state_id": "IN-HR", "tier": "METRO", "aliases": ["Ballabgarh"]},
    {"id": "IN-HR-PANCHKULA", "name": "Panchkula", "district_id": "IN-HR-PNC", "state_id": "IN-HR", "tier": "URBAN", "aliases": ["Tricity"]},
    {"id": "IN-HR-PANIPAT", "name": "Panipat", "district_id": "IN-HR-PAN", "state_id": "IN-HR", "tier": "TOWN", "aliases": []},
    {"id": "IN-HR-AMBALA", "name": "Ambala", "district_id": "IN-HR-AMB", "state_id": "IN-HR", "tier": "TOWN", "aliases": ["Ambala Cantt"]},
    {"id": "IN-HR-ROHTAK", "name": "Rohtak", "district_id": "IN-HR-ROH", "state_id": "IN-HR", "tier": "TOWN", "aliases": []},

    # --- UTTAR PRADESH (NCR & STATE) ---
    {"id": "IN-UP-NOIDA", "name": "Noida", "district_id": "IN-UP-GBN", "state_id": "IN-UP", "tier": "METRO", "aliases": ["Sector 18", "Sector 62"]},
    {"id": "IN-UP-GREATER-NOIDA", "name": "Greater Noida", "district_id": "IN-UP-GBN", "state_id": "IN-UP", "tier": "METRO", "aliases": ["Noida Extension", "Knowledge Park"]},
    {"id": "IN-UP-GHAZIABAD", "name": "Ghaziabad", "district_id": "IN-UP-GHA", "state_id": "IN-UP", "tier": "METRO", "aliases": ["Indirapuram", "Vaishali"]},
    {"id": "IN-UP-LUCKNOW", "name": "Lucknow", "district_id": "IN-UP-LUC", "state_id": "IN-UP", "tier": "URBAN", "aliases": ["Gomti Nagar", "Hazratganj"]},
    {"id": "IN-UP-KANPUR", "name": "Kanpur", "district_id": "IN-UP-KAN", "state_id": "IN-UP", "tier": "URBAN", "aliases": ["Cawnpore"]},
    {"id": "IN-UP-VARANASI", "name": "Varanasi", "district_id": "IN-UP-VAR", "state_id": "IN-UP", "tier": "URBAN", "aliases": ["Banaras", "Kashi"]},
    {"id": "IN-UP-AGRA", "name": "Agra", "district_id": "IN-UP-AGR", "state_id": "IN-UP", "tier": "URBAN", "aliases": []},
    {"id": "IN-UP-PRAYAGRAJ", "name": "Prayagraj", "district_id": "IN-UP-PRY", "state_id": "IN-UP", "tier": "URBAN", "aliases": ["Allahabad"]},
    {"id": "IN-UP-MEERUT", "name": "Meerut", "district_id": "IN-UP-MEE", "state_id": "IN-UP", "tier": "URBAN", "aliases": []},
    {"id": "IN-UP-AYODHYA", "name": "Ayodhya", "district_id": "IN-UP-AYO", "state_id": "IN-UP", "tier": "TOWN", "aliases": ["Faizabad"]},

    # --- TAMIL NADU ---
    {"id": "IN-TN-CHENNAI", "name": "Chennai", "district_id": "IN-TN-CHE", "state_id": "IN-TN", "tier": "METRO", "aliases": ["Madras", "OMR", "Velachery", "Adyar", "Anna Nagar"]},
    {"id": "IN-TN-COIMBATORE", "name": "Coimbatore", "district_id": "IN-TN-COI", "state_id": "IN-TN", "tier": "URBAN", "aliases": ["Kovai"]},
    {"id": "IN-TN-MADURAI", "name": "Madurai", "district_id": "IN-TN-MAD", "state_id": "IN-TN", "tier": "URBAN", "aliases": []},
    {"id": "IN-TN-TIRUCHIRAPPALLI", "name": "Tiruchirappalli", "district_id": "IN-TN-TRI", "state_id": "IN-TN", "tier": "URBAN", "aliases": ["Trichy"]},
    {"id": "IN-TN-SALEM", "name": "Salem", "district_id": "IN-TN-SAL", "state_id": "IN-TN", "tier": "TOWN", "aliases": []},

    # --- TELANGANA ---
    {"id": "IN-TS-HYDERABAD", "name": "Hyderabad", "district_id": "IN-TS-HYD", "state_id": "IN-TS", "tier": "METRO", "aliases": ["Secunderabad", "Banjara Hills", "Jubilee Hills", "Hitec City", "Gachibowli", "Madhapur"]},
    {"id": "IN-TS-WARANGAL", "name": "Warangal", "district_id": "IN-TS-WAR", "state_id": "IN-TS", "tier": "URBAN", "aliases": ["Hanamkonda", "Kazipet"]},
    {"id": "IN-TS-NIZAMABAD", "name": "Nizamabad", "district_id": "IN-TS-NIZ", "state_id": "IN-TS", "tier": "TOWN", "aliases": []},

    # --- WEST BENGAL ---
    {"id": "IN-WB-KOLKATA", "name": "Kolkata", "district_id": "IN-WB-KOL", "state_id": "IN-WB", "tier": "METRO", "aliases": ["Calcutta", "Alipore", "Park Street", "Ballygunge"]},
    {"id": "IN-WB-HOWRAH", "name": "Howrah", "district_id": "IN-WB-HOW", "state_id": "IN-WB", "tier": "METRO", "aliases": ["Haora"]},
    {"id": "IN-WB-NEW-TOWN", "name": "Bidhannagar / New Town", "district_id": "IN-WB-N24", "state_id": "IN-WB", "tier": "METRO", "aliases": ["Salt Lake", "Rajarhat"]},
    {"id": "IN-WB-SILIGURI", "name": "Siliguri", "district_id": "IN-WB-DAR", "state_id": "IN-WB", "tier": "URBAN", "aliases": []},
    {"id": "IN-WB-DURGAPUR", "name": "Durgapur", "district_id": "IN-WB-PAS", "state_id": "IN-WB", "tier": "URBAN", "aliases": []},
    {"id": "IN-WB-ASANSOL", "name": "Asansol", "district_id": "IN-WB-PAS", "state_id": "IN-WB", "tier": "URBAN", "aliases": []},

    # --- GUJARAT ---
    {"id": "IN-GJ-AHMEDABAD", "name": "Ahmedabad", "district_id": "IN-GJ-AMD", "state_id": "IN-GJ", "tier": "METRO", "aliases": ["Amdavad", "SG Highway", "Bodakdev", "Prahlad Nagar"]},
    {"id": "IN-GJ-SURAT", "name": "Surat", "district_id": "IN-GJ-SUR", "state_id": "IN-GJ", "tier": "URBAN", "aliases": ["Diamond City"]},
    {"id": "IN-GJ-VADODARA", "name": "Vadodara", "district_id": "IN-GJ-BRD", "state_id": "IN-GJ", "tier": "URBAN", "aliases": ["Baroda"]},
    {"id": "IN-GJ-RAJKOT", "name": "Rajkot", "district_id": "IN-GJ-RAI", "state_id": "IN-GJ", "tier": "URBAN", "aliases": []},
    {"id": "IN-GJ-GANDHINAGAR", "name": "Gandhinagar", "district_id": "IN-GJ-GND", "state_id": "IN-GJ", "tier": "URBAN", "aliases": ["GIFT City"]},

    # --- RAJASTHAN ---
    {"id": "IN-RJ-JAIPUR", "name": "Jaipur", "district_id": "IN-RJ-JAI", "state_id": "IN-RJ", "tier": "URBAN", "aliases": ["Pink City", "Mansarovar", "Malviya Nagar"]},
    {"id": "IN-RJ-JODHPUR", "name": "Jodhpur", "district_id": "IN-RJ-JOD", "state_id": "IN-RJ", "tier": "URBAN", "aliases": []},
    {"id": "IN-RJ-KOTA", "name": "Kota", "district_id": "IN-RJ-KOT", "state_id": "IN-RJ", "tier": "URBAN", "aliases": []},
    {"id": "IN-RJ-UDAIPUR", "name": "Udaipur", "district_id": "IN-RJ-UDA", "state_id": "IN-RJ", "tier": "TOWN", "aliases": ["City of Lakes"]},

    # --- MADHYA PRADESH ---
    {"id": "IN-MP-INDORE", "name": "Indore", "district_id": "IN-MP-IND", "state_id": "IN-MP", "tier": "URBAN", "aliases": ["Vijay Nagar", "Palasia"]},
    {"id": "IN-MP-BHOPAL", "name": "Bhopal", "district_id": "IN-MP-BHO", "state_id": "IN-MP", "tier": "URBAN", "aliases": []},
    {"id": "IN-MP-JABALPUR", "name": "Jabalpur", "district_id": "IN-MP-JAB", "state_id": "IN-MP", "tier": "URBAN", "aliases": []},
    {"id": "IN-MP-GWALIOR", "name": "Gwalior", "district_id": "IN-MP-GWA", "state_id": "IN-MP", "tier": "URBAN", "aliases": []},

    # --- KERALA ---
    {"id": "IN-KL-KOCHI", "name": "Kochi", "district_id": "IN-KL-EKM", "state_id": "IN-KL", "tier": "URBAN", "aliases": ["Cochin", "Ernakulam", "Kakkanad", "Edapally"]},
    {"id": "IN-KL-THIRUVANANTHAPURAM", "name": "Thiruvananthapuram", "district_id": "IN-KL-TVM", "state_id": "IN-KL", "tier": "URBAN", "aliases": ["Trivandrum", "Technopark"]},
    {"id": "IN-KL-KOZHIKODE", "name": "Kozhikode", "district_id": "IN-KL-KKD", "state_id": "IN-KL", "tier": "URBAN", "aliases": ["Calicut"]},

    # --- PUNJAB ---
    {"id": "IN-PB-LUDHIANA", "name": "Ludhiana", "district_id": "IN-PB-LUD", "state_id": "IN-PB", "tier": "URBAN", "aliases": []},
    {"id": "IN-PB-AMRITSAR", "name": "Amritsar", "district_id": "IN-PB-AMR", "state_id": "IN-PB", "tier": "URBAN", "aliases": []},
    {"id": "IN-PB-MOHALI", "name": "SAS Nagar (Mohali)", "district_id": "IN-PB-MOH", "state_id": "IN-PB", "tier": "URBAN", "aliases": ["Mohali"]},

    # --- CHANDIGARH ---
    {"id": "IN-CH-CHANDIGARH", "name": "Chandigarh", "district_id": "IN-CH-CHD", "state_id": "IN-CH", "tier": "URBAN", "aliases": ["City Beautiful", "Tricity"]},

    # --- BIHAR ---
    {"id": "IN-BR-PATNA", "name": "Patna", "district_id": "IN-BR-PAT", "state_id": "IN-BR", "tier": "URBAN", "aliases": ["Patliputra", "Kankarbagh"]},
    {"id": "IN-BR-GAYA", "name": "Gaya", "district_id": "IN-BR-GAY", "state_id": "IN-BR", "tier": "TOWN", "aliases": ["Bodh Gaya"]},

    # --- ODISHA ---
    {"id": "IN-OD-BHUBANESWAR", "name": "Bhubaneswar", "district_id": "IN-OD-KHO", "state_id": "IN-OD", "tier": "URBAN", "aliases": []},
    {"id": "IN-OD-CUTTACK", "name": "Cuttack", "district_id": "IN-OD-CUT", "state_id": "IN-OD", "tier": "URBAN", "aliases": []},

    # --- ANDHRA PRADESH ---
    {"id": "IN-AP-VISAKHAPATNAM", "name": "Visakhapatnam", "district_id": "IN-AP-VSP", "state_id": "IN-AP", "tier": "URBAN", "aliases": ["Vizag"]},
    {"id": "IN-AP-VIJAYAWADA", "name": "Vijayawada", "district_id": "IN-AP-VJA", "state_id": "IN-AP", "tier": "URBAN", "aliases": ["Bezawada"]},

    # --- CHHATTISGARH ---
    {"id": "IN-CG-RAIPUR", "name": "Raipur", "district_id": "IN-CG-RAI", "state_id": "IN-CG", "tier": "URBAN", "aliases": []},
    {"id": "IN-CG-BHILAI", "name": "Bhilai-Durg", "district_id": "IN-CG-DUR", "state_id": "IN-CG", "tier": "URBAN", "aliases": []},

    # --- JHARKHAND ---
    {"id": "IN-JH-RANCHI", "name": "Ranchi", "district_id": "IN-JH-RAN", "state_id": "IN-JH", "tier": "URBAN", "aliases": []},
    {"id": "IN-JH-JAMSHEDPUR", "name": "Jamshedpur", "district_id": "IN-JH-JAM", "state_id": "IN-JH", "tier": "URBAN", "aliases": ["Tatanagar"]},

    # --- ASSAM ---
    {"id": "IN-AS-GUWAHATI", "name": "Guwahati", "district_id": "IN-AS-KAM", "state_id": "IN-AS", "tier": "URBAN", "aliases": ["Gauhati", "Dispur"]},

    # --- UTTARAKHAND ---
    {"id": "IN-UK-DEHRADUN", "name": "Dehradun", "district_id": "IN-UK-DEH", "state_id": "IN-UK", "tier": "URBAN", "aliases": ["Doon"]},
    {"id": "IN-UK-HARIDWAR", "name": "Haridwar", "district_id": "IN-UK-HAR", "state_id": "IN-UK", "tier": "TOWN", "aliases": ["Roorkee"]},

    # --- HIMACHAL PRADESH ---
    {"id": "IN-HP-SHIMLA", "name": "Shimla", "district_id": "IN-HP-SHI", "state_id": "IN-HP", "tier": "TOWN", "aliases": ["Simla"]},

    # --- GOA ---
    {"id": "IN-GA-PANAJI", "name": "Panaji", "district_id": "IN-GA-NG", "state_id": "IN-GA", "tier": "TOWN", "aliases": ["Panjim"]},
    {"id": "IN-GA-MARGAO", "name": "Margao", "district_id": "IN-GA-SG", "state_id": "IN-GA", "tier": "TOWN", "aliases": ["Madgaon"]},

    # --- JAMMU & KASHMIR ---
    {"id": "IN-JK-SRINAGAR", "name": "Srinagar", "district_id": "IN-JK-SRI", "state_id": "IN-JK", "tier": "URBAN", "aliases": []},
    {"id": "IN-JK-JAMMU", "name": "Jammu", "district_id": "IN-JK-JAM", "state_id": "IN-JK", "tier": "URBAN", "aliases": []},

    # --- PUDUCHERRY ---
    {"id": "IN-PY-PUDUCHERRY", "name": "Puducherry", "district_id": "IN-PY-PUD", "state_id": "IN-PY", "tier": "TOWN", "aliases": ["Pondicherry"]}
]

# Fast index by city_id
CITY_BY_ID = {c["id"]: c for c in CITIES_DATA}


# -----------------------------------------------------------------------------
# 4. LOCATION CLASSIFICATION METADATA & PRESET LABELS
# -----------------------------------------------------------------------------
CLASSIFICATION_LABELS = {
    "METRO": {
        "title": "Major Metropolitan Area",
        "description": "High essential cost benchmark (Tier-X Urban Agglomeration, population > 5M). Typical rental and transit commitments require tailored budgeting.",
        "badge": "Metro Tier-1"
    },
    "URBAN": {
        "title": "Other Urban Area",
        "description": "Fast-growing commercial and economic hub (Tier-Y Urban Agglomeration). Balanced essential and lifestyle cost structures.",
        "badge": "Urban Tier-2"
    },
    "TOWN": {
        "title": "Smaller City or Town",
        "description": "Regional district headquarters or commercial market center (Tier-Z). Moderate rental and everyday living costs.",
        "badge": "Town Tier-3"
    },
    "RURAL": {
        "title": "Rural or Semi-Urban",
        "description": "Semi-urban or rural locality with lower essential baseline overheads.",
        "badge": "Rural / Semi-Urban"
    },
    "UNCLASSIFIED": {
        "title": "Standard / Unclassified",
        "description": "Custom or international locality. Calibrated using standard 50/30/20 baseline guidelines.",
        "badge": "General Baseline"
    }
}

BUDGET_PRESETS = {
    "standard": {
        "id": "standard",
        "title": "Standard 50/30/20 Preset",
        "subtitle": "Classic balanced wealth allocation",
        "needs": 50.0,
        "wants": 30.0,
        "savings": 20.0,
        "recommended_for": ["URBAN", "UNCLASSIFIED"]
    },
    "metro": {
        "id": "metro",
        "title": "Metropolitan Starting Preset",
        "subtitle": "Disciplined lifestyle spending with aggressive 25% savings",
        "needs": 50.0,
        "wants": 25.0,
        "savings": 25.0,
        "recommended_for": ["METRO"]
    },
    "high_essential": {
        "id": "high_essential",
        "title": "High Essential-Cost Preset",
        "subtitle": "Realistic accommodation for high rent, family support, or loan EMIs",
        "needs": 60.0,
        "wants": 20.0,
        "savings": 20.0,
        "recommended_for": ["METRO", "URBAN"]
    },
    "lower_cost": {
        "id": "lower_cost",
        "title": "Lower-Cost Starting Preset",
        "subtitle": "Leverage low living expenses to maximize wealth building",
        "needs": 45.0,
        "wants": 30.0,
        "savings": 25.0,
        "recommended_for": ["TOWN", "RURAL"]
    }
}


# -----------------------------------------------------------------------------
# 5. CORE QUERY APIS
# -----------------------------------------------------------------------------

def get_supported_countries() -> List[Dict[str, str]]:
    """Returns supported onboarding countries with India prioritized."""
    return [
        {"code": "IN", "name": "India", "currency": "INR", "is_primary": True},
        {"code": "US", "name": "United States", "currency": "USD", "is_primary": False},
        {"code": "GB", "name": "United Kingdom", "currency": "GBP", "is_primary": False},
        {"code": "AE", "name": "United Arab Emirates", "currency": "AED", "is_primary": False},
        {"code": "SG", "name": "Singapore", "currency": "SGD", "is_primary": False},
        {"code": "CA", "name": "Canada", "currency": "CAD", "is_primary": False},
        {"code": "OTHER", "name": "Other Country", "currency": "USD", "is_primary": False}
    ]


def get_all_states() -> List[Dict[str, Any]]:
    """Returns sorted list of all 28 States and 8 Union Territories."""
    return sorted(INDIAN_STATES_AND_UTS, key=lambda s: s["name"])


def get_districts_for_state(state_id: str) -> List[Dict[str, str]]:
    """Returns administrative districts for the given state ID."""
    districts = DISTRICTS_BY_STATE.get(state_id, [])
    # Always guarantee at least an Other District option if not present
    if not any(d["name"].startswith("Other") for d in districts):
        districts = districts + [{"id": f"{state_id}-OTH", "name": "Other District"}]
    return sorted(districts, key=lambda d: (d["name"].startswith("Other"), d["name"]))


def search_cities_for_state(state_id: str, district_id: Optional[str] = None, query: Optional[str] = None, limit: int = 40) -> List[Dict[str, Any]]:
    """
    Searches cities within a state and optional district.
    Handles transliterations, aliases (e.g. Bombay -> Mumbai, Gurgaon -> Gurugram),
    and displays parent district/state clearly for disambiguation.
    """
    clean_q = (query or "").strip().lower()

    # 1. Gather all known cities for this state
    matched = []
    for c in CITIES_DATA:
        if c["state_id"] != state_id:
            continue
        if district_id and district_id != f"{state_id}-OTH" and c["district_id"] != district_id:
            continue

        if clean_q:
            # Check name and aliases
            name_match = clean_q in c["name"].lower()
            alias_match = any(clean_q in a.lower() for a in c.get("aliases", []))
            if not (name_match or alias_match):
                continue

        # Look up district name for clear display
        dist_list = DISTRICTS_BY_STATE.get(state_id, [])
        dist_name = next((d["name"] for d in dist_list if d["id"] == c["district_id"]), "District")
        state_obj = STATE_BY_ID.get(state_id, {})

        matched.append({
            "id": c["id"],
            "name": c["name"],
            "district_id": c["district_id"],
            "district_name": dist_name,
            "state_id": state_id,
            "state_name": state_obj.get("name", state_id),
            "tier": c["tier"],
            "tier_label": CLASSIFICATION_LABELS.get(c["tier"], {}).get("title", c["tier"]),
            "badge": CLASSIFICATION_LABELS.get(c["tier"], {}).get("badge", ""),
            "display_label": f"{c['name']} ({dist_name}, {state_obj.get('name', '')})"
        })

    # Sort matched cities: Metros first, then alphabetically
    tier_order = {"METRO": 1, "URBAN": 2, "TOWN": 3, "RURAL": 4, "UNCLASSIFIED": 5}
    matched.sort(key=lambda x: (tier_order.get(x["tier"], 99), x["name"]))

    return matched[:limit]


# -----------------------------------------------------------------------------
# 6. PIN CODE VERIFICATION LOGIC
# -----------------------------------------------------------------------------

def validate_indian_pincode(pincode: str, state_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Validates a 6-digit Indian PIN code and checks if it matches the selected state.
    Indian PIN code format: 6 digits, first digit 1-9 (cannot begin with 0).
    """
    clean_pin = (pincode or "").strip()

    if not clean_pin:
        return {"valid": False, "error": "PIN code cannot be empty.", "matches_state": True}

    if not re.match(r"^[1-9][0-9]{5}$", clean_pin):
        return {
            "valid": False,
            "error": "Indian PIN codes must be exactly 6 digits and cannot start with 0.",
            "matches_state": False
        }

    # If state_id provided, check postal circle
    if state_id and state_id in STATE_BY_ID:
        state_obj = STATE_BY_ID[state_id]
        prefixes = state_obj.get("postal_prefix", [])

        is_matching = any(clean_pin.startswith(p) for p in prefixes)
        if not is_matching:
            return {
                "valid": True,
                "clean_pincode": clean_pin,
                "matches_state": False,
                "warning": (
                    f"PIN code '{clean_pin}' usually belongs to a postal circle outside {state_obj['name']}. "
                    "Please double check if this is your intended PIN code."
                )
            }

    return {
        "valid": True,
        "clean_pincode": clean_pin,
        "matches_state": True,
        "message": "PIN code format verified."
    }


# -----------------------------------------------------------------------------
# 7. INDIA-ADAPTIVE 50/30/20 BUDGET RECOMMENDATION ENGINE
# -----------------------------------------------------------------------------

def calculate_adaptive_budget_recommendation(
    location_tier: str,
    monthly_income_minor: int,
    rent_minor: int = 0,
    essentials_minor: int = 0,
    debt_minor: int = 0,
    dependants_count: int = 0,
    currency: str = "INR"
) -> Dict[str, Any]:
    """
    Generates intelligent, transparent 50/30/20 recommendations based on location
    and user's actual contractual household commitments.
    Never forces an unrealistic allocation if essentials exceed 50%.
    """
    tier = location_tier or "UNCLASSIFIED"
    tier_info = CLASSIFICATION_LABELS.get(tier, CLASSIFICATION_LABELS["UNCLASSIFIED"])

    # Baseline total essential outflow
    total_essential_minor = (rent_minor or 0) + (essentials_minor or 0) + (debt_minor or 0)

    # If income is known and greater than zero, compute actual essential percentage
    if monthly_income_minor > 0:
        actual_needs_pct = round((total_essential_minor / monthly_income_minor) * 100, 1)
    else:
        actual_needs_pct = 0.0

    # Determine recommended preset
    recommended_preset_key = "standard"
    explanation = ""

    # CASE A: High contractual essential overhead (Essentials exceed 50%)
    if actual_needs_pct > 50.0:
        recommended_preset_key = "high_essential"
        calibrated_needs = min(max(round(actual_needs_pct / 5) * 5, 55.0), 75.0)
        remaining_pct = 100.0 - calibrated_needs
        calibrated_wants = round(remaining_pct * 0.45, 1)
        calibrated_savings = round(remaining_pct - calibrated_wants, 1)

        explanation = (
            f"Based on your recorded essential commitments (Rent/EMI, groceries, transit, debt), "
            f"your baseline essentials total {actual_needs_pct}% of take-home income. "
            f"Rather than enforcing an unrealistic 50% cap, we recommend our High Essential-Cost preset "
            f"({int(calibrated_needs)}% Needs, {int(calibrated_wants)}% Wants, {int(calibrated_savings)}% Savings) "
            f"to protect essential bills while preserving a consistent wealth-building habit."
        )
        recommended_preset = {
            "id": "high_essential",
            "title": "High Essential-Cost Preset",
            "needs": calibrated_needs,
            "wants": calibrated_wants,
            "savings": calibrated_savings,
            "is_calibrated": True
        }

    # CASE B: Low essential costs (Essentials <= 45% and not major metro, or Tier-Z / Rural)
    elif actual_needs_pct > 0 and actual_needs_pct <= 45.0 and tier in ("TOWN", "RURAL", "UNCLASSIFIED"):
        recommended_preset_key = "lower_cost"
        recommended_preset = BUDGET_PRESETS["lower_cost"].copy()
        explanation = (
            f"Your recorded essential commitments represent {actual_needs_pct}% of income. "
            "Living in a lower-cost regional hub creates significant headroom. "
            "We suggest our Lower-Cost Preset (45% Needs, 30% Wants, 25% Savings) to accelerate investments."
        )

    # CASE C: Major Metropolitan Area with standard or disciplined expenses
    elif tier == "METRO":
        recommended_preset_key = "metro"
        recommended_preset = BUDGET_PRESETS["metro"].copy()
        explanation = (
            "In major metropolitan areas (Mumbai, Delhi NCR, Bengaluru, Hyderabad, Chennai, etc.), "
            "lifestyle and discretionary leakages (frequent dining out, delivery apps, shopping) often dilute wealth. "
            "We recommend the Metropolitan Starting Preset (50% Needs, 25% Wants, 25% Savings) to maintain disciplined lifestyle spending."
        )

    # CASE D: Default standard 50/30/20
    else:
        recommended_preset_key = "standard"
        recommended_preset = BUDGET_PRESETS["standard"].copy()
        explanation = (
            "The classic 50/30/20 framework divides your income into 50% essential Needs, "
            "30% discretionary lifestyle Wants, and 20% automated Savings & Debt reduction."
        )

    return {
        "location_tier": tier,
        "tier_title": tier_info["title"],
        "tier_badge": tier_info["badge"],
        "tier_description": tier_info["description"],
        "monthly_income_minor": monthly_income_minor,
        "total_essential_minor": total_essential_minor,
        "actual_needs_pct": actual_needs_pct,
        "recommended_preset_key": recommended_preset_key,
        "recommended_preset": recommended_preset,
        "explanation": explanation,
        "available_presets": [
            BUDGET_PRESETS["standard"],
            BUDGET_PRESETS["metro"],
            BUDGET_PRESETS["high_essential"],
            BUDGET_PRESETS["lower_cost"]
        ]
    }
