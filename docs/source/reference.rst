Developer Reference
===================

Configuration Files
###################
Configuration files




Running an Analysis Without Interface
-------------------------------------

Data Inputs
^^^^^^^^^^^

In order to run an analysis without the user interface, you will need to assemble much of the data sources yourself. A folder needs to be created in the `cache` directory which represents an individual project. Here's what your initial folder structure should look like::

    cache
    ├── example-analysis
    │    ├── analysis_centroids.geojson
    │    ├── analysis_polygons.geojson
    │    ├── config.yml
    │    ├── demographics.csv
    │    ├── gtfs0
    │    │    ├── cta.zip
    │    │    └── metra.zip
    │    ├── gtfs1
    │    │    ├── cta.zip
    │    │    └── metra.zip
    │    ├── impact_area.csv
    │    ├── opportunities.csv
    │    ├── osm.pbf


Here's a description of each file:

- ``analysis_centroids.geojson`` contains geospatial point data of the representative centers or centroids of the block group zone. 
- ``analysis_polygons.geojson`` contains geospatial area data of the block group zones. This file should contain an ``id`` column with block group IDs.
- ``config.yml`` is the configuration file which contains all of the parameters of the analysis. You can read more about that ``INSERT_LINK_TO_FILE``
- ``demographics.csv`` (optional) contain the demographic counts of the population groups used in the analysis. These should correspond to the demogrpahic keys listed in the configuration file, and should span all impact area zones. This file should contain a ``bg_id`` column along with a column for each demographic group matching the keys provided in the configuration file. The data for this file can be fetched automatically from the Census API.
- ``gtfs0`` is a folder containing all of the ``.zip`` files of all GTFS data used for Scenario A analysis.
- ``gtfs1`` is a folder containing all of the ``.zip`` files of all GTFS data used for Scenario B analysis.
- ``impact_area.csv`` is a file containing a single column (``bg_id``) with block group defintions for the impact area
- ``opportunities.csv`` is a file containing a ``bg_id`` column containing block groups for all analysis area zones, and a column for each opportunity type matching the opportunity keys in the configuration file.
- ``osm.pbf`` is the OpenStreetMap PBF file spanning the analysis area.

Setting Up The Analysis
^^^^^^^^^^^^^^^^^^^^^^^

You will need to set up the ``config.yml`` file with the appropriate parameters. Here's an example file you can work from.

.. literalinclude:: example_config.yml
    :language: yaml

Analysis
########
.. automodule:: tesca.analysis
   :members: