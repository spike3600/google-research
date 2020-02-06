# coding=utf-8
# Copyright 2020 The Google Research Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests compression_wrapper.

Since each compression operator class should have its own set of unit tests,
these tests will only check that we've created the correct type of compression
operator.
"""

from __future__ import absolute_import
from __future__ import division

from absl.testing import absltest
import mock

from graph_compression.compression_lib import compression_op as comp_op
from graph_compression.compression_lib import compression_wrapper_py2 as compression_wrapper
from graph_compression.compression_lib import simhash_compression_op


# Default global step value.
_GLOBAL_STEP = 10


class MatrixCompressorInterfaceMock(mock.MagicMock):

  def __init__(self, spec):
    super(MatrixCompressorInterfaceMock, self).__init__(spec)
    self._spec = spec


class CompressionWrapperTest(absltest.TestCase):

  def _create_compression_op_spec(self, option):
    hparams = comp_op.CompressionOp.get_default_hparams().parse(
        'name=cifar10_compression,'
        'alpha_decrement_value=0.005,'
        'begin_compression_step=40000,'
        'end_compression_step=100000,'
        'compression_frequency=100,'
        'use_tpu=False,'
        'update_option=1,'
        'rank=4')
    hparams.set_hparam('compression_option', option)
    return hparams

  def _default_compressor_spec(self, hparams):
    spec = comp_op.LowRankDecompMatrixCompressor.get_default_hparams()
    spec.set_hparam('rank', hparams.rank)
    return spec

  @mock.patch.object(comp_op, 'LowRankDecompMatrixCompressor')
  def testWrapper_CreatesProperCompressorOption1(self, low_rank_mock):
    hparams = self._create_compression_op_spec(1)
    mock_compressor = MatrixCompressorInterfaceMock(
        self._default_compressor_spec(hparams))
    low_rank_mock.side_effect = [mock_compressor]

    with mock.patch.object(comp_op, 'ApplyCompression') as apply_mock:
      compression_wrapper.get_apply_compression(hparams, _GLOBAL_STEP)
      apply_mock.assert_called_with(
          scope='default_scope',
          compression_spec=hparams,
          compressor=mock_compressor,
          global_step=_GLOBAL_STEP)

  @mock.patch.object(simhash_compression_op, 'SimhashMatrixCompressor')
  def testWrapper_CreatesProperCompressorOption2(self, sim_hash_mock):
    hparams = self._create_compression_op_spec(2)
    mock_compressor = MatrixCompressorInterfaceMock(
        self._default_compressor_spec(hparams))
    sim_hash_mock.side_effect = [mock_compressor]

    with mock.patch.object(simhash_compression_op,
                           'SimhashApplyCompression') as apply_mock:
      compression_wrapper.get_apply_compression(hparams, _GLOBAL_STEP)
      apply_mock.assert_called_with(
          scope='default_scope',
          compression_spec=hparams,
          compressor=mock_compressor,
          global_step=_GLOBAL_STEP)


if __name__ == '__main__':
  absltest.main()
