# raindropper

A CLI tool for cleaning up tags and bookmarks in [Raindrop.io](https://raindrop.io).

## What it does

Raindropper helps you reduce clutter in your Raindrop database by letting you build a **selection set** — a working list of tags or bookmarks — then act on it. You pick actions from a numbered menu; the selection set accumulates across actions within a session.

## Menu options

| Option | Description |
|---|---|
| Select single-use tags | Load tags used on exactly one bookmark into the selection set |
| Select gibberish tags | Load tags that look like gibberish (digits mixed in, or ≤3 chars with no vowels) |
| Select multi-word tags | Load tags that contain spaces and contain only real words |
| Select bookmarks with mixed tags | Load bookmarks that have both single-use and multi-use tags |
| Remove stop words | Strip common English stop words from the selection set |
| Print selection set | Display current contents of the selection set |
| Split multi-word tags on bookmarks | For each multi-word tag in the set, replace it with its individual words on all affected bookmarks |
| Delete tags in selection set | Delete all tags in the selection set from Raindrop (with confirmation) |

## Setup

Requires a Raindrop.io API token. Store it in Doppler under project `raindrop`, config `dev_personal` as `RAINDROP_TOKEN`.

```bash
# Install dependencies
uv sync

# Generate .env from Doppler
doppler secrets download --no-file --format env --project raindrop --config dev_personal > .env

# Run
uv run raindropper
```

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [Doppler CLI](https://docs.doppler.com/docs/cli) (for secrets)
- A Raindrop.io account and API token
