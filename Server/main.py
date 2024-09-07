import asyncio
import aiohttp
from aiohttp import web
from erorr.erorr import ServerSide
from src.server import protection, RequestHandler
from aiohttp_middlewares import https_middleware

# define class
ProtectionServer = protection()
ReqeustHandel = RequestHandler()

app = web.Application(middlewares=[ProtectionServer.RateLimiter, https_middleware()])
app.router.add_get("/api/v1/get", ReqeustHandel.Recive)
app.router.add_post("/api/v1/post", ReqeustHandel.Recive)
app.router.add_delete("/api/v1/delete", ReqeustHandel.Recive)

if __name__ == "__main__":
    try:
        web.run_app(app, host="0.0.0.0", port=8080)
    except Exception:
        raise ServerSide("Server Crash Before Event Started")
