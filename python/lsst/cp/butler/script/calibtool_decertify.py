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

__all__ = ["calibtool_decertify"]

from astropy.time import Time

from lsst.daf.butler import Butler, Timespan, CollectionType
from ..utils import _probe


def calibtool_decertify(repo, collections, dataset_type, begin_date, end_date, dry_run, verbose):
    """Decertify a calibration from the specified collection.

    Parmeters
    ---------
    repo : `str`
        Location of the butler repository to operate on.
    collections : `tuple` [`str`]
        List of collections to search through.
    dataset_type : `tuple` [`str`]
        List of dataset_types to decertify.
    begin_date : `str`
    end_date : `str`
    dry_run : `bool`
        If false, do not change theo database.
    verbose : `bool`
        If true, print before and after datasets.
    """
    time_start = None
    time_end = None

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
    timespan = Timespan(time_start, time_end)

    nDecertified = 0
    with Butler.from_config(repo, writeable=not dry_run) as butler:
        collection_type = butler.registry.getCollectionType(collections[0])
        if collection_type != CollectionType.CALIBRATION:
            raise RuntimeError("For safety, only CALIBRATION type collections may be specified.")

        datasets = _probe(butler, collections, dataset_type)
        if verbose:
            print(datasets)

        for ds in datasets:
            if ds['calib_timespan'] == timespan:
                grammar = {True: 'would', False: 'will'}
                print(f"Dataset {ds} {grammar[dry_run]} be decertified.")
                if not dry_run:
                    butler.registry.decertify(ds['calib_collection'],
                                              ds['calib_type'],
                                              timespan)
                    nDecertified += 1
        if verbose and not dry_run:
            datasets = _probe(butler, collections, dataset_type)
            print(datasets)
    if nDecertified == 0:
        raise RuntimeError("No datasets were decertified.")
