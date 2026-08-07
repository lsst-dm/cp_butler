# This file is part of cp_butler.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__all__ = ["calibtool_recertify"]

import logging

from lsst.daf.butler import Butler, CollectionType
from ..utils import _probe, _create_timespan


def calibtool_recertify(repo, collections, dataset_type,
                        begin_date, end_date,
                        new_begin_date, new_end_date,
                        dry_run):
    """Recertify a calibration from the specified collection by changing
    the validity date range.

    Parmeters
    ---------
    repo : `str`
        Location of the butler repository to operate on.
    collections : `tuple` [`str`]
        List of collections to search through.
    dataset_type : `tuple` [`str`]
        List of dataset types to decertify.
    begin_date : `str`
        The ISO-8601 datetime (TAI) of the beginning of the
        calibration to recertify.
    end_date : `str`
        The ISO-8601 datetime (TAI) of the end of the calibration to
        recertify.
    new_begin_date : `str`
        The ISO-8601 datetime (TAI) of the new beginning of the
        calibration to recertify.
    new_end_date : `str`
        The ISO-8601 datetime (TAI) of the new end of the calibration to
        recertify.
    dry_run : `bool`
        If false, do not change theo database.
    """
    log = logging.getLogger(__name__)
    if len(dataset_type) == 0:
        raise RuntimeError("A dataset_type must be specified for decertification.")
    if len(collections) != 1:
        raise RuntimeError("For safety, only one collection may be specified at a time.")

    existing_timespan = _create_timespan(begin_date, end_date)
    updated_timespan = _create_timespan(new_begin_date, new_end_date)

    # This can only decertify part of a currently valid timespan.
    # Ensure we meet that case.
    is_valid = True
    if not existing_timespan.overlaps(updated_timespan):
        is_valid = False
    if not existing_timespan.contains(updated_timespan):
        is_valid = False
    if not is_valid:
        raise RuntimeError("The new date range is not a subset of the existing date range.")

    timespan = existing_timespan.difference(updated_timespan)

    nDecertified = 0
    with Butler.from_config(repo, writeable=not dry_run) as butler:
        collection_type = butler.collections.get_info(collections[0]).type
        if collection_type != CollectionType.CALIBRATION:
            raise RuntimeError("For safety, only CALIBRATION type collections may be specified.")

        datasets = _probe(butler, collections, dataset_type)

        for ds in datasets:
            if ds['calib_timespan'] == existing_timespan:
                grammar = {True: 'would', False: 'will'}
                log.info(f"Dataset {ds['calib_type']} {ds['calib_dataId']} {ds['gen_run']} "
                         f"{grammar[dry_run]} be recertified.")
                if not dry_run:
                    for ts in timespan:
                        butler.registry.decertify(ds['calib_collection'],
                                                  ds['calib_type'],
                                                  ts)
                    nDecertified += 1

    if nDecertified == 0 and not dry_run:
        raise RuntimeError("No datasets were recertified.")
