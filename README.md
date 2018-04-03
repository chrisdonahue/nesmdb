# The NES Music Database (NES-MDB)

The NES Music Database (NES-MDB) is a dataset for training machine learning models to compose music for the NES audio processing unit. `nesmdb` is a Python package that can be used to convert between low- and high-level representations of NES music.

## Installation

To install `nesmdb`, install it as a local Python package with `pip`.

`pip install -e .`

### Rendering WAV

The `vgm2wav` tool from [VGMPlay](https://github.com/vgmrips/vgmplay) is required to synthesize NES audio. NES-MDB will look for this binary on your path or in the ${VGMPLAYDIR} environment variable. Installation instructions:

* `wget https://github.com/vgmrips/vgmplay/archive/0.40.8.tar.gz`
* `tar xvfz 0.40.8.tar.gz`
* `cd vgmplay-0.40.8/VGMPlay`
* `make`
* `export VGMTOWAV=\`pwd\`/vgm2wav`

To render WAV

## File formats


