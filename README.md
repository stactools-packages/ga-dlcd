# stactools ga-dlcd

The Dynamic Land Cover Dataset uses a standard land cover classification to show the change in behaviour of land cover across Australia. The DLCD includes data for every 250m by 250m area on the ground, for the period 2001 to 2015. The DLDC provides a basis for reporting on change and trends in vegetation cover and extent. Information about land cover dynamics is essential to understanding and addressing a range of national challenges such as drought, salinity, water availability and ecosystem health (Lymburner, L et al., 2014). 

## Usage

1. As a python module

```python
from stactools.ga-dlcd import cog, stac

# Create a STAC Collection
json_path = os.path.join(tmp_dir, "/path/to/collection.json")
stac.create_collection(metadata, json_path)

# Create a COG
cog.create_cog("/path/to/local.tif", "/path/to/cog.tif")

# Create a STAC Item
stac.create_item("/path/to/item.json", "/path/to/cog.tif")
```

2. Using the CLI

```bash
# STAC Collection
stac ga-dlcd create-collection -d "/path/to/directory"
# Create a COG - creates /path/to/local_cog.tif
stac ga-dlcd create-cog -d "/path/to/directory" -s "/path/to/local.tif"
# Create a STAC Item - creates /path/to/directory/local_cog.json
stac ga-dlcd create-item -d "/path/to/directory" -c "/path/to/local_cog.tif"
```

### References

1. Lymburner, L., Tan, P., McIntyre, A., Thankappan, M., Sixsmith, J. 2014. Dynamic Land Cover Dataset Version 2.1. Geoscience Australia, Canberra. http://pid.geoscience.gov.au/dataset/ga/83868   
