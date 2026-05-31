# DAFNA

Search for and generate DNA secondary structures (G-quadruplexes, i-motifs,
hairpins, triplexes) using finite automata.

[DAFNA tutorial](https://colab.research.google.com/drive/1JRkKK-3yBIT7gCNQMs1inFMF0euY29qf?usp=sharing)
for a quick start.

## Installation

Compatible with Windows and Linux. Building the package compiles the C++ engine,
so a C++ toolchain and CMake are required.

```
pip install git+https://github.com/myurushkin/dfalib
```

For local development (editable install):

```
pip install -e .
```

## Command-line interface

Installing the package provides a `dafna` command (equivalently
`python -m dafna`). It is driven by a config file — see [`example.conf`](example.conf).

```
dafna run CONFIG [--mode gen|scan] [--in PATH] [--out PATH] [--plugin MODULE]... [--limit N]
dafna validate CONFIG
```

Two modes:

- **`gen`** — enumerate DNA strings that realise the requested structures within
  a strength window (and an optional fixed length).
- **`scan`** — read an input sequence (FASTA or plain text) and report the
  strength of each enabled structure found in it.

Output is tab-separated with a header carrying the project name and date (handy
for batch parsing); the first columns are the sequence and its source, followed
by one strength column per measurable structure.

```
# enumerate quadruplexes/i-motifs/hairpins/triplexes described by the config
dafna run example.conf

# scan a FASTA file, overriding the mode and input from the command line
dafna run example.conf --mode scan --in sequences.fa --out results.tsv

# check a config without running (no engine or plugins required)
dafna validate example.conf
```

## Config format

A config is a sequence of `&BLOCK ... &END` sections; `#` starts a comment.

```
&GQD T                  # enable G-quadruplexes (T = on, F/omitted = off)
TOP=all                 # 'all', or a list e.g. [canonical,tandem]
STR_MIN=2               # strength window (defaults: 2..5)
STR_MAX=3
&END

&IMT T                  # i-motifs
&END
&HRP T                  # hairpins
&END
&TRX T                  # triplexes
&END

&GEN                    # general settings
PROJECT=demo            # project name (printed with the date on the first line)
MODE=gen                # 'gen' or 'scan'
LEN=MIN                 # fixed length (integer) or MIN for the shortest
# IN=sequences.fa       # input for MODE=scan
# OUT=results.tsv       # output file (defaults to stdout)
&END
```

Built-in structures: **GQD** (topologies `canonical`, `tandem`), **IMT**,
**HRP**, **TRX**.

## Extending with your own structures

### Inline, in the config (no code)

Add a `&CUSTOM` block with a strength-parameterised pattern. `{s}` (and
expressions like `{2*s}` or `{s+1}`) expand to literal repetition for each
strength in the window.

```
&CUSTOM myquad
PATTERN=X* g{s} X+ g{s} X+ g{s} X+ g{s} X*
STR_MIN=2
STR_MAX=3
# SIMPLE=Z:a|c          # optional extra named patterns usable in PATTERN
&END
```

`X` (= `a|c|g|t`) is always available. A custom structure has no strength
function, so it is *generated* in gen mode and matched by *membership* in scan
mode (the largest strength whose pattern accepts the sequence).

### Python plugins (full power)

A plugin is a module that registers a structure — with its own generator(s) and,
optionally, a strength function — into the registry on import:

```python
# my_structures.py
from dafna.lib.generation.template import make_template_generator
from dafna.lib.registry import StructureDef, register


def polya_strength(seq: str) -> int:
    """Strength = length of the longest run of consecutive 'a's."""
    best = run = 0
    for char in seq.lower():
        run = run + 1 if char == "a" else 0
        best = max(best, run)
    return best


register(StructureDef(
    name="POLYA",
    generators={"canonical": make_template_generator("X* a{s} X*")},
    strength_fn=polya_strength,
    description="poly-A run",
))
```

Load it via `--plugin my_structures.py` or `PLUGIN=my_structures.py` in `&GEN`;
afterwards `&POLYA` works like any built-in block. A worked example ships as
[`example_plugin.py`](example_plugin.py).

## Running the tests

```
python -m unittest discover -s test --verbose
```
