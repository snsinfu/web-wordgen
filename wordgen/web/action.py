from aiohttp import web
import multidict

from .backend import BackendUsageError


ASSET_CACHE_AGE = 60 * 60 * 24

routes = web.RouteTableDef()
static_headers = multidict.CIMultiDict()
static_headers["Cache-Control"] = f"public, max-age={ASSET_CACHE_AGE}"


@routes.get("/")
async def index(request):
    return web.FileResponse("index.html", headers=static_headers)


@routes.get("/index.js")
async def index_js(request):
    return web.FileResponse("index.js", headers=static_headers)


@routes.get("/index.css")
async def index_css(request):
    return web.FileResponse("index.css", headers=static_headers)


@routes.post("/requests")
async def requests(request):
    try:
        post_data = await request.post()
        model_name = post_data["model"]
        prefix = post_data["prefix"]
        count = int(post_data["count"])
    except:
        return web.json_response({"error": "bad post data"}, status=400)

    if prefix == "":
        prefix = None

    try:
        backend = request.app["backend"]
        words = []
        for word in set(backend.generate(model_name, prefix, count)):
            words.append({"w": word, "p": 1})
    except BackendUsageError as e:
        return web.json_response({"error": str(e)}, status=400)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

    return web.json_response({"words": words, "error": None})
