"""
cli.py: read the command you type and call the right function.

Loop step:      none (this is the front door)
Start reading:  main()
Called by:      main.py

Example:  py main.py validate experiments/shadow_02.json
To add a command: write a cmd_<name>(args) function, then register it in main().
"""

import argparse

from controller.experiments import load_allowlist, load_json, validate_experiment


def cmd_validate(args):
    """Check one experiment file against the allowlist."""
    experiment = load_json(args.file)
    errors = validate_experiment(experiment, load_allowlist())
    if errors:
        print(f"NOT ALLOWED: {args.file}")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"OK: {experiment['id']} is allowed")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="main.py", description="FrameForge")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help="check an experiment file")
    validate.add_argument("file", help="path to an experiment .json file")
    validate.set_defaults(func=cmd_validate)

    args = parser.parse_args(argv)
    return args.func(args)
