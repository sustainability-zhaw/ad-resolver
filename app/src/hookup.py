import datetime
import logging
import db
import ldap
import settings
import utils


logger = logging.getLogger("ad_resolver")


def run():
    if not ldap.connected():
        logger.debug("Connecting to active directory")
        ldap.connect()

    logger.debug(f"Querying next unchecked author batch of size {settings.BATCH_SIZE}")
    for author in db.query_unchecked_author_batch():
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
                person_update["ad_check"] = update_time
                author_update["person"]   = person_update
                author_update["objects"] = { "departments" : [{"id": person_update['department']['id']}]}
            
            logger.debug(f"Updating author: {author_update}")
            result = db.update_author(author["fullname"], author_update)

        except:
            logger.exception(f'Failed to process author: {author}')
        break