import itertools
import re


def build_full_name_variations(full_name: str):
    surname_and_given_name = [value.strip() for value in full_name.split(',')]
    
    if len(surname_and_given_name) != 2:
        return []

    surname_and_given_name_words = [None, None]

    for index, value in enumerate(surname_and_given_name):
        # Matches unicode characters
        words = re.findall(r'[\w+-]+\b(?!\.)', value)
        generated_words = []

        if len(words) > 1:
            generated_words.append('-'.join(words))
        
        for word in words:
            if '-' in word: 
                generated_words.extend(word.split('-'))

        # Adding original name part at the top
        if value not in words:
            words = [value] + words

        surname_and_given_name_words[index] = words + generated_words

    full_name_variations = list(itertools.product(
        surname_and_given_name_words[0],
        surname_and_given_name_words[1]
    ))

    # Input stays at the top because it is the most likely to be found in the active directory.
    full_name_variations[1:] = sorted(
        full_name_variations[1:], 
        key=lambda values: len(values[0] + values[1]), reverse=True
    )

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
