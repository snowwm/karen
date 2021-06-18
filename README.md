# karen

[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

This VK bot notifies all chat members when someone edits or deletes a message.
The bot also shows message's old text (stored in a database for this purpose).
Minor edits (with [Damerau–Levenshtein distance](https://en.wikipedia.org/wiki/Damerau–Levenshtein_distance) up to 3) and non-textual edits are ignored.

## Usage

You can run this bot on Heroku or any other server.
You will also need a MongoDB database. Provide it in the env variable `AFH_DB_URL` (like `AFH_DB_URL=mongodb://user:pass@example.com/db-name`).

You can get a cloud MongoDB instance for free on https://www.mongodb.com/cloud (there's a web UI and VS Code plugin for editing data).

App configuration is stored as JSON in the database table `singletons`. It looks like:

```json
{
  "_id": "config",
  "access_token": "VK group API token here",
  "logging": {
    "version": 1,
    "incremental": true,
    "loggers": {
      "karen": {
        "level": "INFO"
      }
    }
  }
}
```

It's also a good idea to create a [TTL index](https://docs.mongodb.com/manual/tutorial/expire-data/) to remove old messages from the DB.

## Todo

- commands
  - help
  - per-chat settings?
- tone analysis ([example](https://github.com/Ngoroth/Toxicometer))
  - warn people if they are being toxic
- ChatOps
- integrate some bot framework, become channel-agnostic
