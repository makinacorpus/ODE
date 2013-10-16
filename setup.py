import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()

requires = [
    'fanstatic==0.16',
    'pyramid_formalchemy',
    'pyramid_fanstatic',
    'cornice',
    'fa.jquery',
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'colander',
]

setup(name='ode',
      version='0.0',
      description='ode',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Makina Corpus',
      author_email='alex.marandon@makina-corpus.com',
      url='',
      keywords='web wsgi bfg pylons pyramid opendata calendar rest',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='ode',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = ode:main
      [console_scripts]
      initialize_ode_db = ode.scripts.initializedb:main
      """,
      )
