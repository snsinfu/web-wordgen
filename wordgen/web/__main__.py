import argparse

from aiohttp import web

from .action import routes
from .backend import Backend


BACKEND_CONFIG = "config.json"


def main():
    args = parse_args()

    app = web.Application()
    app.add_routes(routes)
    app["backend"] = Backend(args["backend_config"])
    web.run_app(app, host=args["host"], port=args["port"])


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("backend_config", type=str)
    return vars(parser.parse_args())


if __name__ == "__main__":
    main()
