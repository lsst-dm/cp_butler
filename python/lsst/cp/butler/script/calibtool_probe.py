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

__all__ = ["calibtool_probe"]

from lsst.daf.butler import Butler
from ..utils import _probe


def calibtool_probe(repo, collections, dataset_type):
    """Print useful information about the calibrations in the specified
    collections.

    Parameters
    ----------
    repo : `str`
        Location of the butler to examine.
    collections : `list` [`str`]
        Comma separated list of collections to examine.
    dataset_type : `list` [`str`]
        List of dataset_types to restrict the results to.

    Returns
    -------
    datasets : `astropy.table.Table`
        Table containing all matching calibrations.
    """
    with Butler.from_config(repo, writeable=False) as butler:
        datasets = _probe(butler, collections, dataset_type)

    return datasets
