import argparse
import os
import sys

from src.brain import SecondBrain
from src.config import DEFAULT_TOP_K


def cmd_index(args: argparse.Namespace) -> None:
    brain = SecondBrain()
    result = brain.index(args.folder, skip_existing=not args.reindex)
    print(
        f"Done — indexed: {result['indexed']}, "
        f"skipped: {result['skipped']}, "
        f"failed: {result['failed']}"
    )


def cmd_search(args: argparse.Namespace) -> None:
    brain = SecondBrain()
    hits = brain.search(args.query, top_k=args.top_k)
    if not hits:
        print("No results found.")
        return
    for i, hit in enumerate(hits, 1):
        score_pct = f"{hit['score'] * 100:.1f}%"
        print(f"\n[{i}] {hit['filename']}  (score: {score_pct})")
        print(f"    {hit['path']}")
        preview = hit["text"][:200].replace("\n", " ")
        print(f"    {preview}...")

    top_path = hits[0]["path"]
    print(f"\nOpening top result...")
    os.system(f"open '{top_path}'")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="second-brain",
        description="Semantic search for your screenshots",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    idx = sub.add_parser("index", help="Index a folder of screenshots")
    idx.add_argument("folder", help="Path to screenshot folder")
    idx.add_argument(
        "--reindex",
        action="store_true",
        help="Re-index files already in the database",
    )
    idx.set_defaults(func=cmd_index)

    srch = sub.add_parser("search", help="Search indexed screenshots")
    srch.add_argument("query", help="Natural language query")
    srch.add_argument(
        "-k",
        "--top-k",
        type=int,
        default=DEFAULT_TOP_K,
        dest="top_k",
        help=f"Number of results to return (default: {DEFAULT_TOP_K})",
    )
    srch.set_defaults(func=cmd_search)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
