"""
=============================
Track a series of pyart grids
=============================

"""

# Author: Mark Picel (mhpicel@gmail.com)
# License: BSD 3 clause

from glob import glob
import os
import pyart
from tint.tracks import Cell_tracks
from tint.visualization import animate

# Obtain sorted list of pyart grid files
data_dir = ''  # put the path to your grid files here
grid_files = glob(os.path.join(data_dir, '*.nc'))
grid_files = [os.path.join(data_dir, file_name) for file_name in grid_files]
grid_files.sort()

# Create generator of pyart grid objects
grid_gen = (pyart.io.read_grid(file_name) for file_name in grid_files)

# Instantiate tracks object and view parameter defaults
tracks_obj = Cell_tracks()
print(tracks_obj.params)

# Adjust size parameter
tracks_obj.params['MIN_SIZE'] = 4

# Get tracks from grid generator
tracks_obj.get_tracks(grid_gen)

# Inspect tracks
print(tracks_obj.tracks)

# Create generator of the same grids for animator
anim_gen = (pyart.io.read_grid(file_name) for file_name in grid_files)

# Create animation in current working directory
animate(tracks_obj, anim_gen, 'tint_test_animation', alt=1500)
