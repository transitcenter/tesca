Glossary 
========

.. glossary:: 
    
    analysis area
        A list of :term:`block groups<block group>` that constitute the broader 
        area of analysis. This list of block groups is used to compute the 
        travel time matrices and access scores. Often, the analysis area may be 
        defined as a Metropolitan Statistical Area (MSA) for a given city.

    block group
        The base unit of analysis in TESCA. Block groups are small geographic
        areas that contain a relatively stable number of residents. We use the
        centroids of block group areas as our representative origins and
        destinations. Block groups are defined in the census as a 12-digit
        string of numbers (e.g. ``"100030029004"``)

    GTFS
        GTFS data, or *General Transit Feed Specifciation* data, is the standard
        way that transit agencies distribute their bus schedules, and is needed
        to conduct any transit-based analysis. GTFS files can be downloaded from
        agency websites, or via an aggregator such as `Transitland
        <https://www.transit.land/>`_.

    impact area
        A list of :term:`block groups<block group>` that constitutde the specific
        area of impact over which to study the differences in scores for various
        populaiton groups between the two scenarios. Impact areas must be a subset
        of the analysis area (it could be the entire analysis area).

    opportunities
        Destinations that individuals may travel to in their day-to-day. They
        can be abstract such as "jobs", or can be concrete and specific such as
        "hospitals".