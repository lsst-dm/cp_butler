# This file is part of cp_butler.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import tempfile
import unittest

import lsst.daf.butler.tests as butlerTests
import lsst.ip.isr.isrMockLSST as isrMockLSST
import lsst.utils.tests

from astropy.time import Time
from lsst.daf.butler import Timespan, CollectionType, DatasetType
from lsst.daf.butler.cli.butler import cli
from lsst.daf.butler.cli.utils import LogCliRunner


class CommandLineTests(lsst.utils.tests.TestCase):
    def setUp(self):
        # based on summit_utils/test_quickLook.py
        self.bias = isrMockLSST.BiasMockLSST().run()
        self.camera = isrMockLSST.BiasMockLSST().getCamera()

        self.repo_path = tempfile.TemporaryDirectory(delete=False)
        self.butler = butlerTests.makeTestRepo(self.repo_path.name)

        butlerTests.addDataIdValue(self.butler, "instrument", self.camera.getName())
        # The first detector of the test camera is id=10
        butlerTests.addDataIdValue(self.butler, "detector", self.camera[10].getId())

        # Just do one detector
        detector_id = self.butler.registry.expandDataId(
            {
                "instrument": self.camera.getName(),
                "detector": self.camera[10].getId(),
            }
        )

        # Register and put the bias.
        biasDatasetType = DatasetType(
            "bias",
            ("instrument", "detector"),
            "Exposure",
            universe=self.butler.dimensions,
            isCalibration=True
        )

        self.butler.registry.registerDatasetType(biasDatasetType)

        self.butler.collections.register("testCam/calib/biasGen")
        self.butler.put(self.bias, "bias", detector_id, run="testCam/calib/biasGen")

        # Get the bias dataset, and then register it for three date
        # ranges for testing.
        biasDataset = self.butler.registry.findDataset(
            "bias",
            dataId=detector_id,
            collections="testCam/calib/biasGen",
        )

        stop0 = Time("2020-01-01T00:00:00", scale="tai", format="isot")

        start1 = Time("2020-01-01T00:00:00", scale="tai", format="isot")
        stop1 = Time("2021-01-01T00:00:00", scale="tai", format="isot")

        start2 = Time("2021-01-01T00:00:00", scale="tai", format="isot")
        stop2 = Time("2022-01-01T00:00:00", scale="tai", format="isot")

        start3 = Time("2022-01-01T00:00:00", scale="tai", format="isot")
        stop3 = Time("2023-01-01T00:00:00", scale="tai", format="isot")

        start4 = Time("2023-01-01T00:00:00", scale="tai", format="isot")

        self.butler.registry.registerCollection("testCam/calib/bias.00", CollectionType.CALIBRATION)
        self.butler.registry.certify(
            "testCam/calib/bias.00",
            [biasDataset],
            Timespan(None, stop0)
        )

        self.butler.registry.registerCollection("testCam/calib/bias.01", CollectionType.CALIBRATION)
        self.butler.registry.certify(
            "testCam/calib/bias.01",
            [biasDataset],
            Timespan(start1, stop1)
        )

        self.butler.registry.registerCollection("testCam/calib/bias.02", CollectionType.CALIBRATION)
        self.butler.registry.certify(
            "testCam/calib/bias.02",
            [biasDataset],
            Timespan(start2, stop2)
        )

        self.butler.registry.registerCollection("testCam/calib/bias.03", CollectionType.CALIBRATION)
        self.butler.registry.certify(
            "testCam/calib/bias.03",
            [biasDataset],
            Timespan(start3, stop3)
        )

        self.butler.registry.registerCollection("testCam/calib/bias.04", CollectionType.CALIBRATION)
        self.butler.registry.certify(
            "testCam/calib/bias.04",
            [biasDataset],
            Timespan(start4, None)
        )

        self.butler.registry.registerCollection("testCam/calib", CollectionType.CHAINED)
        self.butler.collections.prepend_chain("testCam/calib",
                                              ["testCam/calib/bias.00",
                                               "testCam/calib/bias.01",
                                               "testCam/calib/bias.02",
                                               "testCam/calib/bias.03",
                                               "testCam/calib/bias.04"])
        self.runner = LogCliRunner()

    def tearDown(self):
        self.repo_path.cleanup()

    def test_probe(self):
        result = self.runner.invoke(cli, ["calibtool", "probe", self.repo_path.name,
                                          "--collections", "testCam/calib"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.stdout,
            "calib_type        gen_run           calib_collection                  "
            "calib_dataId                              calib_timespan              \n"
            "---------- --------------------- --------------------- "
            "------------------------------------------ ------------------------------------------\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.00 "
            "{instrument: 'testCameraSC', detector: 10} (-∞, 2020-01-01T00:00:00)                 \n"
            "bias       testCam/calib/biasGen testCam/calib/bias.01 "
            "{instrument: 'testCameraSC', detector: 10} [2020-01-01T00:00:00, 2021-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.02 "
            "{instrument: 'testCameraSC', detector: 10} [2021-01-01T00:00:00, 2022-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.03 "
            "{instrument: 'testCameraSC', detector: 10} [2022-01-01T00:00:00, 2023-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.04 "
            "{instrument: 'testCameraSC', detector: 10} [2023-01-01T00:00:00, ∞)                  \n"
        )

    # Decertify tests
    def test_decertify_full_date(self):
        result_before = self.runner.invoke(cli, ["calibtool", "probe", self.repo_path.name,
                                                 "--collections", "testCam/calib"])
        self.assertEqual(result_before.exit_code, 0)
        self.assertEqual(
            result_before.stdout,
            "calib_type        gen_run           calib_collection                  "
            "calib_dataId                              calib_timespan              \n"
            "---------- --------------------- --------------------- "
            "------------------------------------------ ------------------------------------------\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.00 "
            "{instrument: 'testCameraSC', detector: 10} (-∞, 2020-01-01T00:00:00)                 \n"
            "bias       testCam/calib/biasGen testCam/calib/bias.01 "
            "{instrument: 'testCameraSC', detector: 10} [2020-01-01T00:00:00, 2021-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.02 "
            "{instrument: 'testCameraSC', detector: 10} [2021-01-01T00:00:00, 2022-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.03 "
            "{instrument: 'testCameraSC', detector: 10} [2022-01-01T00:00:00, 2023-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.04 "
            "{instrument: 'testCameraSC', detector: 10} [2023-01-01T00:00:00, ∞)                  \n"
        )

        result_decert = self.runner.invoke(
            cli,
            [
                "calibtool", "decertify", self.repo_path.name,
                "--collections", "testCam/calib/bias.01",
                "--dataset-type", "bias",
                "--begin-date", "2020-01-01T00:00:00",
                "--end-date", "2021-01-01T00:00:00",
                "--dry-run", "False"
            ],
        )
        self.assertEqual(result_decert.exit_code, 0)

        result_after = self.runner.invoke(cli, ["calibtool", "probe", self.repo_path.name,
                                                "--collections", "testCam/calib"])
        self.assertEqual(result_after.exit_code, 0)
        self.assertEqual(
            result_after.stdout,
            "calib_type        gen_run           calib_collection                  "
            "calib_dataId                              calib_timespan              \n"
            "---------- --------------------- --------------------- "
            "------------------------------------------ ------------------------------------------\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.00 "
            "{instrument: 'testCameraSC', detector: 10} (-∞, 2020-01-01T00:00:00)                 \n"
            "bias       testCam/calib/biasGen testCam/calib/bias.02 "
            "{instrument: 'testCameraSC', detector: 10} [2021-01-01T00:00:00, 2022-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.03 "
            "{instrument: 'testCameraSC', detector: 10} [2022-01-01T00:00:00, 2023-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.04 "
            "{instrument: 'testCameraSC', detector: 10} [2023-01-01T00:00:00, ∞)                  \n"
        )

    def test_decertify_inf_future(self):
        result_before = self.runner.invoke(cli, ["calibtool", "probe", self.repo_path.name,
                                                 "--collections", "testCam/calib"])
        self.assertEqual(result_before.exit_code, 0)
        self.assertEqual(
            result_before.stdout,
            "calib_type        gen_run           calib_collection                  "
            "calib_dataId                              calib_timespan              \n"
            "---------- --------------------- --------------------- "
            "------------------------------------------ ------------------------------------------\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.00 "
            "{instrument: 'testCameraSC', detector: 10} (-∞, 2020-01-01T00:00:00)                 \n"
            "bias       testCam/calib/biasGen testCam/calib/bias.01 "
            "{instrument: 'testCameraSC', detector: 10} [2020-01-01T00:00:00, 2021-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.02 "
            "{instrument: 'testCameraSC', detector: 10} [2021-01-01T00:00:00, 2022-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.03 "
            "{instrument: 'testCameraSC', detector: 10} [2022-01-01T00:00:00, 2023-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.04 "
            "{instrument: 'testCameraSC', detector: 10} [2023-01-01T00:00:00, ∞)                  \n"
        )

        result_decert = self.runner.invoke(
            cli,
            [
                "calibtool", "decertify", self.repo_path.name,
                "--collections", "testCam/calib/bias.04",
                "--dataset-type", "bias",
                "--begin-date", "2023-01-01T00:00:00",
                "--dry-run", "False"
            ],
        )
        self.assertEqual(result_decert.exit_code, 0)

        result_after = self.runner.invoke(cli, ["calibtool", "probe", self.repo_path.name,
                                                "--collections", "testCam/calib"])
        self.assertEqual(result_after.exit_code, 0)
        self.assertEqual(
            result_after.stdout,
            "calib_type        gen_run           calib_collection                  "
            "calib_dataId                              calib_timespan              \n"
            "---------- --------------------- --------------------- "
            "------------------------------------------ ------------------------------------------\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.00 "
            "{instrument: 'testCameraSC', detector: 10} (-∞, 2020-01-01T00:00:00)                 \n"
            "bias       testCam/calib/biasGen testCam/calib/bias.01 "
            "{instrument: 'testCameraSC', detector: 10} [2020-01-01T00:00:00, 2021-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.02 "
            "{instrument: 'testCameraSC', detector: 10} [2021-01-01T00:00:00, 2022-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.03 "
            "{instrument: 'testCameraSC', detector: 10} [2022-01-01T00:00:00, 2023-01-01T00:00:00)\n"
        )

    def test_decertify_inf_past(self):
        result_before = self.runner.invoke(cli, ["calibtool", "probe", self.repo_path.name,
                                                 "--collections", "testCam/calib"])
        self.assertEqual(result_before.exit_code, 0)
        self.assertEqual(
            result_before.stdout,
            "calib_type        gen_run           calib_collection                  "
            "calib_dataId                              calib_timespan              \n"
            "---------- --------------------- --------------------- "
            "------------------------------------------ ------------------------------------------\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.00 "
            "{instrument: 'testCameraSC', detector: 10} (-∞, 2020-01-01T00:00:00)                 \n"
            "bias       testCam/calib/biasGen testCam/calib/bias.01 "
            "{instrument: 'testCameraSC', detector: 10} [2020-01-01T00:00:00, 2021-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.02 "
            "{instrument: 'testCameraSC', detector: 10} [2021-01-01T00:00:00, 2022-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.03 "
            "{instrument: 'testCameraSC', detector: 10} [2022-01-01T00:00:00, 2023-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.04 "
            "{instrument: 'testCameraSC', detector: 10} [2023-01-01T00:00:00, ∞)                  \n"
        )

        result_decert = self.runner.invoke(
            cli,
            [
                "calibtool", "decertify", self.repo_path.name,
                "--collections", "testCam/calib/bias.00",
                "--dataset-type", "bias",
                "--end-date", "2020-01-01T00:00:00",
                "--dry-run", "False"
            ],
        )
        self.assertEqual(result_decert.exit_code, 0)

        result_after = self.runner.invoke(cli, ["calibtool", "probe", self.repo_path.name,
                                                "--collections", "testCam/calib"])
        self.assertEqual(result_after.exit_code, 0)
        self.assertEqual(
            result_after.stdout,
            "calib_type        gen_run           calib_collection                  "
            "calib_dataId                              calib_timespan              \n"
            "---------- --------------------- --------------------- "
            "------------------------------------------ ------------------------------------------\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.01 "
            "{instrument: 'testCameraSC', detector: 10} [2020-01-01T00:00:00, 2021-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.02 "
            "{instrument: 'testCameraSC', detector: 10} [2021-01-01T00:00:00, 2022-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.03 "
            "{instrument: 'testCameraSC', detector: 10} [2022-01-01T00:00:00, 2023-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.04 "
            "{instrument: 'testCameraSC', detector: 10} [2023-01-01T00:00:00, ∞)                  \n"
        )

    def test_decertifyExpectedFailures(self):
        # CHAINED collection
        result_decert = self.runner.invoke(
            cli,
            [
                "calibtool", "decertify", self.repo_path.name,
                "--collections", "testCam/calib",
                "--dataset-type", "bias",
                "--begin-date", "2020-01-01T00:00:00",
                "--end-date", "2021-01-01T00:00:00",
                "--dry-run", "False"
            ],
        )
        self.assertEqual(result_decert.exit_code, 1)

        # Multiple collections
        result_decert = self.runner.invoke(
            cli,
            [
                "calibtool", "decertify", self.repo_path.name,
                "--collections", "testCam/calib/bias.00,testCam/calib/bias.01",
                "--dataset-type", "bias",
                "--begin-date", "2020-01-01T00:00:00",
                "--end-date", "2021-01-01T00:00:00",
                "--dry-run", "False"
            ],
        )
        self.assertEqual(result_decert.exit_code, 1)

        # Wildcard collections
        result_decert = self.runner.invoke(
            cli,
            [
                "calibtool", "decertify", self.repo_path.name,
                "--collections", "testCam/calib/bias.*",
                "--dataset-type", "bias",
                "--begin-date", "2020-01-01T00:00:00",
                "--end-date", "2021-01-01T00:00:00",
                "--dry-run", "False"
            ],
        )
        self.assertEqual(result_decert.exit_code, 1)

        # Missing date
        result_decert = self.runner.invoke(
            cli,
            [
                "calibtool", "decertify", self.repo_path.name,
                "--collections", "testCam/calib/bias.00",
                "--dataset-type", "bias",
                "--dry-run", "False"
            ],
        )
        self.assertEqual(result_decert.exit_code, 1)

        # Bad date
        result_decert = self.runner.invoke(
            cli,
            [
                "calibtool", "decertify", self.repo_path.name,
                "--collections", "testCam/calib/bias.01",
                "--dataset-type", "bias",
                "--begin-date", "2020-02-01T00:00:00",
                "--end-date", "2021-02-01T00:00:00",
                "--dry-run", "False"
            ],
        )
        self.assertEqual(result_decert.exit_code, 1)

    # Recertify tests
    def test_recertify(self):
        result_before = self.runner.invoke(cli, ["calibtool", "probe", self.repo_path.name,
                                                 "--collections", "testCam/calib"])
        self.assertEqual(result_before.exit_code, 0)
        self.assertEqual(
            result_before.stdout,
            "calib_type        gen_run           calib_collection                  "
            "calib_dataId                              calib_timespan              \n"
            "---------- --------------------- --------------------- "
            "------------------------------------------ ------------------------------------------\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.00 "
            "{instrument: 'testCameraSC', detector: 10} (-∞, 2020-01-01T00:00:00)                 \n"
            "bias       testCam/calib/biasGen testCam/calib/bias.01 "
            "{instrument: 'testCameraSC', detector: 10} [2020-01-01T00:00:00, 2021-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.02 "
            "{instrument: 'testCameraSC', detector: 10} [2021-01-01T00:00:00, 2022-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.03 "
            "{instrument: 'testCameraSC', detector: 10} [2022-01-01T00:00:00, 2023-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.04 "
            "{instrument: 'testCameraSC', detector: 10} [2023-01-01T00:00:00, ∞)                  \n"
        )

        result_recert = self.runner.invoke(
            cli,
            [
                "calibtool", "recertify", self.repo_path.name,
                "--collections", "testCam/calib/bias.01",
                "--dataset-type", "bias",
                "--begin-date", "2020-01-01T00:00:00",
                "--end-date", "2021-01-01T00:00:00",
                "--new-begin-date", "2020-02-02T00:00:00",
                "--new-end-date", "2020-10-01T00:00:00",
                "--dry-run", "False"
            ],
        )
        self.assertEqual(result_recert.exit_code, 0)

        result_after = self.runner.invoke(cli, ["calibtool", "probe", self.repo_path.name,
                                                "--collections", "testCam/calib"])
        self.assertEqual(result_after.exit_code, 0)
        self.assertEqual(
            result_after.stdout,
            "calib_type        gen_run           calib_collection                  "
            "calib_dataId                              calib_timespan              \n"
            "---------- --------------------- --------------------- "
            "------------------------------------------ ------------------------------------------\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.00 "
            "{instrument: 'testCameraSC', detector: 10} (-∞, 2020-01-01T00:00:00)                 \n"
            "bias       testCam/calib/biasGen testCam/calib/bias.01 "
            "{instrument: 'testCameraSC', detector: 10} [2020-02-02T00:00:00, 2020-10-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.02 "
            "{instrument: 'testCameraSC', detector: 10} [2021-01-01T00:00:00, 2022-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.03 "
            "{instrument: 'testCameraSC', detector: 10} [2022-01-01T00:00:00, 2023-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.04 "
            "{instrument: 'testCameraSC', detector: 10} [2023-01-01T00:00:00, ∞)                  \n"
        )

    # Recertify tests
    def test_recertifyExpectedFailures(self):
        result_before = self.runner.invoke(cli, ["calibtool", "probe", self.repo_path.name,
                                                 "--collections", "testCam/calib"])
        self.assertEqual(result_before.exit_code, 0)
        self.assertEqual(
            result_before.stdout,
            "calib_type        gen_run           calib_collection                  "
            "calib_dataId                              calib_timespan              \n"
            "---------- --------------------- --------------------- "
            "------------------------------------------ ------------------------------------------\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.00 "
            "{instrument: 'testCameraSC', detector: 10} (-∞, 2020-01-01T00:00:00)                 \n"
            "bias       testCam/calib/biasGen testCam/calib/bias.01 "
            "{instrument: 'testCameraSC', detector: 10} [2020-01-01T00:00:00, 2021-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.02 "
            "{instrument: 'testCameraSC', detector: 10} [2021-01-01T00:00:00, 2022-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.03 "
            "{instrument: 'testCameraSC', detector: 10} [2022-01-01T00:00:00, 2023-01-01T00:00:00)\n"
            "bias       testCam/calib/biasGen testCam/calib/bias.04 "
            "{instrument: 'testCameraSC', detector: 10} [2023-01-01T00:00:00, ∞)                  \n"
        )

        # Chained collection
        result_recert = self.runner.invoke(
            cli,
            [
                "calibtool", "recertify", self.repo_path.name,
                "--collections", "testCam/calib",
                "--dataset-type", "bias",
                "--begin-date", "2020-01-01T00:00:00",
                "--end-date", "2021-01-01T00:00:00",
                "--new-begin-date", "2020-02-02T00:00:00",
                "--new-end-date", "2020-10-01T00:00:00",
                "--dry-run", "False"
            ],
        )
        self.assertEqual(result_recert.exit_code, 1)

        # Multiple collections
        result_recert = self.runner.invoke(
            cli,
            [
                "calibtool", "recertify", self.repo_path.name,
                "--collections", "testCam/calib/bias.01,testCam/calib/bias.02",
                "--dataset-type", "bias",
                "--begin-date", "2020-01-01T00:00:00",
                "--end-date", "2021-01-01T00:00:00",
                "--new-begin-date", "2020-02-02T00:00:00",
                "--new-end-date", "2020-10-01T00:00:00",
                "--dry-run", "False"
            ],
        )
        self.assertEqual(result_recert.exit_code, 1)

        # Wildcard in collections
        result_recert = self.runner.invoke(
            cli,
            [
                "calibtool", "recertify", self.repo_path.name,
                "--collections", "testCam/calib/bias.*",
                "--dataset-type", "bias",
                "--begin-date", "2020-01-01T00:00:00",
                "--end-date", "2021-01-01T00:00:00",
                "--new-begin-date", "2020-02-02T00:00:00",
                "--new-end-date", "2020-10-01T00:00:00",
                "--dry-run", "False"
            ],
        )
        self.assertEqual(result_recert.exit_code, 1)

        # Missing date
        result_recert = self.runner.invoke(
            cli,
            [
                "calibtool", "recertify", self.repo_path.name,
                "--collections", "testCam/calib/bias.01",
                "--dataset-type", "bias",
                "--new-begin-date", "2020-02-02T00:00:00",
                "--new-end-date", "2020-10-01T00:00:00",
                "--dry-run", "False"
            ],
        )
        self.assertEqual(result_recert.exit_code, 1)

        # Missing date v2
        result_recert = self.runner.invoke(
            cli,
            [
                "calibtool", "recertify", self.repo_path.name,
                "--collections", "testCam/calib/bias.01",
                "--dataset-type", "bias",
                "--begin-date", "2020-01-01T00:00:00",
                "--end-date", "2021-01-01T00:00:00",
                "--dry-run", "False"
            ],
        )
        self.assertEqual(result_recert.exit_code, 1)

        # Bad date
        result_recert = self.runner.invoke(
            cli,
            [
                "calibtool", "recertify", self.repo_path.name,
                "--collections", "testCam/calib/bias.01",
                "--dataset-type", "bias",
                "--begin-date", "2021-01-01T00:00:00",
                "--end-date", "2022-01-01T00:00:00",
                "--new-begin-date", "2020-02-02T00:00:00",
                "--new-end-date", "2020-10-01T00:00:00",
                "--dry-run", "False"
            ],
        )
        self.assertEqual(result_recert.exit_code, 1)


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
