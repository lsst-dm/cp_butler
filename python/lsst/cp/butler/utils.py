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

__all__ = []


def _probe(butler, collections, dataset_type):
    """Extract useful information about the calibrations in the specified
    collections.

    Parameters
    ----------
    butler : `lsst.daf.butler.Butler`
        Butler repo to query.
    collections : `list` [`str`]
        Comma separated list of collections to examine.
    dataset_type : `list` [`str`]
        List of dataset_types to restrict the results to.

    Returns
    -------
    datasets : `list` [`dict` [`str` : `str`]]
        List of matching datasets, along with their calibration
        association information.
    """
    datasets = []
    for butler_dataset_type in butler.registry.queryDatasetTypes(...):
        if not butler_dataset_type.isCalibration():
            continue

        for assoc in butler.registry.queryDatasetAssociations(butler_dataset_type,
                                                              collections=collections):
            if len(dataset_type) == 0 or butler_dataset_type.name in dataset_type:
                result = {
                    'calib_type': butler_dataset_type.name,
                    'gen_run': assoc.ref.run,
                    'calib_collection': assoc.collection,
                    'calib_dataId': assoc.ref.dataId,
                    'calib_timespan': assoc.timespan
                }
                datasets.append(result)
    return datasets
