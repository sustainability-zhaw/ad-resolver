import datetime
import logging
import db
import ldap
import utils


logger = logging.getLogger("ad_resolver")


def resolve_author(author):
    author_has_person = author["person"] is not None
    ad_entry = None

    if author_has_person:
        response = ldap.find_person_by_dn(author["person"]["LDAPDN"])
        ad_entry = response[0] if len(response) else None
    else:
        for surname, given_name in utils.build_full_name_variations(author["fullname"]):
            response = ldap.find_person_by_surename_and_given_name(surname, given_name)
            ad_entry = response[0] if len(response) == 1 else None

    person = {}

    if ad_entry:
        person.update(utils.read_person_values_from_ad_entry(ad_entry))
        person["retired"] = 0
    elif not ad_entry and author_has_person:
        person.update({ "LDAPDN": author["person"]["LDAPDN"], "retired": 1 })

    update_time = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    db.update_author({ "fullname": author["fullname"], "ad_check": update_time })

    if person:
        person.update({ "ad_check": update_time, "pseudonyms": [{"fullname": author["fullname"]}] })
        db.upsert_person(person)

    return bool(person)


def resolve_authors(link):
    has_resolved_any_author = False
    authors = db.query_authors_by_info_object_link(link)
    unchecked_authors = [author for author in authors if not author["ad_check"]]
    for author in unchecked_authors:
        success = resolve_author(author)
        has_resolved_any_author = success or has_resolved_any_author
    return has_resolved_any_author


def run(routing_key, body):
    return resolve_authors(body["link"])
