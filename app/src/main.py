import datetime
import logging
import sys
import time
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from ldap3 import Server, Connection, SAFE_SYNC
import settings


logging.basicConfig(level=settings.LOG_LEVEL, handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("ldap_resolver")

logger.debug("Connecting to active directory")
active_directory = Connection(
    server=Server(settings.AD_HOST),
    user=settings.AD_USER,
    password=settings.AD_PASS,
    auto_bind=True, 
    client_strategy=SAFE_SYNC
)

if not active_directory.bound:
    raise Exception("Failed to connect to active directory")

logger.debug("Connected to active directory")

graphql = Client(
    transport=RequestsHTTPTransport(url=f"http://{settings.DB_HOST}/graphql"),
    fetch_schema_from_transport=True
)

# TODO: Filter by resolve state = unresolved
logger.debug(f"Querying person batch with size of {settings.BATCH_SIZE}")
person_batch = graphql.execute(
    gql("query ($batchSize:Int) { queryPerson(first:$batchSize) { fullname } }"),
    variable_values={"batchSize": settings.BATCH_SIZE}
)

logger.debug("Processing person batch of size {result_size}".format(result_size=len(person_batch["queryPerson"])))

for person in person_batch["queryPerson"]:
    logger.debug("Querying active directory for person: {person}".format(person=person))
    lastname, firstname = [str.strip(value) for value in str.split(person["fullname"], ",")]
    status, result, response, _ = active_directory.search(
        search_base="OU=AUM,DC=zhaw,DC=ch",
        search_filter=f"(&(objectclass=person)(objectclass=user)(objectclass=organizationalPerson)(sn={lastname})(givenName={firstname}))",
        attributes=["*"],
        size_limit=2,
    )

    # TODO: Mark as processed and (resolved or unresolved)
    person_update = {
        "filter": { "fullname": {"eq": person["fullname"]}},
        "set": { 'dateUpdate': datetime.datetime.now(datetime.timezone.utc).isoformat() }
    }

    if not status:
        logging.warning("No matching AD entries found for person: {person}".format(person=person))
        continue
    elif len(response) != 1:
        logging.warning("{match_size} matching AD entries found for Person: {person}".format(person=person, match_size=len(response)))
        continue
    else:
        ldap_to_field_map = {
            "initials": ("initials", lambda attributes: attributes["initials"]),
            "surname": ("surname", lambda attributes: attributes["surname"]),
            "givenname": ("givenname", lambda attributes: attributes["givenname"]),
            "displayName": ("displayname", lambda attributes: attributes["displayName"]),
            "extensionattribute3": ("gender", lambda attributes: attributes["extensionattribute3"]),
            "title": ("title", lambda attributes: attributes["title"]),
            "mail": ("mail", lambda attributes: attributes["mail"]),
            "ipphone": ("ipphone", lambda attributes: attributes["ipphone"]),
            "physicaldeliveryofficename": ("physicaldeliveryofficename", lambda attributes: attributes["physicaldeliveryofficename"]),
            "department": ("department", lambda attributes: { "id": attributes["department"] }),
            "distinguishedname": ("LDAPDN", lambda attributes: attributes["distinguishedname"])
        }

        for attribute_name in ldap_to_field_map:
            if attribute_name in response[0]["attributes"]:
                field_name, field_mapper = ldap_to_field_map[attribute_name]
                person_update["set"][field_name] = field_mapper(response[0]["attributes"])

    logger.debug("Executing person update: {person_update}".format(person_update=person_update))
    graphql.execute(
        gql(
            """
            mutation updatePerson($personUpdate: UpdatePersonInput!){ 
                updatePerson(input: $personUpdate) {
                    person { fullname }
                } 
            }
            """
        ),
        variable_values={"personUpdate": person_update}
    )
