from ldap3 import Server, Connection, SAFE_SYNC
import settings


_connection = None


def connected():
    global _connection
    return _connection != None and _connection.bound


def requires_connection(func):
    def check_connection(*args, **kwargs):
        if not connected():
            raise Exception("Not connected to active directory. Did you forget to call connect()?")
        return func(*args, **kwargs)
    return check_connection


def connect():
    global _connection
    _connection = Connection(
        server=Server(settings.AD_HOST),
        user=settings.AD_USER,
        password=settings.AD_PASS,
        auto_bind=True, 
        client_strategy=SAFE_SYNC
    )
    return connected()


@requires_connection
def find_person_by_surename_and_given_name(surname, given_name):
    global _connection
    status, result, response, _ = _connection.search(
        search_base="OU=Staff,OU=AUM,DC=zhaw,DC=ch",
        search_filter=f"(&(objectclass=person)(objectclass=user)(objectclass=organizationalPerson)(sn={surname})(givenName={given_name}))",
        attributes=["*"],
        size_limit=2
    )
    return status, result, response
    

@requires_connection
def find_person_by_dn(dn):
    global _connection
    status, result, response, _ = _connection.search(
        search_base="OU=Staff,OU=AUM,DC=zhaw,DC=ch",
        search_filter=f"(&(objectclass=person)(objectclass=user)(objectclass=organizationalPerson)(distinguishedName={dn}))",
        attributes=["*"],
        size_limit=1,
    )
    return status, result, response
