import optparse
import sys
import textwrap

import transaction
from pyramid.paster import bootstrap
from ode.harvesting import harvest
import pyramid.paster


def main():
    description = """\
    Harvest event from sources.
    Example: 'harvest deployment.ini'
    """
    usage = "usage: %prog config_uri"
    parser = optparse.OptionParser(
        usage=usage,
        description=textwrap.dedent(description)
        )

    options, args = parser.parse_args(sys.argv[1:])
    if not len(args) >= 1:
        print('You must provide one argument')
        return 2
    config_uri = args[0]
    pyramid.paster.setup_logging(config_uri)
    env = bootstrap(config_uri)
    settings, closer = env['registry'].settings, env['closer']
    try:
        with transaction.manager:
            harvest()
    finally:
        closer()
