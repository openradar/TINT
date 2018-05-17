"""Setup for tint subpackages."""

from numpy.distutils.core import setup
from numpy.distutils.misc_util import Configuration

def configuration(parent_package='', top_path=None):
    """ Configuration of TINT subpackages. """
    config = Configuration('tint', parent_package, top_path)
    config.add_subpackage('testing')
    return config

if __name__ == '__main__':
    setup(**configuration(top_path='').todict())
