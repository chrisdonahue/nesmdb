from __future__ import division
import glob
import os
from unittest import TestCase

from nesmdb.vgm import vgm_simplify, vgm_shorten
import nesmdb.cycle

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_EXAMPLE_VGMS = sorted(glob.glob(os.path.join(_TEST_DIR, 'data', '*.vgm')))

class TestFormats(TestCase):
  @classmethod
  def setUpClass(cls):
    vgms = []
    for vgm_fp in _EXAMPLE_VGMS:
      with open(vgm_fp, 'rb') as f:
        vgms.append(f.read())

    vgms_simple = [vgm_simplify(vgm)[0] for vgm in vgms]

    cls.vgms_full = vgms
    cls.vgms = vgms_simple


  def test_simplify(self):
    # Verify original lengths
    self.assertListEqual(
        [len(v) for v in self.vgms_full],
        [78942, 86159, 2685, 2254, 84706])

    # Remove invalid VGM commands
    vgms_simple = []
    delcmds = []
    for vgm in self.vgms_full:
      vgm, delcmd = vgm_simplify(vgm)
      vgms_simple.append(vgm)
      delcmds.append(delcmd)

    # Make sure we have deleted the right number of commands
    self.assertListEqual(delcmds, [5, 5, 4, 4, 5])

    # Make sure simplified lengths are correct
    self.assertListEqual(
        [len(v) for v in vgms_simple],
        [78927, 86144, 2673, 2242, 84691])

    # Shorten VGMs
    vgms_short = []
    for vgm in vgms_simple:
      vgms_short.append(vgm_shorten(vgm, 1000, 400))

    # Make sure shortened lengths are correct
    self.assertListEqual(
        [len(v) for v in vgms_short],
        [3193, 3193, 1756, 1192, 3193])


  def test_nlm(self):
    total_dist = 0.
    cycle_vgms = []
    for source_vgm in self.vgms:
      cycle_vgm = nesmdb.cycle.vgm_cycle(source_vgm, 'nlm')
      total_dist += nesmdb.cycle.vgm_dist(source_vgm, cycle_vgm)[0]
      cycle_vgms.append(cycle_vgm)

    # Make sure shortened lengths are correct
    self.assertListEqual(
        [len(v) for v in cycle_vgms],
        [82168, 86497, 2656, 2161, 87442])

    # Make sure the WAV files are lossless
    self.assertEqual(total_dist, 0.)


  def test_midi(self):
    total_dist = 0.
    cycle_vgms = []
    for source_vgm in self.vgms:
      cycle_vgm = nesmdb.cycle.vgm_cycle(source_vgm, 'midi', score_rate=24.)
      total_dist += nesmdb.cycle.vgm_dist(source_vgm, cycle_vgm)[0]
      cycle_vgms.append(cycle_vgm)

    # Make sure shortened lengths are correct
    self.assertListEqual(
        [len(v) for v in cycle_vgms],
        [12283, 16303, 1162, 1063, 15880])

    # Make sure the MIDI files are the same as expressive score
    avg_dist = total_dist / len(self.vgms)
    self.assertTrue(2.20 < avg_dist and avg_dist < 2.24)


  def test_exprsco(self):
    total_dist = 0.
    cycle_vgms = []
    for source_vgm in self.vgms:
      cycle_vgm = nesmdb.cycle.vgm_cycle(source_vgm, 'exprsco', score_rate=24.)
      total_dist += nesmdb.cycle.vgm_dist(source_vgm, cycle_vgm)[0]
      cycle_vgms.append(cycle_vgm)

    # Make sure shortened lengths are correct
    self.assertListEqual(
        [len(v) for v in cycle_vgms],
        [12283, 16303, 1162, 1063, 15880])

    # Make sure the expressive scores are within acceptable range
    avg_dist = total_dist / len(self.vgms)
    self.assertTrue(2.20 < avg_dist and avg_dist < 2.24)


  def test_seprsco(self):
    total_dist = 0.
    cycle_vgms = []
    for source_vgm in self.vgms:
      cycle_vgm = nesmdb.cycle.vgm_cycle(source_vgm, 'seprsco', score_rate=24.)
      total_dist += nesmdb.cycle.vgm_dist(source_vgm, cycle_vgm)[0]
      cycle_vgms.append(cycle_vgm)

    # Make sure shortened lengths are correct
    self.assertListEqual(
        [len(v) for v in cycle_vgms],
        [8026, 10573, 850, 790, 10330])

    # Make sure the expressive scores are within acceptable range
    avg_dist = total_dist / len(self.vgms)
    self.assertTrue(12.40 < avg_dist and avg_dist < 12.42)


  def test_blndsco(self):
    total_dist = 0.
    cycle_vgms = []
    for source_vgm in self.vgms:
      cycle_vgm = nesmdb.cycle.vgm_cycle(source_vgm, 'blndsco', score_rate=24.)
      total_dist += nesmdb.cycle.vgm_dist(source_vgm, cycle_vgm)[0]
      cycle_vgms.append(cycle_vgm)

    # Make sure shortened lengths are correct
    self.assertListEqual(
        [len(v) for v in cycle_vgms],
        [9589, 10630, 895, 853, 12361])

    # Make sure the expressive scores are within acceptable range
    avg_dist = total_dist / len(self.vgms)
    self.assertTrue(11.95 < avg_dist and avg_dist < 11.97)
