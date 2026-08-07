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

import logging

from lsst.daf.butler import Butler, CollectionType
from ..utils import _probe, _create_timespan


def calibtool_decertify(repo, collections, dataset_type, begin_date, end_date, dry_run):
    """Decertify a calibration from the specified collection.

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
        calibration to decertify.
    end_date : `str`
        The ISO-8601 datetime (TAI) of the end of the calibration to
        decertify.
    dry_run : `bool`
        If false, do not change theo database.
    """
    log = logging.getLogger(__name__)
    if len(dataset_type) == 0:
        raise RuntimeError("A dataset_type must be specified for decertification.")
    if len(collections) != 1:
        raise RuntimeError("For safety, only one collection may be specified at a time.")

    timespan = _create_timespan(begin_date, end_date)

    nDecertified = 0
    with Butler.from_config(repo, writeable=not dry_run) as butler:
        collection_type = butler.collections.get_info(collections[0]).type
        if collection_type != CollectionType.CALIBRATION:
            raise RuntimeError("For safety, only CALIBRATION type collections may be specified.")

        datasets = _probe(butler, collections, dataset_type)

        for ds in datasets:
            if ds['calib_timespan'] == timespan:
                grammar = {True: 'would', False: 'will'}
                log.info(f"Dataset  {ds['calib_type']} {ds['calib_dataId']} {ds['gen_run']} "
                         f"{grammar[dry_run]} be decertified.")
                if not dry_run:
                    butler.registry.decertify(ds['calib_collection'],
                                              ds['calib_type'],
                                              timespan)
                    nDecertified += 1

    if nDecertified == 0 and not dry_run:
        raise RuntimeError("No datasets were decertified.")
