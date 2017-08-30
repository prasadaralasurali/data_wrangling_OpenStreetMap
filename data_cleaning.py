def clean_street_name(name):
    import re
    street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

    mapping = { "St": "Street",
                "St.": "Street",
                'street': 'Street', 
                "Ave": "Avenue",
                "Ave.": "Avenue",
                'AVE': 'Avenue',
                'avenue': 'Avenue',
                "Rd.": "Road",
                '104th': '104',
                 '806': '',
                 'Blvd': 'Boulevard',
                 'North-West': 'NW',
                 'North-west': 'NW',
                 'Northwest': 'NW',
                 'Rd': 'Road',
                 'St': 'Street',
                 'W': 'NW'
                  }

    m = street_type_re.search(name)
    street_type = m.group()
    if street_type == 'NW':
        name = clean_street_name(name[:-3].strip()) + " NW"
    else:
        if street_type in mapping:
            name = name.replace(street_type, mapping[street_type])        

    return name

def clean_postal_code(code):
    
    mapping = { 'T6E 4R9 Commute to Downtown Edmonton   4 min  24 min  8 min  30 min View Routes Check Availability Favorite Map Nearby Apartments': "T6E 4R9",
                "AB T6E4S6": "T6E4S6",
                }
    if code in mapping:
        code = mapping[code]
#convert postal code to "X1Y 2Z3" format which is the standard format in Canada
    code = code.upper()
    code = code.replace(" ", "")
    code = code.replace("-", "")        
    code = code[:3] + " " + code [3:]
    return code


def clean_phone_number(phone):
    phone_number = ""
    for ch in phone:
        if ch in "0123456789":
            phone_number += ch
#extract phone number without country code
    phone_number = phone_number[-10:]
#format phone number and add contry code
    phone_number_components = ['1', phone_number[0:3], phone_number[3:6], phone_number[6:]]
    phone_number_cleaned = "-".join(phone_number_components)            
    return phone_number_cleaned

def clean_house_number(house_number):
    
    mapping = {'10200 Suite 1259': '1259-10200', 
               '111000 Suite K6': 'K6-111000',
               '8525.0': '8525',
               '#200 10150': '200:10150',
               'Main Address\t10015': '10015',
               'Suite 220-10423':'220-10423' 
                }
    if house_number in mapping:
        house_number = mapping[house_number]
    return house_number


