import itertools


def clean_words(words):
    cleaned_words = []

    for word in words:
        if word.endswith('.'):
            continue    
        for char in ['(', ')']:
            word = word.replace(char, '')
        cleaned_words.append(word)

    return cleaned_words


def build_full_name_variations(full_name):
    def build_variations(value):
        variations = []
        initial_words = [word for word in value.split(' ')]
        cleaned_words = clean_words(initial_words)

        for word in cleaned_words:
            if '-' in word:
                variations.extend(word.split('-'))

        if len(initial_words) > 1:
            variations.extend(cleaned_words)

        if len(cleaned_words) > 1:
            variations.append('-'.join(cleaned_words))

        return variations

    nameparts = [value.strip() for value in full_name.split(',')]

    if len(nameparts) != 2: 
        return [];

    surname, given_name = nameparts
    
    full_name_variations = list(itertools.product(
        [surname] + build_variations(surname),
        [given_name] + build_variations(given_name)
    ))

    if len(full_name_variations) > 2:
        full_name_tuple = full_name_variations[0]
        full_name_variations = full_name_variations[1:]
        full_name_variations.sort(key=lambda values: len(values[0] + values[1]), reverse=True)
        full_name_variations.insert(0, full_name_tuple)

    return full_name_variations


ldap_to_field_map = {
    "initials": ("initials", lambda attributes: attributes["initials"]),
    "sn": ("surname", lambda attributes: attributes["sn"]),
    "givenname": ("givenname", lambda attributes: attributes["givenname"]),
    "displayName": ("displayname", lambda attributes: attributes["displayName"]),
    "extensionattribute3": ("gender", lambda attributes: attributes["extensionattribute3"]),
    "extensionattribute6": ("team", lambda attributes: { 'LDAPDN': attributes["extensionattribute6"] }),
    "title": ("title", lambda attributes: attributes["title"]),
    "mail": ("mail", lambda attributes: attributes["mail"]),
    "ipphone": ("ipphone", lambda attributes: attributes["ipphone"]),
    "physicaldeliveryofficename": ("physicaldeliveryofficename", lambda attributes: attributes["physicaldeliveryofficename"]),
    "department": ("department", lambda attributes: { "id": 'department_' + attributes["department"] }),
    "distinguishedname": ("LDAPDN", lambda attributes: attributes["distinguishedname"]),
    "manager": ("manager", lambda attributes: { "LDAPDN": attributes["manager"] }),
    "directreports": ("directreports", lambda attributes: [{ "LDAPDN": dn } for dn in attributes["directreports"]]),
}


def read_person_values_from_ad_entry(entry):
    values = {}
    for attribute_name in ldap_to_field_map:
        if attribute_name in entry["attributes"]:
            field_name, field_mapper = ldap_to_field_map[attribute_name]
            values[field_name] = field_mapper(entry["attributes"])
    return values
