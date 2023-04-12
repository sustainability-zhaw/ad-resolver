import datetime
import logging
import db
import ldap
import utils

logger = logging.getLogger("ad_resolver")

def update_author(payload):
    if not ldap.connected():
        logger.debug("Connecting to active directory")
        ldap.connect()

    logger.debug(f'Querying author {payload}')
    author = db.query_author_by_fullname(payload['fullname'])

    if not author:
        logger.debug(f'Author not found')
        return
    elif author['ad_check']:
        logger.debug('Skipping already checked author')
        return

    try:
        logger.debug(f"Processing author: {author}")
        person_update = None

        if author["person"]:
            if not author["person"]["ad_check"]:
                logger.debug(f"Searching active directory for person with dn {author['person']['LDAPDN']}")
                status, result, response = ldap.find_person_by_dn(author["person"]["LDAPDN"])
                if len(response):
                    person_update = utils.read_person_values_from_ad_entry(response[0])
                else:
                    person_update = { "LDAPDN": author["person"]["LDAPDN"], "retired": 1 }
        else:
            for surname, given_name in utils.build_full_name_variations(author["fullname"]):
                logger.debug(f"Searching active directory for person with sn {surname} and givenName {given_name}")
                status, result, response = ldap.find_person_by_surename_and_given_name(surname, given_name)
                if len(response) == 1:
                    # if more than 1 match is returned it is impossible to map an author to a person.
                    person_update = utils.read_person_values_from_ad_entry(response[0])
                    break

        update_time = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        author_update = { "ad_check": update_time }

        if person_update:
            author_update["person"] = { "LDAPDN": person_update["LDAPDN"] }

        logger.debug(f"Updating author: {author_update}")
        result = db.update_author(author["fullname"], author_update)

        if person_update:
            person_update["ad_check"] = update_time
            person_ldapdn = person_update["LDAPDN"]
            logger.debug(f"Updating person: {person_update}")
            del person_update["LDAPDN"]
            # This relys on update_author() creating non existing person objects.
            db.update_person(person_ldapdn, person_update)

    except:
        logger.exception(f'Failed to process author: {author}')

    # TODO: Send update message


def run(message_key, payload):    
    logger.info(f"received message {message_key}: {payload}")
    update_author(payload)
