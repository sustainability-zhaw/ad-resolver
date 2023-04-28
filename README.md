# AD-Resolver

Resolve person records in an organisational directory service based on author names. 

## Context

Universities and research institutions have a person directory with relevant information about organisational members. Additionally, these institutions have a range of databases and information systems that refer to these persons. This includes course catalogs, publication databases, and project databases. In the person names in the different systems are not always identical. In order to align the names with the personal records variations of a names need to be tested. 

The names in seconday databases are called in the context of this service *author names*.

## Approach

The AD-Resolver uses the most significant match to identify a person. For this purpose the resolver creates a list of potential names from the initial *author names*. This is necessary because author names may have partial surnaes and/or partial or (partially) abbreviated firstnames. 

- Create a list of potential names based on a given author name.
- The list of potential names is ordered by descending length.
- Query the person directory for the potential names. 
- The match for the longest potential name is used as a person reference. 

### Border cases

- A match yields more than one person.
- For common names it is possible that a match is found even if the person is actually not identical with the author. 
- No match yielded for retired staff

If the longest match already yields more than one person, then no assignment is made.

If an author has a common name that matches a (different) person in the personal directory, then this is not detectable by this approach. This could get resolved, only if organisational affiliations would be available and get traced via the personal records. This is not possible. Because even with common names with appears to be a rare case, we consider it as an acceptable error. 

If persons retire from the organiation, then they are removed from the person directory. In this case no match is generated for this person.  

### Special case

A special case is given when person change their surnames at marriage. This is partially covered by the longest match approach. If a person *replaces* the surname *completely*, the AD-Resolver cannot identify that relation. This kind of matching requires special knowledge that is not represented in the personal records.

### Deploy on Docker

```yaml
version: "3.8"
services:
  resolver:
    image: ghcr.io/sustainability-zhaw/ad-resolver:main
    restart: unless-stopped
    networks:
      - servicenet
    environment:
      DB_HOST: ${YOUR_GRAPHQL_ENDPOINT}
    secrets:
      - source: resolver_config
        target: /etc/app/secrets.json

networks: 
  servicenet: 
    external: true

secrets: 
  resolver_config:
    external: true
    name: ${NAME_OF_CONFIGURATION_RECORDS}
```

### Configuration File

The configuration file has to be anchored at `/etc/app/secrets.json`. The configuration MUST be stored in JSON-format. 

The configuration file MUST be stored as a SECRET because it contains the service credentials for accessing the (external) directory service. 

The file is organised as follows:

```json
{
   "ad_user": "foobar",
   "ad_password": "barbaz"
}
```

### Configuration Variables

The main service configuration is set via environment variables. 

- `AD_HOST` - domain, host, or IP of the directory host
- `DB_HOST` - host or IP of the graphQL endpoint
- `LOG_LEVEL` - log level for tracing and debugging, default is `ERROR`
