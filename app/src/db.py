from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import settings

# import logging
# logger = logging.getLogger("ad_resolver")

_client = Client(
    transport=RequestsHTTPTransport(url=f"http://{settings.DB_HOST}/graphql"),
    fetch_schema_from_transport=True
)


def query_unchecked_author_batch():
    return _client.execute(
        gql(
            """
            query ($batchSize:Int) { 
                queryAuthor(filter: { ad_check: { eq: null } }, first:$batchSize) { 
                    fullname 
                    ad_check 
                    person { 
                        LDAPDN
                        retired
                        ad_check
                    }
                } 
            }
            """
        ),
        variable_values={"batchSize": settings.BATCH_SIZE}
    )['queryAuthor']


def update_author(fullname, input):
    result = _client.execute(
        gql(
            """
            mutation updateAuthor($authorUpdate: UpdateAuthorInput!){ 
                updateAuthor(input: $authorUpdate) {
                    author { 
                        fullname 
                    }
                } 
            }
            """
        ),
        variable_values={
            "authorUpdate": {
                "filter": { "fullname": { "eq": fullname } },
                "set": input
            }
        }
    )



def update_person(ldapdn, input):
    _client.execute(
        gql(
            """
            mutation updatePerson($personUpdate: UpdatePersonInput!){ 
                updatePerson(input: $personUpdate) {
                    person { LDAPDN }
                }
            }
            """
        ),
        variable_values={"personUpdate": {
            "filter": { "LDAPDN": { "eq": ldapdn } },
            "set": input
        }}
    )
