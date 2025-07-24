from hypha_rpc import api

async def setup():
    print("hello")

api.export({
    "config": {
        "visibility": "public",
    },
    "setup": setup
})
