"""
tint.visualization
==================

Visualization tools for tracks objects.

"""

import gc
import os
import numpy as np
import shutil
from matplotlib import animation
from matplotlib import pyplot as plt

import pyart

from .grid_utils import get_grid_alt


def animate(tobj, grids, outfile_name, alt=2000, isolated_only=False, fps=1):
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
    tmp_dir = outfile_name + '_tmp_frames'
    print('tmp_dir:', tmp_dir)
    os.mkdir(tmp_dir)

    grid_size = tobj.grid_size
    radar_lon = tobj.radar_info['radar_lon']
    radar_lat = tobj.radar_info['radar_lat']
    lon = np.arange(radar_lon-5, radar_lon+5, 0.5)
    lat = np.arange(radar_lat-5, radar_lat+5, 0.5)

    nframes = tobj.tracks.index.levels[0].max() + 1
    print('Animating', nframes, 'frames')

    for nframe, grid in enumerate(grids):
        plt.clf()
        fig_grid = plt.figure(figsize=(10, 8))
        print('Frame:', nframe)
        display = pyart.graph.GridMapDisplay(grid)
        ax = fig_grid.add_subplot(111)
        display.plot_basemap(resolution='h', lat_lines=lat, lon_lines=lon)
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
        del grid, display, ax
        gc.collect()
    plt.close()

    os.chdir(tmp_dir)
    os.system(" ffmpeg -framerate " + str(fps)
              + " -pattern_type glob -i '*.png'"
              + " -movflags faststart -pix_fmt yuv420p -vf"
              + " 'scale=trunc(iw/2)*2:trunc(ih/2)*2' -y "
              + outfile_name + ".mp4")
    shutil.move(outfile_name + '.mp4', '../')
    os.chdir('..')
    shutil.rmtree(tmp_dir)
