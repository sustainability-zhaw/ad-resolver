from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from settings import settings


_client = Client(
    transport=RequestsHTTPTransport(url=f"http://{settings.DB_HOST}/graphql"),
    fetch_schema_from_transport=True
)


def query_authors_by_info_object_link(link):
    result = _client.execute(
        gql(
            """
            query($link: String!) {
                getInfoObject(link: $link) {
                    authors {
                        fullname
                        ad_check
                        person {
                            LDAPDN
                            retired
                            ad_check
                        }
                    }
                } 
            }
            """
        ),
        variable_values={"link": link}
    )["getInfoObject"]
    return result["authors"] if result else []


def update_author(author):
    data = author.copy()
    del data["fullname"]
    _client.execute(
        gql(
            """
            mutation updateAuthor($patch: UpdateAuthorInput!) {
                updateAuthor(input: $patch) {
                    author {
                        fullname
                    }
                }
            }
            """
        ),
        variable_values={
            "patch": {
                "filter": { "fullname": { "eq": author["fullname"] } },
                "set": data
            }
        }
    )


def upsert_person(person):
    _client.execute(
        gql(
            """
            mutation ($person: [AddPersonInput!]!) {
                addPerson(input: $person, upsert: true) {
                    person { 
                        LDAPDN
                    }
                }
            }
            """
        ),
        variable_values={
            "person": [person]
        }
    )
