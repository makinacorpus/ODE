from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
tranlation_factory = TranslationStringFactory('ode')

from pyramid.events import NewRequest
from pyramid.events import subscriber


@subscriber(NewRequest)
def setup_i18n(event):
    request = event.request
    if request.accept_language:
        accepted = event.request.accept_language
        event.request._LOCALE_ = accepted.best_match(('en', 'fr'), 'en')
    localizer = get_localizer(request)

    def auto_translate(string, *args, **kwargs):
        return localizer.translate(tranlation_factory(string, *args, **kwargs))

    request.localizer = localizer
    request.translate = auto_translate
