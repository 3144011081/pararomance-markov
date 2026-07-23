# Paranormal Romance Title Generator 🌙📖

A word-level Markov chain (built from scratch, no external libraries)
trained on ~4,000 real paranormal-romance book titles. It learns how
titles in this genre are put together, then generates new, original
(fake) ones — with a desktop GUI or a command-line tool.

This project pairs with the "Introduction to Markov Chains" notebook:
same core idea (states + weighted transition probabilities), applied
to text generation instead of the maze/weather examples.

## Project structure

```
pararomance-markov/
├── data/
│   └── pararomance_titles.txt   # training data (one title per line)
├── src/
│   ├── markov_model.py          # the Markov chain engine
│   ├── train.py                 # CLI: trains the model, saves model.json
│   ├── generate.py              # CLI: generates titles from a trained model
│   └── gui.py                   # Desktop GUI (Tkinter)
├── model.json                   # trained model (created by train.py)
└── README.md
```

## Requirements

Pure Python standard library only — **nothing to `pip install`**.

- Python 3.9+
- Tkinter, for the GUI only. It ships with most Python installs, but on
  some Linux distros it's a separate system package:
  ```bash
  # Debian/Ubuntu
  sudo apt-get install python3-tk

  # Fedora
  sudo dnf install python3-tkinter

  # macOS / Windows: already included with python.org installers
  ```

## 1. Train the model

Run this once (or any time you want to retrain with a different order):

```bash
cd pararomance-markov
python3 src/train.py
```

This reads `data/pararomance_titles.txt`, builds the Markov chain, and
saves it to `model.json`. It also prints 5 sample generated titles so
you can sanity-check the result immediately.

Optional flags:

```bash
# Use a different "order" (how many previous words the chain looks at).
# 1 = looser, more chaotic/creative titles.
# 2 = good default balance (recommended).
# 3 = tighter, closer to real titles, but can just reproduce originals.
python3 src/train.py --order 1
python3 src/train.py --order 3

# Point at a different dataset or output path
python3 src/train.py --data data/pararomance_titles.txt --out model.json
```

## 2. Generate titles

### Option A — GUI (recommended)

```bash
python3 src/gui.py
```

- Click **✨ Generate** to get a fresh batch of titles.
- Adjust **How many titles** and **Chain order** at the top (changing
  order automatically retrains).
- Click **↻ Retrain model** to retrain from scratch at any time.
- Click **Save results to file** to write the current list to
  `generated_titles.txt`.

The GUI trains a model automatically on first launch if `model.json`
doesn't exist yet, so you can technically skip step 1.

### Option B — Command line

```bash
python3 src/generate.py -n 10
```

```bash
# generate 20 titles from a specific model file
python3 src/generate.py -n 20 --model model.json
```

## How it works (short version)

For each title, the text is split into words and padded with `BEGIN`
and `END` markers. For every window of `order` consecutive words (a
"state"), we record which word came next, and how often. To generate
a new title, we start from a real title-opening state, then repeatedly
pick a next word at random — weighted by how often that word followed
that state in the real data — until we land on `END`.

This is exactly the "transition matrix" concept from the notebook,
just implemented as a sparse dictionary instead of a dense matrix
(a full matrix over ~9,700 states would be enormous and mostly zeros).

## Notes on the dataset

`data/pararomance_titles.txt` is the title list you provided. Titles
that were truncated with a trailing `...` in the source data are
cleaned (the truncation marker is stripped) before training, so the
model doesn't learn to end titles mid-word.
# pararomance-markov
