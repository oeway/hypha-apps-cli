from hypha_rpc import api

from some_module.test_import import this_function_does_nothing

async def setup():
    print("hello")
    this_function_does_nothing()


api.export({
    "config": {
        "visibility": "public",
    },
    "setup": setup
})
