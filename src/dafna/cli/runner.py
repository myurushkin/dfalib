"""Executes a parsed :class:`~dafna.cli.config.Config`, driven by the registry.

Two modes:

* ``gen``  — enumerate DNA strings realising the requested structures within the
  configured strength window (and optional length), reporting the strength of
  every directly-measurable enabled structure for each string.
* ``scan`` — read an input sequence (FASTA or plain text) and report the strength
  of every enabled structure found in it (directly, or by membership for
  generator-only structures).

Everything — built-ins, ``&CUSTOM`` templates and plugin structures — flows
through :mod:`dafna.lib.registry`, so adding a structure needs no change here.
"""
from __future__ import annotations

import contextlib
import datetime
import importlib
import importlib.util
import sys
from dataclasses import dataclass
from typing import Iterator, Optional, TextIO

from dafna.cli.config import (
    Config,
    ConfigError,
    StructureConfig,
    parse_config_file,
)
from dafna.lib import registry
from dafna.lib.registry import RegistryError, StructureDef
from dafna.shared import pintersect, psum

# Safety cap: a length-constrained automaton can match astronomically many
# strings, so we stream at most this many per (structure, topology, strength).
DEFAULT_LIMIT = 1000


class RunError(Exception):
    """Raised on unrecoverable runtime problems (bad input, unwritable output)."""


@dataclass
class _Resolved:
    """An enabled structure bound to its registry definition and topologies."""

    cfg: StructureConfig
    sd: StructureDef
    topologies: list[str]

    @property
    def measurable(self) -> bool:
        return self.sd.strength_fn is not None


# --- entry points ---------------------------------------------------------

def run_config_file(
    path: str,
    *,
    mode: Optional[str] = None,
    input_path: Optional[str] = None,
    out: Optional[str] = None,
    cli_plugins: tuple[str, ...] = (),
    limit: Optional[int] = None,
) -> int:
    """Load plugins, parse ``path`` against the live registry, then run."""
    # First pass is lenient: it runs before plugins are loaded, so plugin
    # structure names aren't known yet. We use it only to discover PLUGIN=
    # entries, then load all plugins so the registry knows every structure name
    # before the authoritative strict parse below.
    try:
        prelim = parse_config_file(path, strict=False)
    except OSError as exc:
        raise RunError(f"cannot read config: {exc}") from None

    load_plugins(list(cli_plugins) + prelim.general.plugins)

    config = parse_config_file(path, known_topologies=registry.topologies_by_name(), strict=True)

    if mode is not None:
        config.general.mode = mode
    if input_path is not None:
        config.general.input_path = input_path
    if out is not None:
        config.general.out = out

    config.validate_runnable()
    return run(config, limit=limit)


def run(config: Config, limit: Optional[int] = None) -> int:
    """Run an already-parsed config (plugins must already be loaded)."""
    resolved = _resolve_structures(config)
    with _open_output(config.general.out) as handle:
        _write_header(handle, config, resolved)
        if config.general.mode == "scan":
            _run_scan(config, resolved, handle)
        else:
            _run_generation(config, resolved, handle, limit or DEFAULT_LIMIT)
    return 0


def load_plugins(names: list[str]) -> None:
    """Import plugin modules so their top-level ``register()`` calls run.

    A name ending in ``.py`` is loaded as a file path; otherwise it is imported
    as a module (``pkg.mod``).
    """
    for name in names:
        try:
            if name.endswith(".py"):
                spec = importlib.util.spec_from_file_location(_module_name_for(name), name)
                if spec is None or spec.loader is None:
                    raise RunError(f"cannot load plugin file '{name}'")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                importlib.import_module(name)
        except RunError:
            raise
        except Exception as exc:
            raise RunError(f"failed to load plugin '{name}': {exc}") from None


def _module_name_for(path: str) -> str:
    base = path.rsplit("/", 1)[-1]
    return "dafna_plugin_" + base[:-3] if base.endswith(".py") else base


# --- resolution -----------------------------------------------------------

def _resolve_structures(config: Config) -> list[_Resolved]:
    known = registry.topologies_by_name()
    resolved: list[_Resolved] = []
    for cfg in config.enabled_structures():
        if cfg.is_custom:
            sd = registry.make_template_structure(
                cfg.name,
                cfg.pattern,
                required_simple={"X": "a|c|g|t", **cfg.simple},
                description="custom",
            )
            topologies = ["canonical"]
            # Expand the template once now so a bad PATTERN fails cleanly (with a
            # config error, before any output) instead of mid-generation.
            from dafna.lib.generation.template import TemplateError, expand_template

            try:
                expand_template(cfg.pattern, cfg.str_min)
            except TemplateError as exc:
                raise ConfigError(f"&CUSTOM {cfg.name}: {exc}") from None
        else:
            try:
                sd = registry.get(cfg.name)
            except RegistryError as exc:
                raise ConfigError(str(exc)) from None
            topologies = cfg.resolved_topologies(known)
            missing = [t for t in topologies if t not in sd.generators]
            if missing:
                raise ConfigError(
                    f"&{cfg.name}: no generator for topology {missing} "
                    f"(have: {', '.join(sd.topologies)})"
                )
        resolved.append(_Resolved(cfg=cfg, sd=sd, topologies=topologies))
    return resolved


# --- output plumbing ------------------------------------------------------

@contextlib.contextmanager
def _open_output(path: Optional[str]) -> Iterator[TextIO]:
    if path is None:
        yield sys.stdout
        return
    try:
        handle = open(path, "w", encoding="utf-8")
    except OSError as exc:
        raise RunError(f"cannot open output '{path}': {exc}") from None
    try:
        yield handle
    finally:
        handle.close()


def _write_header(out: TextIO, config: Config, resolved: list[_Resolved]) -> None:
    now = datetime.datetime.now().isoformat(timespec="seconds")
    g = config.general
    # First line carries project + date for easy downstream parsing (per spec).
    print(f"# project={g.project} date={now} mode={g.mode}", file=out)
    cols = _columns(resolved, g.mode)
    print("# columns: " + "\t".join(["seq", "source", *cols]), file=out)


def _columns(resolved: list[_Resolved], mode: str) -> list[str]:
    if mode == "scan":
        return [r.cfg.name for r in resolved]  # all measurable in scan (direct or membership)
    return [r.cfg.name for r in resolved if r.measurable]


def _fmt_strength(value) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _format_row(seq: str, source: str, cells: list[str]) -> str:
    return "\t".join([seq, source, *cells])


# --- generation mode ------------------------------------------------------

def _run_generation(config: Config, resolved: list[_Resolved], out: TextIO, limit: int) -> None:
    columns = _columns(resolved, "gen")
    measurable = [r for r in resolved if r.measurable]
    seen: set[str] = set()

    for r in resolved:
        _generate_one(r, config, measurable, columns, out, limit, seen)


def _generate_one(
    r: _Resolved,
    config: Config,
    measurable: list[_Resolved],
    columns: list[str],
    out: TextIO,
    limit: int,
    seen: set[str],
) -> None:
    ctx = r.sd.make_context()
    length_automaton = None
    if config.general.length is not None:
        length_automaton = ctx.create_pattern("X" * config.general.length)

    for topology in r.topologies:
        for strength in range(r.cfg.str_min, r.cfg.str_max + 1):
            source = f"{r.cfg.name}/{topology}@{strength}"
            patterns = r.sd.generators[topology](strength, ctx)
            result = pintersect(psum(patterns))
            if length_automaton is not None:
                result = result.intersect(length_automaton).minimize()

            emitted = 0
            for seq in result.min_strings():
                if seq in seen:
                    continue
                seen.add(seq)
                cells = _gen_cells(seq, columns, measurable, r, strength)
                print(_format_row(seq, source, cells), file=out)
                emitted += 1
                if emitted >= limit:
                    print(f"# note: {source} truncated at limit={limit}", file=out)
                    break


def _gen_cells(
    seq: str, columns: list[str], measurable: list[_Resolved], origin: _Resolved, strength: int
) -> list[str]:
    by_name = {m.cfg.name: m for m in measurable}
    cells = []
    for col in columns:
        m = by_name[col]
        cells.append(_fmt_strength(m.sd.strength_fn(seq)))
    return cells


# --- scan mode ------------------------------------------------------------

def _run_scan(config: Config, resolved: list[_Resolved], out: TextIO) -> None:
    columns = _columns(resolved, "scan")
    records = _read_sequences(config.general.input_path)
    if not records:
        raise RunError(f"no sequences found in '{config.general.input_path}'")

    for name, seq in records:
        cells = []
        for r in resolved:
            if r.measurable:
                value = r.sd.strength_fn(seq)
            else:
                value = registry.membership_strength(r.sd, seq, r.cfg.str_min, r.cfg.str_max)
            cells.append(_fmt_strength(value))
        shown = seq if len(seq) <= 60 else f"{seq[:57]}..."
        print(_format_row(shown, f"{name}(len={len(seq)})", cells), file=out)


def _read_sequences(path: str) -> list[tuple[str, str]]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            text = handle.read()
    except OSError as exc:
        raise RunError(f"cannot read input '{path}': {exc}") from None

    records: list[tuple[str, str]] = []
    if ">" in text:
        name = None
        chunks: list[str] = []
        for line in text.splitlines():
            if line.startswith(">"):
                if name is not None:
                    records.append((name, _clean_sequence("".join(chunks))))
                name = line[1:].strip() or f"seq{len(records) + 1}"
                chunks = []
            else:
                chunks.append(line)
        if name is not None:
            records.append((name, _clean_sequence("".join(chunks))))
    else:
        seq = _clean_sequence(text)
        if seq:
            records.append(("seq1", seq))

    return [(n, s) for n, s in records if s]


def _clean_sequence(raw: str) -> str:
    return "".join(raw.split()).lower()
