[![Issues](https://img.shields.io/github/issues/open-public-transport/open-public-transport-analytics)](https://github.com/open-public-transport/open-public-transport-analytics/issues)

<br />
<p align="center">
  <a href="https://github.com/open-public-transport/open-public-transport-analytics">
    <img src="./logo_with_text.png" alt="Logo" height="80">
  </a>

  <h1 align="center">Open Public Transport (Analytics)</h1>

  <p align="center">
    Analytics of <a href="https://github.com/open-public-transport/open-public-transport-data" target="_blank">Open
     Public Transport data</a> 
  </p>
</p>

## About The Project

tbd

### Built With

* tbd

## Installation

Initialize the submodules of this repository by running the following commands.

```shell script
git submodule init
git submodule update
```

Install Anaconda

```shell script
brew install --cask anaconda
export PATH="/usr/local/anaconda3/bin:$PATH"
```

Install [osmnx](https://osmnx.readthedocs.io/en/stable/#installation).

```shell script
conda config --prepend channels conda-forge
conda create -n ox --strict-channel-priority osmnx
```

**BEWARE:** Make sure that any venv is deactivated which can be done by `deactivate`.
**BEWARE:** Make sure that you only activate the `ox` environment using `conda activate ox`.

Install GDAL bindings.

```shell script
brew install gdal
pip download GDAL
tar -xpzf GDAL-*.tar.gz
cd GDAL-*
python setup.py build_ext --gdal-config /usr/local/Cellar/gdal/*/bin/gdal-config
python setup.py build
python setup.py install
```

Install the following dependencies to fulfill the requirements for this project to run.

```shell script
python -m pip install --upgrade pip
pip install flake8 pytest
pip install geojson
pip install tdqm
pip install GDAL
pip install networkx
pip install shapely
```

## Usage

Run this command to start the main script.

```shell script
python main.py [OPTION]...

  -h, --help                           show this help
  -c, --clean                          clean intermediate results before start
  -q, --quiet                          do not log outputs
  -p, --points                         number of sample points to use

Examples:
  python main.py -c -p 10000
```

## Roadmap

See the [open issues](https://github.com/open-public-transport/open-public-transport-analytics/issues) for a list of proposed features (and
 known issues).

## Contributing

Follow our [contribution guidelines](./CONTRIBUTING.md).

## Funding

Between September 2021 through February 2022 this project is founded by [German Federal Ministry of Education and Research](https://www.bmbf.de/bmbf/en/home/home_node.html) and supported by [Prototype Fund](https://prototypefund.de/).

<p align="center">
  <a href="https://www.bmbf.de/bmbf/en/home/home_node.html">
    <img src="./logo-bmbf.svg" alt="Logo" height="100">
  </a>
  <a href="https://prototypefund.de/">
    <img src="./logo-ptf.svg" alt="Logo" height="80">
  </a>
</p>

## License

Distributed under the GPLv3 License. See [LICENSE.md](./LICENSE.md) for more information.

## Contact

kontakt@openpublictransport.de
