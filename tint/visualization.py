"""
tint.visualization
==================

Visualization tools for tracks objects.

"""

import gc
import os
import numpy as np
import shutil
import tempfile
from matplotlib import pyplot as plt

import pyart

from .grid_utils import get_grid_alt


def make_animation(tobj, grids, basename, tmp_dir, dest_dir, alt=2000,
                   isolated_only=False, fps=1, basemap_res='l'):

    grid_size = tobj.grid_size
    radar_lon = tobj.radar_info['radar_lon']
    radar_lat = tobj.radar_info['radar_lat']
    lon = np.arange(radar_lon-5, radar_lon+5, 0.5)
    lat = np.arange(radar_lat-5, radar_lat+5, 0.5)

    nframes = tobj.tracks.index.levels[0].max() + 1
    print('Animating', nframes, 'frames')

    for nframe, grid in enumerate(grids):
        fig_grid = plt.figure(figsize=(10, 8))
        print('Frame:', nframe)
        display = pyart.graph.GridMapDisplay(grid)
        ax = fig_grid.add_subplot(111)
        display.plot_basemap(resolution=basemap_res,
                             lat_lines=lat, lon_lines=lon)
        display.plot_crosshairs(lon=radar_lon, lat=radar_lat)
        display.plot_grid(tobj.field, level=2*get_grid_alt(grid_size, alt),
                          vmin=-8, vmax=64, mask_outside=False,
                          cmap=pyart.graph.cm.NWSRef)

        if nframe in tobj.tracks.index.levels[0]:
            frame_tracks = tobj.tracks.loc[nframe]
            for ind, uid in enumerate(frame_tracks.index):
                if isolated_only and not frame_tracks['isolated'].iloc[ind]:
                    continue
                x = frame_tracks['grid_x'].iloc[ind]*grid_size[2]
                y = frame_tracks['grid_y'].iloc[ind]*grid_size[1]
                ax.annotate(uid, (x, y), fontsize=20)

        plt.savefig(tmp_dir + '/frame_' + str(nframe).zfill(3) + '.png')
        plt.close()
        del grid, display, ax
        gc.collect()

    os.chdir(tmp_dir)
    print(os.getcwd())
    print(os.listdir())
    os.system(" ffmpeg -framerate " + str(fps)
              + " -pattern_type glob -i '*.png'"
              + " -movflags faststart -pix_fmt yuv420p -vf"
              + " 'scale=trunc(iw/2)*2:trunc(ih/2)*2' -y "
              + basename + '.mp4')

    print(os.getcwd())
    print(os.listdir())
    try:
        shutil.move(basename + '.mp4', dest_dir)
    except FileNotFoundError:
        print('Make sure ffmpeg is installed properly.')


def animate(tobj, grids, outfile_name, alt=2000,
            isolated_only=False, fps=1, basemap_res='l'):
    """
    Creates gif animation of tracked cells.

    Parameters
    ----------
    tobj : Cell_tracks
        The Cell_tracks object to be visualized.
    grids : iterable
        An iterable containing all of the grids used to generate tobj
    outfile_name : str
        The name of the output file to be produced.
    arrows : bool
        If True, draws arrow showing corrected shift for each object.
    isolation : bool
        If True, only annotates uids for isolated objects.
    fps : int
        Frames per second for output gif.

    """
    dest_dir = os.path.dirname(outfile_name)
    basename = os.path.basename(outfile_name)
    if len(dest_dir) == 0:
        dest_dir = os.getcwd()

    if os.path.exists(basename + '.mp4'):
        print('Filename already exists.')
        return

    tmp_dir = tempfile.mkdtemp()

    try:
        make_animation(tobj, grids, basename, tmp_dir, dest_dir,
                       alt, isolated_only, fps, basemap_res)
    finally:
        shutil.rmtree(tmp_dir)
