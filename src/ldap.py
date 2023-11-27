from ldap3 import Server, Connection, SAFE_RESTARTABLE
from ldap3.utils.conv import escape_filter_chars
from settings import settings


_connection = Connection(
    server=Server(settings.AD_HOST, connect_timeout=30),
    user=settings.AD_USER,
    password=settings.AD_PASS,
    auto_bind=True, 
    client_strategy=SAFE_RESTARTABLE,
    lazy=True,
    receive_timeout=30
)


def find_person_by_surename_and_given_name(surname, given_name):
    _, _, response, _ = _connection.search(
        search_base="OU=Staff,OU=AUM,DC=zhaw,DC=ch",
        search_filter="(&(objectclass=person)(objectclass=user)(objectclass=organizationalPerson)(sn={})(givenName={}))".format(
            escape_filter_chars(surname),
            escape_filter_chars(given_name)
        ),
        attributes=["*"],
        size_limit=2
    )
    return response
    

def find_person_by_dn(dn):
    _, _, response, _ = _connection.search(
        search_base="OU=Staff,OU=AUM,DC=zhaw,DC=ch",
        search_filter="(&(objectclass=person)(objectclass=user)(objectclass=organizationalPerson)(distinguishedName={}))".forrmat(
            escape_filter_chars(dn)
        ),
        attributes=["*"],
        size_limit=1,
    )
    return response
