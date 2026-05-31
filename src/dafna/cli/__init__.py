"""Command-line interface for dafna.

The console-script ``dafna`` (declared under ``[project.scripts]`` in
``pyproject.toml``) and ``python -m dafna`` both dispatch to :func:`main`.

Sub-commands::

    dafna run CONFIG [--mode gen|scan] [--in PATH] [--out PATH]
                     [--plugin MODULE_OR_FILE]... [--limit N]
    dafna validate CONFIG

``validate`` only parses and checks the config (no compiled backend, no plugin
imports), so it works in a minimal environment. ``run`` loads any plugins (from
``--plugin`` and ``PLUGIN=`` in the config), then validates against the live
structure registry.
"""
import argparse
import sys

from dafna.cli.config import ConfigError, parse_config_file

__all__ = ["main"]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dafna",
        description="Search/generate DNA secondary structures via finite automata.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run a search described by a config file.")
    run.add_argument("config", help="Path to the config file (see example.conf).")
    run.add_argument("--mode", choices=["gen", "scan"], help="Override the MODE field.")
    run.add_argument("--in", dest="input_path", help="Override IN (input sequence for scan).")
    run.add_argument("--out", dest="out", help="Override OUT (defaults to stdout).")
    run.add_argument(
        "--plugin",
        action="append",
        default=[],
        metavar="MODULE_OR_FILE",
        help="Import a plugin (module name or .py file) that registers structures. Repeatable.",
    )
    run.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max strings emitted per (structure, topology, strength) in gen mode.",
    )

    validate = sub.add_parser("validate", help="Parse and validate a config file.")
    validate.add_argument("config", help="Path to the config file to validate.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        return _cmd_validate(args)
    if args.command == "run":
        return _cmd_run(args)
    parser.error("unknown command")  # pragma: no cover - argparse guards this
    return 2


def _cmd_validate(args) -> int:
    # Lenient pre-parse: catches syntax/structure errors and discovers PLUGIN=
    # entries. Stays backend-free, so validation works even without the engine.
    try:
        config = parse_config_file(args.config, strict=False)
    except ConfigError as exc:
        print(f"dafna: config error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"dafna: cannot read config: {exc}", file=sys.stderr)
        return 2

    # Best-effort strict pass: if the registry and any declared plugins import
    # cleanly, re-validate structure names/topologies against the live registry
    # (catches typo'd blocks and unknown plugin structures). If the engine or a
    # plugin is unavailable, fall back to the lenient result above.
    try:
        from dafna.cli import runner
        from dafna.lib import registry

        runner.load_plugins(config.general.plugins)
        config = parse_config_file(
            args.config, known_topologies=registry.topologies_by_name(), strict=True
        )
    except ConfigError as exc:
        print(f"dafna: config error: {exc}", file=sys.stderr)
        return 2
    except Exception:
        pass  # engine/plugin unavailable — keep the lenient validation result

    print(f"dafna: {args.config} is valid.")
    _print_config_summary(config)
    return 0


def _cmd_run(args) -> int:
    # Imported lazily: the runner pulls in the compiled backend, which the
    # lightweight `validate` path must not require.
    from dafna.cli import runner

    try:
        return runner.run_config_file(
            args.config,
            mode=args.mode,
            input_path=args.input_path,
            out=args.out,
            cli_plugins=tuple(args.plugin),
            limit=args.limit,
        )
    except ConfigError as exc:
        print(f"dafna: config error: {exc}", file=sys.stderr)
        return 2
    except runner.RunError as exc:
        print(f"dafna: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"dafna: {exc}", file=sys.stderr)
        return 2


def _print_config_summary(config) -> None:
    g = config.general
    print(f"  project: {g.project}")
    print(f"  mode:    {g.mode}")
    print(f"  length:  {'MIN' if g.length is None else g.length}")
    print(f"  out:     {g.out or '<stdout>'}")
    if g.mode == "scan":
        print(f"  in:      {g.input_path}")
    if g.plugins:
        print(f"  plugins: {', '.join(g.plugins)}")
    enabled = [s for s in config.structures.values() if s.enabled]
    if not enabled:
        print("  structures: <none enabled>")
        return
    print("  structures:")
    for s in enabled:
        if s.is_custom:
            print(f"    {s.name} (custom): strength=[{s.str_min},{s.str_max}] pattern={s.pattern!r}")
        else:
            tops = "all" if s.topologies is None else ",".join(s.topologies)
            print(f"    {s.name}: top={tops} strength=[{s.str_min},{s.str_max}]")
