def absolute_url(request, route_name, **kwargs):
    if 'X-ODE-API-Mount-Point' in request.headers:
        mount_point = request.headers['X-ODE-API-Mount-Point']
        path = request.route_path(route_name, **kwargs)
        return mount_point + path
    else:
        return request.route_url(route_name, **kwargs)
