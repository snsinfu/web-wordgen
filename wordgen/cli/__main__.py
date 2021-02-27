import argparse
import signal
import sys

from . import Train, Generate


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    args = parse_args()
    mode = args.pop("mode")

    if mode == "train":
        command = Train(source=sys.stdin, **args)
    if mode == "generate":
        command = Generate(**args)

    command.run()


def parse_args():
    parser = argparse.ArgumentParser(prog="wordgen")
    sub = parser.add_subparsers(dest="mode", required=True)

    train_parser = sub.add_parser("train")
    train_parser.add_argument("--group", type=str)
    train_parser.add_argument("--token-size", type=int)
    train_parser.add_argument("output", type=str)

    generate_parser = sub.add_parser("generate")
    generate_parser.add_argument("--group", type=str)
    generate_parser.add_argument("--count", type=int)
    generate_parser.add_argument("input", type=str)

    return vars(parser.parse_args())


if __name__ == "__main__":
    main()
