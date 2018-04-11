""" Setup for tests subpackages. """

from numpy.distutils.core import setup
from numpy.distutils.misc_util import Configuration

def configuration(parent_package='', top_path=None):
    """ Configuration of tests subpackages. """
    config = Configuration('tests', parent_package, top_path)
    config.add_data_dir('data')
    return config

if __name__ == '__main__':
    setup(**configuration(top_path='').todict())
