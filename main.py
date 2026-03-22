import argparse
import sys
from lib.src.network_lib.utils.config import AppConfig
from lib.src.network_lib.utils.simulation import run_single, run_experiment


def _build_parser():
    parser = argparse.ArgumentParser(prog="main.py")
    parser.add_argument("-c", "--config", required=True, )
    parser.add_argument("-o", "--output", required=True)
    # TODO think about the two parameters requirement, maybe it's a not necessary restriction
    parser.add_argument("-e", "--experiment", action="store_true", default=False)
    return parser



if __name__ == "__main__":
    args = _build_parser().parse_args()
    try:
        config = AppConfig.load(args.config)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error {exc}", file=sys.stderr)
        sys.exit(1)

    output_file = args.output
    config_file = args.config
    if args.experiment:
        run_experiment(config, output_file)
    else:
        run_single(config, output_file)

