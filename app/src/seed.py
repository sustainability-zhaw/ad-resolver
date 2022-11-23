
from ldap3 import Server, Connection
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import settings


server = Server(settings.AD_HOST)
conn = Connection(server, settings.AD_USER, settings.AD_PASS, auto_bind=True)

conn.search(
    search_base="OU=P_E,OU=_N,OU=Staff,OU=AUM,DC=zhaw,DC=ch",
    search_filter="(&(objectclass=person)(objectclass=user)(objectclass=organizationalPerson)(displayName=*))", 
    size_limit=10,
    attributes=["sn", "givenname"]
)
conn.unbind()

persons = []
for entry in conn.entries:
  persons.append({
    "fullname": f"{entry['sn']}, {entry['givenName']}"
  })

transport = RequestsHTTPTransport(url=f"http://{settings.DB_HOST}/graphql")
client = Client(transport=transport, fetch_schema_from_transport=True)
query = gql(
  """
  mutation addAllPersons($persons: [AddPersonInput!]!) { 
    addPerson(input: $persons) { 
      person { fullname }
    }
  }
  """
)
result = client.execute(query, variable_values={"persons": persons})
print(result)
