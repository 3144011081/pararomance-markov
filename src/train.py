"""
train.py
--------
Train a Markov chain on the paranormal-romance title dataset and save it
to disk so the GUI (or anything else) can load it instantly without
retraining every time.

Usage:
    python src/train.py
    python src/train.py --order 2 --data data/pararomance_titles.txt --out model.json
"""

import argparse
from pathlib import Path

from markov_model import MarkovChain, load_titles

DEFAULT_DATA = Path(__file__).resolve().parent.parent / "data" / "pararomance_titles.txt"
DEFAULT_OUT = Path(__file__).resolve().parent.parent / "model.json"


def main():
    parser = argparse.ArgumentParser(description="Train a Markov chain title generator.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="Path to training titles (one per line).")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Where to save the trained model (JSON).")
    parser.add_argument("--order", type=int, default=2, help="Markov chain order (state size, in words). Try 1-3.")
    args = parser.parse_args()

    print(f"Loading titles from {args.data} ...")
    titles = load_titles(args.data)
    print(f"Loaded {len(titles)} cleaned titles.")

    print(f"Training order-{args.order} Markov chain ...")
    chain = MarkovChain(order=args.order).fit(titles)
    print(f"Learned {len(chain.table)} unique states.")

    chain.save(args.out)
    print(f"Saved model to {args.out}")

    print("\nSample generations:")
    for title in chain.generate_many(5):
        print(f"  - {title}")


if __name__ == "__main__":
    main()
