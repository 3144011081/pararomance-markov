"""
generate.py
-----------
Command-line title generator (no GUI needed). Loads the trained model
and prints new fake paranormal-romance titles.

Usage:
    python src/generate.py
    python src/generate.py -n 15
    python src/generate.py -n 5 --model model.json
"""

import argparse
from pathlib import Path

from markov_model import MarkovChain

DEFAULT_MODEL = Path(__file__).resolve().parent.parent / "model.json"


def main():
    parser = argparse.ArgumentParser(description="Generate fake paranormal-romance titles.")
    parser.add_argument("-n", "--num", type=int, default=10, help="How many titles to generate.")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL, help="Path to trained model JSON.")
    args = parser.parse_args()

    if not args.model.exists():
        raise SystemExit(
            f"No trained model found at {args.model}.\n"
            f"Train one first with: python src/train.py"
        )

    chain = MarkovChain.load(args.model)
    titles = chain.generate_many(args.num)
    for t in titles:
        print(f"- {t}")


if __name__ == "__main__":
    main()
