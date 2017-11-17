"""
tint.grid_utils
===============

Tools for pulling data from pyart grids.


"""

import datetime

import numpy as np
import pandas as pd
from scipy import ndimage


def parse_grid_datetime(grid_obj):
    """ Obtains datetime object from pyart grid_object. """
    dt_string = grid_obj.time['units'].split(' ')[-1]
    date = dt_string[:10]
    time = dt_string[11:19]
    dt = datetime.datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M:%S')
    return dt


def get_grid_size(grid_obj):
    """ Calculates grid size per dimension given a grid object. """
    z_len = grid_obj.z['data'][-1] - grid_obj.z['data'][0]
    x_len = grid_obj.x['data'][-1] - grid_obj.x['data'][0]
    y_len = grid_obj.y['data'][-1] - grid_obj.y['data'][0]
    z_size = z_len / (grid_obj.z['data'].shape[0] - 1)
    x_size = x_len / (grid_obj.x['data'].shape[0] - 1)
    y_size = y_len / (grid_obj.y['data'].shape[0] - 1)
    return np.array([z_size, y_size, x_size])


def get_radar_info(grid_obj):
    radar_lon = grid_obj.radar_longitude['data'][0]
    radar_lat = grid_obj.radar_latitude['data'][0]
    info = {'radar_lon': radar_lon,
            'radar_lat': radar_lat}
    return info


def get_grid_alt(grid_size, alt_meters=1500):
    """ Returns z-index closest to alt_meters. """
    return np.int(np.round(alt_meters/grid_size[0]))


def get_vert_projection(grid, thresh=40):
    """ Returns boolean vertical projection from grid. """
    return np.any(grid > thresh, axis=0)


def get_filtered_frame(grid, min_size, thresh):
    """ Returns a labeled frame from gridded radar data. Smaller objects
    are removed and the rest are labeled. """
    echo_height = get_vert_projection(grid, thresh)
    labeled_echo = ndimage.label(echo_height)[0]
    frame = clear_small_echoes(labeled_echo, min_size)
    return frame


def clear_small_echoes(label_image, min_size):
    """ Takes in binary image and clears objects less than min_size. """
    flat_image = pd.Series(label_image.flatten())
    flat_image = flat_image[flat_image > 0]
    size_table = flat_image.value_counts(sort=False)
    small_objects = size_table.keys()[size_table < min_size]

    for obj in small_objects:
        label_image[label_image == obj] = 0
    label_image = ndimage.label(label_image)
    return label_image[0]


def extract_grid_data(grid_obj, field, grid_size, params):
    """ Returns filtered grid frame and raw grid slice at global shift
    altitude. """
    masked = grid_obj.fields[field]['data']
    masked.data[masked.data == masked.fill_value] = 0
    gs_alt = params['GS_ALT']
    raw = masked.data[get_grid_alt(grid_size, gs_alt), :, :]
    frame = get_filtered_frame(masked.data, params['MIN_SIZE'],
                               params['FIELD_THRESH'])
    return raw, frame
