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

from astropy.time import Time

from lsst.daf.butler import Butler, Timespan, CollectionType
from ..utils import _probe


def calibtool_recertify(repo, collections, dataset_type,
                        begin_date, end_date,
                        new_begin_date, new_end_date,
                        dry_run, verbose):
    time_start = None
    time_end = None

    new_time_start = None
    new_time_end = None

    if len(dataset_type) == 0:
        raise RuntimeError("A dataset_type must be specified for decertification.")
    if len(collections) != 1:
        raise RuntimeError("For safety, only one collection may be specified at a time.")

    if begin_date is not None:
        time_start = Time(begin_date, scale="tai", format="isot")
    if end_date is not None:
        time_end = Time(end_date, scale="tai", format="isot")
    if time_start is None and time_end is None:
        raise RuntimeError("Cannot continue with no valid dates.")
    existing_timespan = Timespan(time_start, time_end)

    if new_begin_date is not None:
        new_time_start = Time(new_begin_date, scale="tai", format="isot")
    if new_end_date is not None:
        new_time_end = Time(new_end_date, scale="tai", format="isot")
    if new_time_start is None and new_time_end is None:
        raise RuntimeError("Cannot continue with no valid updated dates.")
    updated_timespan = Timespan(new_time_start, new_time_end)

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
        collection_type = butler.registry.getCollectionType(collections[0])
        if collection_type != CollectionType.CALIBRATION:
            raise RuntimeError("For safety, only CALIBRATION type collections may be specified.")

        datasets = _probe(butler, collections, dataset_type)
        if verbose or True:
            for ds in datasets:
                print(
                    ds["calib_type"],
                    ds["gen_run"],
                    ds["calib_collection"],
                    ds["calib_dataId"],
                    ds["calib_timespan"]
                )

        for ds in datasets:
            if ds['calib_timespan'] == existing_timespan:
                grammar = {True: 'would', False: 'will'}
                print(f"Dataset {ds['calib_type']} {ds['calib_dataId']} {ds['gen_run']} "
                      f"{grammar[dry_run]} be recertified.")
                if not dry_run:
                    for ts in timespan:
                        butler.registry.decertify(ds['calib_collection'],
                                                  ds['calib_type'],
                                                  ts)
                    nDecertified += 1

        if verbose and not dry_run:
            datasets = _probe(butler, collections, dataset_type)
            for ds in datasets:
                print(
                    ds["calib_type"],
                    ds["gen_run"],
                    ds["calib_collection"],
                    ds["calib_dataId"],
                    ds["calib_timespan"]
                )

    if nDecertified == 0:
        raise RuntimeError("No datasets were decertified.")
