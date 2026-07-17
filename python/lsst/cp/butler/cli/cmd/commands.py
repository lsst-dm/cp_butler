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

import click

from lsst.daf.butler.cli.opt import (
    collections_option,
    dataset_type_option,
    #    destination_argument,
    repo_argument,
    # where_option,
)

from lsst.daf.butler.cli.utils import ButlerCommand
# , MWPath

from ... import script


@click.group(short_help="Commands to probe and update calibration collections.")
def calibtool():
    """Set of commands to probe and update calibration collections."""
    pass


@calibtool.command(
    short_help="Probe and update calibration collections.",
    cls=ButlerCommand,
)
@repo_argument(required=True)
@dataset_type_option(
    help=(
        "Comma-separated list of dataset types."
    )
)
@collections_option()
def probe(*args, **kwargs):
    """Print information about the calibrations in a given collection."""
    datasets = script.calibtool_probe(*args, **kwargs)
    if datasets:
        datasets.pprint_all(align="<")


@calibtool.command(
    short_help="Decertify a calibration.",
    cls=ButlerCommand,
)
@repo_argument(required=True)
@dataset_type_option(
    help=(
        "Comma-separated list of dataset types."
    )
)
@collections_option()
# @where_option()
@click.option(
    "--begin-date",
    type=str,
    default=None,
    help=(
        "ISO-8601 datetime (TAI) of the beginning of the validity range for the "
        "currently certified calibrations."
    ),
)
@click.option(
    "--end-date",
    type=str,
    default=None,
    help=(
        "ISO-8601 datetime (TAI) of the end of the validity range for the "
        "currently certified calibrations."
    ),
)
@click.option(
    "--dry-run",
    type=bool,
    default=True,
    help=(
        "If true, do not modify the butler repository."
    ),
)
@click.option(
    "--verbose",
    type=bool,
    default=False,
    help=(
        "If true, print status updates."
    ),
)
def decertify(*args, **kwargs):
    """Decertify a calibration from a calibration collection."""
    script.calibtool_decertify(*args, **kwargs)


@calibtool.command(
    short_help="Recertify a calibration with updated start and end dates.",
    cls=ButlerCommand,
)
@repo_argument(required=True)
@dataset_type_option(
    help=(
        "Comma-separated list of dataset types."
    )
)
@collections_option()
@click.option(
    "--begin-date",
    type=str,
    default=None,
    help=(
        "ISO-8601 datetime (TAI) of the beginning of the validity range for the "
        "currently certified calibrations."
    ),
)
@click.option(
    "--end-date",
    type=str,
    default=None,
    help=(
        "ISO-8601 datetime (TAI) of the end of the validity range for the "
        "currently certified calibrations."
    ),
)
@click.option(
    "--new-begin-date",
    type=str,
    default=None,
    help=(
        "ISO-8601 datetime (TAI) of the beginning of the updated validity range "
        "for the certified calibrations."""
    ),
)
@click.option(
    "--new-end-date",
    type=str,
    default=None,
    help=(
        "ISO-8601 datetime (TAI) of the end of the updated validity range "
        "for the certified calibrations."
    ),
)
@click.option(
    "--dry-run",
    type=bool,
    default=True,
    help=(
        "If true, do not modify the butler repository."
    ),
)
@click.option(
    "--verbose",
    type=bool,
    default=False,
    help=(
        "If true, print status updates."
    ),
)
def recertify(*args, **kwargs):
    """Recertify a calibration from a calibration collection."""
    script.calibtool_recertify(*args, **kwargs)


# @calibtool.command(
#     short_help=(
#         "Generate fingerprint.yaml for a given calibration collection."
#     ),
#     cls=ButlerCommand,
# )
# @repo_argument(required=True)
# @destination_argument(
#     required=True,
#     help="DESTINATION is the location of the output file.",
#     type=MWPath(file_okay=True, dir_okay=False, writable=True),
# )
# @collections_option()
# def fingerprint(*args, **kwargs):
#     """Generate a fingerprint file from a calibration collection."""
#     script.calibtool_fingerprint(*args, **kwargs)


# @calibtool.command(
#     short_help="Verify fingerprint.yaml for a given calibration collection.",
#     cls=ButlerCommand,
# )
# @repo_argument(required=True)
#     required=True,
#     help=(
#         "DESTINATION is the location of the input file (CZW: ???) "
#         "Look at python/lsst/daf/butler/cli/cmd/commands.py#L100"
#     ),
#     type=MWPath(file_okay=True, dir_okay=False, writable=False),
# )
# @collections_option()
# def authenticate(*args, **kwargs):
#     """Authenticate that the repository matches the fingerprint file."""
#     script.calibtool_authenticate(*args, **kwargs)
