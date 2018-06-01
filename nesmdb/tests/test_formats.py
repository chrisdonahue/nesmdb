import glob
import os
from unittest import TestCase

from nesmdb.vgm import vgm_simplify, vgm_shorten

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