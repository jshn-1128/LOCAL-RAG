"""
CLI entry point.

Purpose: Provide command-line interface for Local RAG operations.
Commands:
  ingest   — Ingest documents into the system.
  query    — Query the RAG system.
  chat     — Start interactive chat session.
  serve    — Start the FastAPI server.

Future milestone: Milestone 17 — CLI.
"""

import argparse
import sys


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="local-rag",
        description="Local RAG — Fully local, privacy-first RAG system",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("ingest", help="Ingest documents into the system")
    subparsers.add_parser("query", help="Query the RAG system")
    subparsers.add_parser("chat", help="Start an interactive chat session")
    subparsers.add_parser("serve", help="Start the FastAPI server")

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
