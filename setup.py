import  sys
import  re
from    setuptools import setup

_version_re = re.compile(r"(?<=^__version__ = (\"|'))(.+)(?=\"|')")

def get_version(rel_path: str) -> str:
    """
    Searches for the ``__version__ = `` line in a source code file.

    https://packaging.python.org/en/latest/guides/single-sourcing-package-version/
    """
    with open(rel_path, 'r') as f:
        matches = map(_version_re.search, f)
        filtered = filter(lambda m: m is not None, matches)
        version = next(filtered, None)
        if version is None:
            raise RuntimeError(f'Could not find __version__ in {rel_path}')
        return version.group(0)

# Make sure we are running python3.5+
if 10 * sys.version_info[0]  + sys.version_info[1] < 35:
    sys.exit("Sorry, only Python 3.5+ is supported.")


def readme():
    with open('README.rst') as f:
        return f.read()

requirements    = []
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith('#')]


setup(
      name             =   'persair',
      version          =   get_version('persair/__main__.py'),
      description      =   'A mongodb aware purple air client',
      long_description =   readme(),
      author           =   'FNNDSC',
      author_email     =   'dev@babymri.org',
      url              =   'https://github.com/FNNDSC/persair',
      packages         =   ['persair', 'persair/config', 'persair/models'],
      install_requires =   requirements,
      entry_points={
          'console_scripts': [
              'persair = persair.__main__:main'
          ]
      },
      license          =   'MIT',
      zip_safe         =   False
)
