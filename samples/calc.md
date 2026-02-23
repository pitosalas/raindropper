# Project Specification: calc

## Overview
A minimal command-line calculator

## Users
Developers learning the j2 framework workflow. This spec exists to test the simplest possible end-to-end project.

## Problem
Demonstrates that the j2 workflow functions correctly with a trivially simple project.

## Key Features
- tool is called calc
- run it with uv run calc
- accepts one, two or three arguments
  - 1 argument: a positive or negative number; echoes it back, otherwise prints an error
  - 2 arguments: <+ or -> <number>: treats as 0 <op> <number> and prints result, otherwise error
  - 3 arguments: <number> <+ - * or /> <number>: prints answer, otherwise error
- also accepts a full arithmetic expression across any number of arguments, joined and evaluated as one expression
  - supports +, -, *, / and parentheses ()
  - example: uv run calc "(3 + 4) * 2"  or  uv run calc 3 + 4 * 2
- output is integer when result is whole, float only when result is non-integer
- division by zero prints an error message (does not crash)
- invalid expression prints an error message (does not crash)

## Constraints
- Python 3.10+

## Out of Scope
