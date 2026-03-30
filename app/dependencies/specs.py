from fastapi.routing import APIRoute

def generate_unique_endpoint_id(route: APIRoute):
    return route.name