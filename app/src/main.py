import datetime
import logging
import time
import db
import ldap
import settings
import utils


logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)
logger = logging.getLogger("ldap_resolver")

logger.debug("Connecting to active directory")
ldap.connect()


while True:
    logger.debug(f"Querying next unchecked author batch of size {settings.BATCH_SIZE}")
    for author in db.queryUncheckedAuthorBatch():
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
                logger.debug("Searching active directory for person with sn {surname} and givenName {given_name}")
                status, result, response = ldap.find_person_by_surename_and_given_name(surname, given_name)
                if len(response):
                    # TODO: Decide what to do if more than 1 match is returned.
                    person_update = utils.read_person_values_from_ad_entry(response[0])
                    break

        update_time = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

        author_update = { "ad_check": update_time }
        if person_update:
            author_update["person"] = { "LDAPDN": person_update["LDAPDN"] }
        logger.debug(f"Updating author: {author_update}")
        result = db.updateAuthor(author["fullname"], author_update)

        if person_update:
            person_update["ad_check"] = update_time
            person_ldapdn = person_update["LDAPDN"]
            logger.debug(f"Updating person: {person_update}")
            del person_update["LDAPDN"]
            # This relys on updateAuthor() creating non existing person objects.
            db.updatePerson(person_ldapdn, person_update)

    logger.debug(f"Waiting for {settings.BATCH_INTERVAL} seconds until next batch run")
    time.sleep(settings.BATCH_INTERVAL)
