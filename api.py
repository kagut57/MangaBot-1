from aiohttp import web


async def root_handler(request):
    return web.json_response({"status": "Made With ♡ By @cant_think_1"})

async def run_web_server():
    app = web.Application()
    app.add_routes([web.get("/", root_handler)])
    runner = web.AppRunner(app)
    await runner.setup()
    PORT = 3000
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
