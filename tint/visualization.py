"""
tint.visualization
==================

Visualization tools for tracks objects.

"""

import gc
import os
import pandas as pd
import numpy as np
import shutil
import tempfile
import matplotlib as mpl
from IPython.display import display, Image
from matplotlib import pyplot as plt

import pyart

from .grid_utils import get_grid_alt


class Tracer(object):
    colors = ['m', 'r', 'lime', 'darkorange', 'k', 'b', 'darkgreen', 'yellow']
    colors.reverse()

    def __init__(self, tobj, persist):
        self.tobj = tobj
        self.persist = persist
        self.color_stack = self.colors * 10
        self.cell_color = pd.Series()
        self.history = None
        self.current = None

    def update(self, nframe):
        self.history = self.tobj.tracks.loc[:nframe]
        self.current = self.tobj.tracks.loc[nframe]
        if not self.persist:
            dead_cells = [key for key in self.cell_color.keys()
                          if key
                          not in self.current.index.get_level_values('uid')]
            self.color_stack.extend(self.cell_color[dead_cells])
            self.cell_color.drop(dead_cells, inplace=True)

    def _check_uid(self, uid):
        if uid not in self.cell_color.keys():
            try:
                self.cell_color[uid] = self.color_stack.pop()
            except IndexError:
                self.color_stack += self.colors * 5
                self.cell_color[uid] = self.color_stack.pop()

    def plot(self, ax):
        for uid, group in self.history.groupby(level='uid'):
            self._check_uid(uid)
            tracer = group[['grid_x', 'grid_y']]
            tracer = tracer*self.tobj.grid_size[[2, 1]]
            if self.persist or (uid in self.current.index):
                ax.plot(tracer.grid_x, tracer.grid_y, self.cell_color[uid])


def full_domain(tobj, grids, tmp_dir, vmin=-8, vmax=64, alt=None,
                basemap_res='l', isolated_only=False, tracers=False,
                persist=False):

    grid_size = tobj.grid_size
    if alt is None:
        alt = tobj.params['GS_ALT']
    if tracers:
        tracer = Tracer(tobj, persist)

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
        display.plot_grid(tobj.field, level=get_grid_alt(grid_size, alt),
                          vmin=vmin, vmax=vmax, mask_outside=False,
                          cmap=pyart.graph.cm.NWSRef)

        if nframe in tobj.tracks.index.levels[0]:
            frame_tracks = tobj.tracks.loc[nframe]

            if tracers:
                tracer.update(nframe)
                tracer.plot(ax)

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


def lagrangian_view(tobj, grids, tmp_dir, uid=None, vmin=-8, vmax=64, alt=None,
                    basemap_res='l', box_rad=25):

    if uid is None:
        print("Please specify 'uid' keyword argument.")
        return
    stepsize = 6
    title_font = 20
    axes_font = 18
    mpl.rcParams['xtick.labelsize'] = 16
    mpl.rcParams['ytick.labelsize'] = 16

    field = tobj.field
    grid_size = tobj.grid_size
    if alt is None:
        alt = tobj.params['GS_ALT']
    cell = tobj.tracks.xs(uid, level='uid')

    nframes = len(cell)
    print('Animating', nframes, 'frames')
    cell_frame = 0

    for nframe, grid in enumerate(grids):
        if nframe not in cell.index:
            continue

        print('Frame:', cell_frame)
        cell_frame += 1

        row = cell.loc[nframe]
        display = pyart.graph.GridMapDisplay(grid)

        # Box Size
        tx = np.int(np.round(row['grid_x']))
        ty = np.int(np.round(row['grid_y']))
        tx_met = grid.x['data'][tx]
        ty_met = grid.y['data'][ty]
        lat = row['lat']
        lon = row['lon']
        box_rad_met = box_rad * 1000
        box = np.array([-1*box_rad_met, box_rad_met])

        lvxlim = (tx * grid_size[2]) + box
        lvylim = (ty * grid_size[1]) + box
        xlim = (tx_met + box)/1000
        ylim = (ty_met + box)/1000

        fig = plt.figure(figsize=(20, 15))

        fig.suptitle('Cell ' + uid + ' Scan ' + str(nframe), fontsize=22)
        plt.axis('off')

        # Lagrangian View
        ax1 = fig.add_subplot(3, 2, (1, 3))

        display.plot_grid(field, level=get_grid_alt(grid_size, alt),
                          vmin=vmin, vmax=vmax, mask_outside=False,
                          cmap=pyart.graph.cm.NWSRef,
                          ax=ax1, colorbar_flag=False, linewidth=4)

        display.plot_crosshairs(lon=lon, lat=lat,
                                line_style='k--', linewidth=3)

        ax1.set_xlim(lvxlim[0], lvxlim[1])
        ax1.set_ylim(lvylim[0], lvylim[1])

        ax1.set_xticks(np.arange(lvxlim[0], lvxlim[1], (stepsize * 1000)))
        ax1.set_yticks(np.arange(lvylim[0], lvylim[1], (stepsize * 1000)))
        ax1.set_xticklabels(np.round(np.arange(xlim[0], xlim[1], stepsize), 1))
        ax1.set_yticklabels(np.round(np.arange(ylim[0], ylim[1], stepsize), 1))

        ax1.set_title('Top-Down View', fontsize=title_font)
        ax1.set_xlabel('East West Distance From Origin (km)' + '\n',
                       fontsize=axes_font)
        ax1.set_ylabel('North South Distance From Origin (km)',
                       fontsize=axes_font)

        # Latitude Cross Section
        ax2 = fig.add_subplot(3, 2, 2)
        display.plot_latitude_slice(field, lon=lon, lat=lat,
                                    title_flag=False,
                                    colorbar_flag=False, edges=False,
                                    vmin=vmin, vmax=vmax, mask_outside=False,
                                    cmap=pyart.graph.cm.NWSRef,
                                    ax=ax2)

        ax2.set_xlim(xlim[0], xlim[1])
        ax2.set_xticks(np.arange(xlim[0], xlim[1], stepsize))
        ax2.set_xticklabels(np.round((np.arange(xlim[0], xlim[1], stepsize)),
                                     2))

        ax2.set_title('Latitude Cross Section', fontsize=title_font)
        ax2.set_xlabel('East West Distance From Origin (km)' + '\n',
                       fontsize=axes_font)
        ax2.set_ylabel('Distance Above Origin (km)', fontsize=axes_font)
        ax2.set_aspect(aspect=1.3)

        # Longitude Cross Section
        ax3 = fig.add_subplot(3, 2, 4)
        display.plot_longitude_slice('reflectivity', lon=lon, lat=lat,
                                     title_flag=False,
                                     colorbar_flag=False, edges=False,
                                     vmin=vmin, vmax=vmax, mask_outside=False,
                                     cmap=pyart.graph.cm.NWSRef,
                                     ax=ax3)
        ax3.set_xlim(ylim[0], ylim[1])
        ax3.set_xticks(np.arange(ylim[0], ylim[1], stepsize))
        ax3.set_xticklabels(np.round(np.arange(ylim[0], ylim[1], stepsize), 2))

        ax3.set_title('Longitudinal Cross Section', fontsize=title_font)
        ax3.set_xlabel('North South Distance From Origin (km)',
                       fontsize=axes_font)
        ax3.set_ylabel('Distance Above Origin (km)', fontsize=axes_font)
        ax3.set_aspect(aspect=1.3)

        # Time Series Statistic
        max_field = cell['max']
        plttime = cell['time']

        # Plot
        ax4 = fig.add_subplot(3, 2, (5, 6))
        ax4.plot(plttime, max_field, color='b', linewidth=3)
        ax4.axvline(x=plttime[nframe], linewidth=4, color='r')
        ax4.set_title('Time Series', fontsize=title_font)
        ax4.set_xlabel('Time (UTC) \n Lagrangian Viewer Time',
                       fontsize=axes_font)
        ax4.set_ylabel('Maximum ' + field, fontsize=axes_font)

        # plot and save figure
        fig.savefig(tmp_dir + '/frame_' + str(nframe).zfill(3) + '.png')
        plt.close()
        del grid, display
        gc.collect()


def make_mp4_from_frames(tmp_dir, dest_dir, basename, fps):
    os.chdir(tmp_dir)
    os.system(" ffmpeg -framerate " + str(fps)
              + " -pattern_type glob -i '*.png'"
              + " -movflags faststart -pix_fmt yuv420p -vf"
              + " 'scale=trunc(iw/2)*2:trunc(ih/2)*2' -y "
              + basename + '.mp4')
    try:
        shutil.move(basename + '.mp4', dest_dir)
    except FileNotFoundError:
        print('Make sure ffmpeg is installed properly.')


def animate(tobj, grids, outfile_name, style='full', fps=1, keep_frames=False,
            **kwargs):
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
    alt : float
        The altitude to be plotted in meters.
    vmin, vmax : float
        Limit values for the colormap.
    arrows : bool
        If True, draws arrow showing corrected shift for each object. Only used
        in 'full' style.
    isolation : bool
        If True, only annotates uids for isolated objects. Only used in 'full'
        style.
    uid : str
        The uid of the object to be viewed from a lagrangian persepective. Only
        used when style is 'lagrangian'.
    fps : int
        Frames per second for output gif.

    """

    styles = {'full': full_domain,
              'lagrangian': lagrangian_view}
    anim_func = styles[style]

    dest_dir = os.path.dirname(outfile_name)
    basename = os.path.basename(outfile_name)
    if len(dest_dir) == 0:
        dest_dir = os.getcwd()

    if os.path.exists(basename + '.mp4'):
        print('Filename already exists.')
        return

    tmp_dir = tempfile.mkdtemp()

    try:
        anim_func(tobj, grids, tmp_dir, **kwargs)
        if len(os.listdir(tmp_dir)) == 0:
            print('Grid generator is empty.')
            return
        make_mp4_from_frames(tmp_dir, dest_dir, basename, fps)
        if keep_frames:
            frame_dir = os.path.join(dest_dir, basename + '_frames')
            shutil.copytree(tmp_dir, frame_dir)
            os.chdir(dest_dir)
    finally:
        shutil.rmtree(tmp_dir)


def embed_mp4_as_gif(filename):
    """ Makes a temporary gif version of an mp4 using ffmpeg for embedding in
    IPython. Intended for use in Jupyter notebooks. """
    if not os.path.exists(filename):
        print('file does not exist.')
        return

    dirname = os.path.dirname(filename)
    basename = os.path.basename(filename)
    newfile = tempfile.NamedTemporaryFile()
    newname = newfile.name + '.gif'
    if len(dirname) != 0:
        os.chdir(dirname)

    os.system('ffmpeg -i ' + basename + ' ' + newname)

    try:
        with open(newname, 'rb') as f:
            display(Image(f.read()), format='png')
    finally:
        os.remove(newname)
