# Pretino

Pretino is a web application that transforms the order objects returned by Pretix for an ITNOG event in a format that the website and meeting buttler can use.

## Configuration
 - PRETINO_ORGANIZER: Organizer name as set on Pretix
 - PRETINO_EVENT_NAME: Event name as set on Pretix
 - PRETINO_API_TOKEN: Pretix API token
 - PRETINO_QUESTION_MAPPING: JSON object (see below)
 - PRETINO_LOGLEVEL: Loglevel. Either ERROR, INFO or DEBUG
 - PRETINO_API_KEYS: JSON list (see below)
 - PRETINO_HOST: Host to bind to
 - PRETINO_PORT: Port to bind to

JSON schemas for the JSON objects are defined in the `schemas` directory.