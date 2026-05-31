"""Parser and data model for the dafna config-file format.

The format (see ``example.conf``) is a sequence of blocks::

    &GQD T            # open the G-quadruplex block, T = enabled
    TOP=[canonical,tandem]
    STR_MIN=2
    STR_MAX=5
    &END              # close the block

    &CUSTOM myquad    # a user-defined structure (always enabled unless flagged F)
    PATTERN=X* g{s} X+ g{s} X+ g{s} X+ g{s} X*   # {s} = strength (expanded in Python)
    STR_MIN=2
    STR_MAX=4
    SIMPLE=Z:a|c      # optional extra simple pattern(s), repeatable
    &END

    &GEN              # general settings (no on/off flag)
    PROJECT=demo
    MODE=gen
    LEN=20            # or LEN=MIN
    OUT=out.log
    PLUGIN=mypkg.structs   # optional: import plugin module(s) that register() structures
    &END

Anything from a ``#`` to the end of a line is a comment.

The parser is intentionally backend-free (it never imports the compiled engine),
so ``dafna validate`` works without it. Topology validation against the live
registry is layered on top by the runner via ``known_topologies``/``strict``.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# Built-in structure block name -> known topologies. Used as the fallback when
# the caller does not pass a live registry map (e.g. the backend-free `validate`).
STRUCTURE_TOPOLOGIES: dict[str, list[str]] = {
    "GQD": ["canonical", "tandem"],
    "IMT": ["canonical"],
    "HRP": ["canonical"],
    "TRX": ["canonical"],
}

STRUCTURE_NAMES = tuple(STRUCTURE_TOPOLOGIES)
GENERAL_BLOCK = "GEN"
CUSTOM_BLOCK = "CUSTOM"
_RESERVED_BLOCKS = {GENERAL_BLOCK, CUSTOM_BLOCK, "END"}

# Per-spec defaults (example.conf): strength window [2, 5].
DEFAULT_STR_MIN = 2
DEFAULT_STR_MAX = 5

_TRUE_TOKENS = {"t", "true", "1", "yes", "y", "on"}
_FALSE_TOKENS = {"f", "false", "0", "no", "n", "off", ""}

_STRUCTURE_KEYS = {"TOP", "STR_MIN", "STR_MAX"}
_CUSTOM_KEYS = {"PATTERN", "STR_MIN", "STR_MAX", "SIMPLE"}
_GENERAL_KEYS = {"PROJECT", "MODE", "LEN", "OUT", "IN", "NCPU", "MEM", "PLUGIN"}


class ConfigError(Exception):
    """Raised on any malformed-config condition, with a human-readable message."""


@dataclass
class StructureConfig:
    name: str
    enabled: bool = False
    topologies: list[str] | None = None  # None == "all"
    str_min: int = DEFAULT_STR_MIN
    str_max: int = DEFAULT_STR_MAX
    is_custom: bool = False
    pattern: str | None = None  # custom structures only
    simple: dict[str, str] = field(default_factory=dict)  # extra simple patterns

    def resolved_topologies(self, known: dict[str, list[str]] | None = None) -> list[str]:
        if self.is_custom:
            return ["canonical"]
        if self.topologies is not None:
            return list(self.topologies)
        key = self.name.upper()
        if known and key in known:
            return list(known[key])
        return list(STRUCTURE_TOPOLOGIES.get(key, ["canonical"]))


@dataclass
class GeneralConfig:
    project: str = "dafna"
    mode: str = "gen"  # "gen" | "scan"
    length: int | None = None  # None == MIN
    out: str | None = None  # None == stdout
    input_path: str | None = None
    ncpu: int = 1
    mem: str | None = None
    plugins: list[str] = field(default_factory=list)


@dataclass
class Config:
    structures: dict[str, StructureConfig] = field(default_factory=dict)
    general: GeneralConfig = field(default_factory=GeneralConfig)

    def enabled_structures(self) -> list[StructureConfig]:
        return [s for s in self.structures.values() if s.enabled]

    def validate_runnable(self) -> None:
        """Check invariants that only matter when actually running a search."""
        if not self.enabled_structures():
            raise ConfigError("no structures enabled — nothing to search for")
        if self.general.mode == "scan" and not self.general.input_path:
            raise ConfigError(
                "mode=scan requires an input sequence (set IN= in &GEN or pass --in)"
            )


def parse_config_file(
    path: str,
    known_topologies: dict[str, list[str]] | None = None,
    strict: bool = True,
) -> Config:
    with open(path, "r", encoding="utf-8") as handle:
        return parse_config(handle.read(), known_topologies=known_topologies, strict=strict)


def parse_config(
    text: str,
    known_topologies: dict[str, list[str]] | None = None,
    strict: bool = True,
) -> Config:
    """Parse config text.

    ``known_topologies`` maps STRUCTURE NAME (upper-case) -> topology list; when
    given, structure-block names/topologies are validated against it (otherwise
    the built-in :data:`STRUCTURE_TOPOLOGIES` map is used). ``strict`` (default)
    makes an unknown structure-block name an error; pass ``strict=False`` to
    accept unknown names as external/plugin structures (e.g. a lenient pre-parse
    that runs before plugins are loaded).
    """
    ctx = _ParseState(config=Config(), known=known_topologies, strict=strict)

    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = _strip_comment(raw).strip()
        if not line:
            continue
        if line.startswith("&"):
            _handle_block_line(line, lineno, ctx)
        else:
            _handle_assignment(line, lineno, ctx)

    if ctx.current_kind is not None:
        raise ConfigError(
            f"unexpected end of file: '&{ctx.current_kind}' block not closed with &END"
        )

    # Custom structures must declare a PATTERN.
    for struct in ctx.config.structures.values():
        if struct.is_custom and not struct.pattern:
            raise ConfigError(f"&CUSTOM {struct.name}: missing PATTERN")

    return ctx.config


@dataclass
class _ParseState:
    config: Config
    known: dict[str, list[str]] | None
    strict: bool
    current: StructureConfig | None = None
    current_kind: str | None = None  # block name, GENERAL_BLOCK, or CUSTOM_BLOCK
    seen_blocks: set[str] = field(default_factory=set)


def _strip_comment(line: str) -> str:
    idx = line.find("#")
    return line if idx < 0 else line[:idx]


def _handle_block_line(line: str, lineno: int, ctx: _ParseState) -> None:
    tokens = line[1:].split()
    if not tokens:
        raise ConfigError(f"line {lineno}: bare '&' with no block name")
    name = tokens[0].upper()

    if name == "END":
        if ctx.current_kind is None:
            raise ConfigError(f"line {lineno}: &END without an open block")
        if len(tokens) > 1:
            raise ConfigError(f"line {lineno}: &END takes no arguments")
        ctx.current = None
        ctx.current_kind = None
        return

    if ctx.current_kind is not None:
        raise ConfigError(
            f"line {lineno}: &{name} opened while '&{ctx.current_kind}' is still open "
            "(missing &END?)"
        )

    if name == GENERAL_BLOCK:
        if len(tokens) > 1:
            raise ConfigError(f"line {lineno}: &GEN takes no on/off flag")
        if GENERAL_BLOCK in ctx.seen_blocks:
            raise ConfigError(f"line {lineno}: duplicate &GEN block")
        ctx.seen_blocks.add(GENERAL_BLOCK)
        ctx.current_kind = GENERAL_BLOCK
        return

    if name == CUSTOM_BLOCK:
        _open_custom_block(tokens, lineno, ctx)
        return

    _open_structure_block(name, tokens, lineno, ctx)


def _open_custom_block(tokens: list[str], lineno: int, ctx: _ParseState) -> None:
    if len(tokens) < 2:
        raise ConfigError(f"line {lineno}: &CUSTOM requires a name (e.g. '&CUSTOM myquad')")
    struct_name = tokens[1]
    key = struct_name.upper()
    if key in _RESERVED_BLOCKS or key in STRUCTURE_NAMES:
        raise ConfigError(f"line {lineno}: &CUSTOM name '{struct_name}' is reserved")
    if key in ctx.config.structures:
        raise ConfigError(f"line {lineno}: duplicate structure '{struct_name}'")
    enabled = _parse_flag(tokens[2], lineno) if len(tokens) > 2 else True
    if len(tokens) > 3:
        raise ConfigError(f"line {lineno}: &CUSTOM takes a name and at most one flag")
    struct = StructureConfig(name=struct_name, enabled=enabled, is_custom=True)
    ctx.config.structures[key] = struct
    ctx.current = struct
    ctx.current_kind = CUSTOM_BLOCK


def _open_structure_block(name: str, tokens: list[str], lineno: int, ctx: _ParseState) -> None:
    valid_names = set(ctx.known) if ctx.known is not None else set(STRUCTURE_NAMES)
    if name not in valid_names:
        if ctx.strict:
            ordered = ", ".join(sorted(valid_names) + [GENERAL_BLOCK, CUSTOM_BLOCK])
            raise ConfigError(f"line {lineno}: unknown block '&{name}' (expected one of: {ordered})")
        # Lenient (e.g. backend-free `validate`): accept as an external/plugin
        # structure whose topologies are checked later by the runner.

    if name in ctx.seen_blocks:
        raise ConfigError(f"line {lineno}: duplicate &{name} block")
    ctx.seen_blocks.add(name)

    enabled = _parse_flag(tokens[1], lineno) if len(tokens) > 1 else False
    if len(tokens) > 2:
        raise ConfigError(f"line {lineno}: &{name} takes at most one flag, got {tokens[1:]}")
    struct = StructureConfig(name=name, enabled=enabled)
    ctx.config.structures[name] = struct
    ctx.current = struct
    ctx.current_kind = name


def _handle_assignment(line: str, lineno: int, ctx: _ParseState) -> None:
    if ctx.current_kind is None:
        raise ConfigError(f"line {lineno}: '{line}' is outside any &BLOCK")
    if "=" not in line:
        raise ConfigError(f"line {lineno}: expected KEY=VALUE, got '{line}'")
    key, _, value = line.partition("=")
    key = key.strip().upper()
    value = value.strip()

    if ctx.current_kind == GENERAL_BLOCK:
        _apply_general_key(key, value, lineno, ctx.config.general)
    elif ctx.current_kind == CUSTOM_BLOCK:
        assert ctx.current is not None
        _apply_custom_key(key, value, lineno, ctx.current)
    else:
        assert ctx.current is not None
        _apply_structure_key(key, value, lineno, ctx.current, ctx.known)


def _apply_structure_key(
    key: str, value: str, lineno: int, struct: StructureConfig, known: dict[str, list[str]] | None
) -> None:
    if key not in _STRUCTURE_KEYS:
        valid = ", ".join(sorted(_STRUCTURE_KEYS))
        raise ConfigError(f"line {lineno}: unknown key '{key}' in &{struct.name} (expected: {valid})")

    if key == "TOP":
        struct.topologies = _parse_topologies(value, lineno, struct.name, known)
    elif key == "STR_MIN":
        struct.str_min = _parse_positive_int(value, lineno, "STR_MIN")
    elif key == "STR_MAX":
        struct.str_max = _parse_positive_int(value, lineno, "STR_MAX")

    if struct.str_min > struct.str_max:
        raise ConfigError(
            f"line {lineno}: STR_MIN ({struct.str_min}) > STR_MAX ({struct.str_max}) in &{struct.name}"
        )


def _apply_custom_key(key: str, value: str, lineno: int, struct: StructureConfig) -> None:
    if key not in _CUSTOM_KEYS:
        valid = ", ".join(sorted(_CUSTOM_KEYS))
        raise ConfigError(
            f"line {lineno}: unknown key '{key}' in &CUSTOM {struct.name} (expected: {valid})"
        )

    if key == "PATTERN":
        if not value:
            raise ConfigError(f"line {lineno}: PATTERN is empty in &CUSTOM {struct.name}")
        struct.pattern = value
    elif key == "STR_MIN":
        struct.str_min = _parse_positive_int(value, lineno, "STR_MIN")
    elif key == "STR_MAX":
        struct.str_max = _parse_positive_int(value, lineno, "STR_MAX")
    elif key == "SIMPLE":
        simple_name, regex = _parse_simple(value, lineno, struct.name)
        struct.simple[simple_name] = regex

    if struct.str_min > struct.str_max:
        raise ConfigError(
            f"line {lineno}: STR_MIN ({struct.str_min}) > STR_MAX ({struct.str_max}) in &CUSTOM {struct.name}"
        )


def _apply_general_key(key: str, value: str, lineno: int, general: GeneralConfig) -> None:
    if key not in _GENERAL_KEYS:
        valid = ", ".join(sorted(_GENERAL_KEYS))
        raise ConfigError(f"line {lineno}: unknown key '{key}' in &GEN (expected: {valid})")

    if key == "PROJECT":
        general.project = value
    elif key == "MODE":
        general.mode = _parse_mode(value, lineno)
    elif key == "LEN":
        general.length = _parse_length(value, lineno)
    elif key == "OUT":
        general.out = value or None
    elif key == "IN":
        general.input_path = value or None
    elif key == "NCPU":
        general.ncpu = _parse_positive_int(value, lineno, "NCPU")
    elif key == "MEM":
        general.mem = value or None
    elif key == "PLUGIN":
        general.plugins.extend(item.strip() for item in value.split(",") if item.strip())


def _parse_flag(token: str, lineno: int) -> bool:
    low = token.strip().lower()
    if low in _TRUE_TOKENS:
        return True
    if low in _FALSE_TOKENS:
        return False
    raise ConfigError(f"line {lineno}: cannot parse on/off flag '{token}' (use T or F)")


def _parse_mode(value: str, lineno: int) -> str:
    low = value.strip().lower()
    if low in {"gen", "generate", "generation"}:
        return "gen"
    if low in {"scan", "search"}:
        return "scan"
    raise ConfigError(f"line {lineno}: MODE must be 'gen' or 'scan', got '{value}'")


def _parse_length(value: str, lineno: int):
    if value.strip().lower() == "min":
        return None
    return _parse_positive_int(value, lineno, "LEN")


def _parse_positive_int(value: str, lineno: int, key: str) -> int:
    try:
        result = int(value.strip())
    except ValueError:
        raise ConfigError(f"line {lineno}: {key} must be an integer, got '{value}'") from None
    if result < 1:
        raise ConfigError(f"line {lineno}: {key} must be >= 1, got {result}")
    return result


def _parse_simple(value: str, lineno: int, struct_name: str) -> tuple[str, str]:
    # Accept "NAME:regex" or "NAME=regex".
    sep_idx = min((value.find(c) for c in ":=" if c in value), default=-1)
    if sep_idx <= 0:
        raise ConfigError(
            f"line {lineno}: SIMPLE in &CUSTOM {struct_name} must be 'NAME:regex' (got '{value}')"
        )
    simple_name = value[:sep_idx].strip()
    regex = value[sep_idx + 1:].strip()
    if not simple_name or not regex:
        raise ConfigError(f"line {lineno}: SIMPLE in &CUSTOM {struct_name} has empty name or regex")
    return simple_name, regex


def _parse_topologies(
    value: str, lineno: int, struct_name: str, known: dict[str, list[str]] | None
) -> list[str] | None:
    inner = value.strip()
    if inner.lower() == "all":
        return None
    inner = inner.strip("[]")
    items = [item.strip().lower() for item in inner.split(",")]
    items = [item for item in items if item]
    if not items:
        raise ConfigError(f"line {lineno}: TOP is empty in &{struct_name} (use 'all' or a list)")

    # Validate against known topologies when available (registry or builtin map).
    key = struct_name.upper()
    valid: list[str] | None = None
    if known is not None and key in known:
        valid = known[key]
    elif key in STRUCTURE_TOPOLOGIES:
        valid = STRUCTURE_TOPOLOGIES[key]
    if valid is not None:
        unknown = [item for item in items if item not in valid]
        if unknown:
            raise ConfigError(
                f"line {lineno}: unknown topology {unknown} for &{struct_name} "
                f"(valid: {', '.join(valid)})"
            )

    seen: set[str] = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
