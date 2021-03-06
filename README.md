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
pip install geopy
pip install peartree
pip install fastapi
pip install osm2geojson
pip install google-cloud-storage
```

## Usage (prepare)

Run this command to download data.

```shell script
cd data
python main.py
```

## Usage (analysis)

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

## Usage (web server)

Run this command to run the web server locally.

```shell
cd ./app
python app.py --reload
```

Open http://localhost:8000/docs#/ to see the OpenAPI specification.

### Usage (local docker)

Run this command to run the docker container locally.

```shell
docker build -t open-public-transport .
docker run -p 8080:8000 open-public-transport
```

### Usage (docker deployment)

Run this command to deploy the Docker image to Google Cloud.

```shell
gcloud auth login
gcloud config set project open-public-transport
gcloud builds submit --tag gcr.io/open-public-transport/open-public-transport-backend
```

## Fix graphml files

In some occasions graphml files created by peartree cannot be loaded since their IDs have a weird format, such as _

```shell
cd results/results/<CITY>/graphs/peartree
sed -E -i '.bak' 's/\"[A-z0-9 ]+[_de]+([0-9]*):*([0-9]*):*([0-9]*):*([0-9]*):*([0-9]*)[_G]*\"/\1\2\3\4\5\"/g' <GRAPH_FILE>
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
