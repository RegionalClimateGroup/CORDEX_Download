# CORDEX_Download
Routines to download CORDEX data for limited extents using opendap.

- download limited extents: get only the data for the area you are interested in. Greatly reduces the file sizes!
- automatic concatenation of files, you get one NetCDF file for each variable/simulation (rather than one for for each year or 5 years). So much easier to load into your analysis package!

#### Contact: 

David Rayner, Department of Earth Science, University of Gothenburg
David.Rayner@gu.se

### What you will need:

```
import json
import os
import re

from netCDF4 import Dataset
import numpy as np
from pydap.client import open_url
from pydap.cas.esgf import setup_session
from siphon.catalog import TDSCatalog
import xarray as xr
```

In addition, you must rename config_RENAME_ME.py to config.py and add your openid! Also, configure the tmpdirname variable in config.py

### What else you will need:

An openid so you can download data from https://esg-dn1.nsc.liu.se/projects/esgf-liu/ There must be instructions, I'm sure you can find them...

Note: Before you can download anything with opendap you need to be a member of a group, accept terms and conditions etc. In short: download a file through the web-browser first, <u>then</u> try to download it with CORDEX_Download!

### And there's more:

You need to get a list of the data you want to download! https://esg-dn1.nsc.liu.se/projects/esgf-liu/ and select down to the datasets you want, then click "return results as JSON"

![](GetJSON.PNG)



### Basic usage:

#### Download and concatenate:

With your config.py edited, try running CORDEX_download_Example.py

The basic usage is:
```python
# ~Norden in EU11
rlat_idx=slice(250,391)
rlon_idx=slice(198,286)

p=JSONParser(ModelSelectionFilename)
ConcatenatedCatalogSlice(p.Catalog, OutputDir , rlat_idx, rlon_idx, retain_raw_files=False)
```

#### Download from a single URL for test purposes:

Note that the grid extent is defined in rotated coordinates, so it might take a bit of trial-and error to download the sub-grid you want. Also, I don't think all models for a given CORDEX domain use the same grid extent, so you may need different extents for different RCMs!

If you want to test extents, you can download just data from a single url by editing the JSONParser output:

```python
p=JSONParser(ModelSelectionFilename)

catalog = p.Catalog[0]

catalog.datasets = [catalog.datasets[0],]
```

...and then download just that catalog...

```
DownloadCatalogSlice(catalog,...
```

... then open the nc file that is created and check it out!

#### Possible developments:

If you want to download just a few pixels from lots of models, you can build on the DownloadPoints function. No support for concatenation or reading a JSON file, but you give it latitude and longitudes, not grid coordinates. 

### Acknowledgements:

This package was developed within projects supported by the funding grants:

Formas 2016-01061. Realistic local climate change time-series matched to climate policy goals (eg 1.5 °C).
Formas 2018-02812. The influence of warm weather and outdoor-environment design on preschoolers’ physical activities and thermal comfort.

Development was enabled by resources provided by the Swedish National Infrastructure for Computing (SNIC) at NSC, Linköping University, partially funded by the Swedish Research Council through grant agreement no. 2018-05973.