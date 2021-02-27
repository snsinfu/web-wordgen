import argparse
import os
import signal
import sys

from . import Main


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    Main(source=sys.stdin, **parse_args()).run()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ngram", type=int)
    parser.add_argument("--output-group", type=str)
    parser.add_argument("output", type=str)
    return vars(parser.parse_args())


if __name__ == "__main__":
    main()
