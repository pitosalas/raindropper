# Project Specification

## Overview
Manage ad clean up Raindrop.io tags and bookmarks

## Users
Marjor raindrop users

## Problem
Removes clutter and noise from my raindrop database

## Key Features
- use the raindrop api
- prints a list of options and user picks one by typing a number
- works on a list of items (selection set)
- options are
  - Select all tags which are used just once and save them in selection set
  - Print selection set
  - More to come

## Tag Linting Rules
- tags are gemerally nouns that have a meaning without more context
- tags are generally but not always single words
- Find tags that are simple variations of each other. Use the singular, throw out the plural.
- Look at similar stems and consider deleting one of them

## Constraints
- python 3.10+
- raindrop.io api
- launched from command line
- 
## Out of Scope
- no gui
- very simple
- 