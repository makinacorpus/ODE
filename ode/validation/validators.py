from ode.validation.schema import QueryStringSchema
from colander import Invalid


def has_provider_id(request):
    provider_id = request.headers.get('X-ODE-Provider-Id', '').strip()
    if provider_id:
        request.validated['provider_id'] = provider_id
    else:
        request.errors.add('body', 'provider_id',
                           'This request requires an X-ODE-Provider-Id header')
        request.errors.status = 403


def validate_querystring(request):
    schema = QueryStringSchema()
    try:
        request.validated.update(schema.deserialize(request.GET))
    except Invalid, e:
        errors = e.asdict(translate=request.localizer.translate)
        for field, message in errors.items():
            request.errors.add('body', field, message)
        request.errors.status = 400
