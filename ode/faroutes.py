import logging

log = logging.getLogger(__name__)


def includeme(config):
    config.registry.settings.get('ode.fa_settings}}', {})

    # Example to add a specific model
    #settings = config.registry.settings.get('ode.fa_settings}}', {})
    #config.formalchemy_model("/my_model", package='ode',
    #                         model='ode.models.MyModel')
    #                         **settings)

    log.info('ode.faroutes loaded')
