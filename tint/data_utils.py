"""
tint.data_utils
===============
Tools for obtaining and handling radar data.

"""

import tempfile

from boto.s3.connection import S3Connection
from datetime import datetime, timedelta

import pyart


def read_nexrad_key(key):
    """
    Returns pyart radar object from nexrad S3 key.
    """
    tmp = tempfile.NamedTemporaryFile()
    key.get_contents_to_filename(tmp.name)
    return pyart.io.read(tmp.name)


def get_nexrad_keys(site, start=None, end=None):
    """
    Get generator of pyart radar objects for all nexrad data between two
    datetimes from Amazon S3.
    ----------
    site : string
        site code e.g. 'khgx'
    start : string
        datetime e.g. '20180101_000000'
    end : string
        same format as start

    """
    fmt = '%Y%m%d_%H%M%S'

    if start is None:
        start = datetime.utcnow() - timedelta(hours=1)
    else:
        start = datetime.strptime(start, fmt)
    if end is None:
        end = datetime.utcnow()
    else:
        end = datetime.strptime(end, fmt)
    if end < start:
        print('end datetime precedes start datetime')
        return

    site = site.upper()

    dates = []
    day_i = start
    while day_i < end:
        dates.append(day_i)
        day_i += timedelta(days=1)

    date_keys = [datetime.strftime(date, '%Y/%m/%d/' + site) for date in dates]

    conn = S3Connection(anon=True)
    bucket = conn.get_bucket('noaa-nexrad-level2')

    keys = [key for date_key in date_keys
            for key in list(bucket.list(date_key))
            if (('.tar' not in str(key)) and ('_MDM' not in str(key)))]

    if len(keys) == 0:
        print('Found 0 files.')
        return

    # Key ealier for keys before 'V06'
    if '.gz>' in str(keys[0]):
        key_fmt = site + '%Y%m%d_%H%M%S_V06.gz>'
        key_fmt_earlier = site + '%Y%m%d_%H%M%S.gz>'
    else:
        key_fmt = site + '%Y%m%d_%H%M%S_V06>'
        key_fmt_earlier = site + '%Y%m%d_%H%M%S>'

    key_dts = []
    for key in keys:
        try:
            key_dts.append(datetime.strptime(str(key).split('/')[-1], key_fmt))
        except ValueError:
            key_dts.append(
                datetime.strptime(str(key).split('/')[-1], key_fmt_earlier))
    key_dts = zip(keys, key_dts)
    keys = [key for key, dt in key_dts if dt > start and dt < end]
    print('Found', len(keys), 'keys.')
    return keys
