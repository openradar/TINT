"""
tint.tracks
===========

Cell_tracks class.

"""

import copy
import datetime

import numpy as np
import pandas as pd

from .grid_utils import get_grid_size, get_radar_info, extract_grid_data
from .helpers import Record, Counter
from .phase_correlation import get_global_shift
from .matching import get_pairs
from .objects import init_current_objects, update_current_objects
from .objects import get_object_prop, write_tracks

# Tracking Parameter Defaults
FIELD_THRESH = 32
ISO_THRESH = 8
ISO_SMOOTH = 3
MIN_SIZE = 32
NEAR_THRESH = 4
SEARCH_MARGIN = 8
FLOW_MARGIN = 20
MAX_DISPARITY = 999
MAX_FLOW_MAG = 50
MAX_SHIFT_DISP = 15
GS_ALT = 1500

"""
Tracking Parameter Guide
------------------------

FIELD_THRESH : units of 'field' attribute
    The threshold used for object detection. Detected objects are connnected
    pixels above this threshold.
ISO_THRESH : units of 'field' attribute
    Used in isolated cell classification. Isolated cells must not be connected
    to any other cell by contiguous pixels above this threshold.
ISO_SMOOTH : pixels
    Gaussian smoothing parameter in peak detection preprocessing. See
    single_max in tint.objects.
MIN_SIZE : pixels
    The minimum size threshold in pixels for an object to be detected.
SEARCH_MARGIN : pixels
    The radius of the search box around the predicted object center.
FLOW_MARGIN : pixels
    The margin size around the object extent on which to perform phase
    correlation.
MAX_DISPARITY : float
    Maximum allowable disparity value. Larger disparity values are sent to
    LARGE_NUM.
MAX_FLOW_MAG : pixels
    Maximum allowable global shift magnitude. See get_global_shift in
    tint.phase_correlation.
MAX_SHIFT_DISP : float
    Maximum magnitude of difference in meters per second for two shifts to be
    considered in agreement. See correct_shift in tint.matching.
GS_ALT : meters
    Altitude in meters at which to perform phase correlation for global shift
    calculation. See correct_shift in tint.matching.
"""


class Cell_tracks(object):
    """
    This is the main class in the module. It allows tracks
    objects to be built using lists of pyart grid objects.

    Attributes
    ----------
    params : dict
        Parameters for the tracking algorithm.
    field : str
        String specifying pyart grid field to be used for tracking. Default is
        'reflectivity'.
    grid_size : array
        Array containing z, y, and x mesh size in meters respectively.
    last_grid : Grid
        Contains the most recent grid object tracked. This is used for dynamic
        updates.
    counter : Counter
        See Counter class.
    record : Record
        See Record class.
    current_objects : dict
        Contains information about objects in the current scan.
    tracks : DataFrame

    __saved_record : Record
        Deep copy of Record at the penultimate scan in the sequence. This and
        following 2 attributes used for link-up in dynamic updates.
    __saved_counter : Counter
        Deep copy of Counter.
    __saved_objects : dict
        Deep copy of current_objects.

    """

    def __init__(self, field='reflectivity'):
        self.params = {'FIELD_THRESH': FIELD_THRESH,
                       'MIN_SIZE': MIN_SIZE,
                       'SEARCH_MARGIN': SEARCH_MARGIN,
                       'FLOW_MARGIN': FLOW_MARGIN,
                       'MAX_FLOW_MAG': MAX_FLOW_MAG,
                       'MAX_DISPARITY': MAX_DISPARITY,
                       'MAX_SHIFT_DISP': MAX_SHIFT_DISP,
                       'ISO_THRESH': ISO_THRESH,
                       'ISO_SMOOTH': ISO_SMOOTH,
                       'GS_ALT': GS_ALT}

        self.field = field
        self.grid_size = None
        self.radar_info = None
        self.last_grid = None
        self.counter = None
        self.record = None
        self.current_objects = None
        self.tracks = pd.DataFrame()

        self.__saved_record = None
        self.__saved_counter = None
        self.__saved_objects = None

    def __save(self):
        """ Saves deep copies of record, counter, and current_objects. """
        self.__saved_record = copy.deepcopy(self.record)
        self.__saved_counter = copy.deepcopy(self.counter)
        self.__saved_objects = copy.deepcopy(self.current_objects)

    def __load(self):
        """ Loads saved copies of record, counter, and current_objects. If new
        tracks are appended to existing tracks via the get_tracks method, the
        most recent scan prior to the addition must be overwritten to link up
        with the new scans. Because of this, record, counter and
        current_objects must be reverted to their state in the penultimate
        iteration of the loop in get_tracks. See get_tracks for details. """
        self.record = self.__saved_record
        self.counter = self.__saved_counter
        self.current_objects = self.__saved_objects

    def get_tracks(self, grids):
        """ Obtains tracks given a list of pyart grid objects. This is the
        primary method of the tracks class. This method makes use of all of the
        functions and helper classes defined above. """
        start_time = datetime.datetime.now()

        if self.record is None:
            # tracks object being initialized
            grid_obj2 = next(grids)
            self.grid_size = get_grid_size(grid_obj2)
            self.radar_info = get_radar_info(grid_obj2)
            self.counter = Counter()
            self.record = Record(grid_obj2)
        else:
            # tracks object being updated
            grid_obj2 = self.last_grid
            self.tracks.drop(self.record.scan + 1)  # last scan is overwritten

        if self.current_objects is None:
            newRain = True
        else:
            newRain = False

        raw2, frame2 = extract_grid_data(grid_obj2, self.field, self.grid_size,
                                         self.params)

        while grid_obj2 is not None:
            grid_obj1 = grid_obj2
            raw1 = raw2
            frame1 = frame2

            try:
                grid_obj2 = next(grids)
            except StopIteration:
                grid_obj2 = None

            if grid_obj2 is not None:
                self.record.update_scan_and_time(grid_obj1, grid_obj2)
                raw2, frame2 = extract_grid_data(grid_obj2,
                                                 self.field,
                                                 self.grid_size,
                                                 self.params)
            else:
                # setup to write final scan
                self.__save()
                self.last_grid = grid_obj1
                self.record.update_scan_and_time(grid_obj1)
                raw2 = None
                frame2 = np.zeros_like(frame1)

            if np.max(frame1) == 0:
                newRain = True
                print('No cells found in scan', self.record.scan)
                self.current_objects = None
                continue

            global_shift = get_global_shift(raw1, raw2, self.params)
            pairs = get_pairs(frame1,
                              frame2,
                              global_shift,
                              self.current_objects,
                              self.record,
                              self.params)

            if newRain:
                # first nonempty scan after a period of empty scans
                self.current_objects, self.counter = init_current_objects(
                    frame1,
                    frame2,
                    pairs,
                    self.counter
                )
                newRain = False
            else:
                self.current_objects, self.counter = update_current_objects(
                    frame1,
                    frame2,
                    pairs,
                    self.current_objects,
                    self.counter
                )

            obj_props = get_object_prop(frame1, grid_obj1, self.field,
                                        self.record, self.params)
            self.record.add_uids(self.current_objects)
            self.tracks = write_tracks(self.tracks, self.record,
                                       self.current_objects, obj_props)
            del grid_obj1, raw1, frame1, global_shift, pairs, obj_props
            # scan loop end
        self.__load()
        time_elapsed = datetime.datetime.now() - start_time
        print('\n')
        print('time elapsed', np.round(time_elapsed.seconds/60, 1), 'minutes')
        return
