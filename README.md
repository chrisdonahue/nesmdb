# The NES Music Database

The NES Music Database (NES-MDB) is a dataset intended for training models to compose music for the NES.

This repository houses `nesmdb`, a Python package that can be used to convert between low- and high-level representations of NES music. Specifically, it converts between the [VGM file format](http://vgmrips.net/wiki/VGM_Specification) and simpler Numpy representations. **You only need to install this package if you want to listen to your results as synthesized by the NES.**

## NES-MDB Dataset

Links to download the datasets in various representations:

1. (Array-based) Expressive Score: [download](http://deepyeti.ucsd.edu/cdonahue/nesmdb/nesmdb24_exprsco.tar.gz)
1. (Array-based) Separated Score: [download](http://deepyeti.ucsd.edu/cdonahue/nesmdb/nesmdb24_seprsco.tar.gz)
1. (Array-based) Blended Score: [download](http://deepyeti.ucsd.edu/cdonahue/nesmdb/nesmdb24_blndsco.tar.gz)
1. (Event-based) MIDI: [download](http://deepyeti.ucsd.edu/cdonahue/nesmdb/nesmdb_midi.tar.gz)
1. (Text-based) NES Dissasembly (Functional): [download](http://deepyeti.ucsd.edu/cdonahue/nesmdb/nesmdb_ndf.tar.gz)
1. (Text-based) NES Dissasembly (Raw): [download](http://deepyeti.ucsd.edu/cdonahue/nesmdb/nesmdb_ndr.tar.gz)
1. (Rawest) VGM: [download](http://deepyeti.ucsd.edu/cdonahue/nesmdb/nesmdb_vgm.tar.gz)

### Score formats

TODO

### Raw formats

TODO

## Package Installation

To install `nesmdb`, install it as a local Python package with `pip`.

`pip install -e .`

## Simple Package Usage

If you have downloaded one of the datasets above and simply want to listen to the files in the dataset or your own generated results, follow these instructions.

### Rendering scores as WAVs

The `vgm2wav` tool from [VGMPlay](https://github.com/vgmrips/vgmplay) is required to synthesize NES audio. NES-MDB will look for this binary on your path or at the `${VGMTOWAV}` environment variable. Installation instructions:

1. `wget https://github.com/vgmrips/vgmplay/archive/0.40.8.tar.gz`
1. `tar xvfz 0.40.8.tar.gz`
1. `cd vgmplay-0.40.8/VGMPlay`
1. `make`
1. `` export VGMTOWAV=`pwd`/vgm2wav ``

Use the following commands to convert a batch of files to WAVs depending on your dataset version above. If you're converting a single file, you can remove the `--out_dir` argument

1. Expressive score: `python -m nesmdb.convert exprsco_to_wav --out_dir wav *.exprsco.pkl`
1. Separated score: `python -m nesmdb.convert exprsco_to_wav --out_dir wav *.seprsco.pkl`
1. Blended score: `python -m nesmdb.convert exprsco_to_wav --out_dir wav *.blndsco.pkl`
1. MIDI: `python -m nesmdb.convert midi_to_wav --out_dir wav *.mid`
1. NES Dissasembly (Functional): `python -m nesmdb.convert ndf_to_wav --out_dir wav *.ndf.pkl`
1. NES Dissasembly (Raw): `python -m nesmdb.convert ndr_to_wav --out_dir wav *.ndr.pkl`
1. VGM: `python -m nesmdb.convert vgm_to_wav --out_dir wav *.vgm`

## Advanced Package Usage

If you have additional needs, such as ingesting new VGM files into the dataset or using a new representation, you may be interested in the advanced usage information listed here.

### Ingesting new VGM files

TODO

### Testing new representations

TODO

#### VGM (`.vgm`)

The [VGM format](http://vgmrips.net/wiki/VGM_Specification) is designed to store timestamped logs of writes to several video game console APUs at audio sample rate (44.1 kHz). Version 1.61 added support for the NES APU (this is the only version `nesmdb` currently supports).

The following command simplifies `.vgm` files, removing all but Pulse 1, Pulse 2, Triangle and Noise channels. This is a required
