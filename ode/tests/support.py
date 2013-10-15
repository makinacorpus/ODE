from sqlalchemy import create_engine
from ode.models import (
    DBSession,
    Base
    )
#import transaction


def initTestingDB():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    #with transaction.manager:
    #    model = Page('FrontPage', 'This is the front page')
    #    DBSession.add(model)
    return DBSession
