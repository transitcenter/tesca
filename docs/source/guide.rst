Running an Analysis
===================

In this guide, we'll walk through how to set up a basic analysis, configure it
to your liking, run and understand the validation outputs, run the analysis, and
view and understand the results.


Basic Workflow
--------------
Performing a successful analysis requires completing the following four to five
steps:

1. Download, prepare, and assemble the appropriate datasets
2. Upload an opportunities dataset and configure the analysis
3. Run the data validation and interpret the validation results
4. Run the analysis and interpret the analysis results
5. (Optional) Create your own additional visualizations and plots

Step 1: Assembling and Preparing Data
-------------------------------------

While TESCA is designed to automatically fetch as much data as possible, there
are a few datasets that you will need to define, assemble, and prepare yourself
for the analysis to succeed. Details on obtaining and structuring these data can
be found below, but here's a summary:

* A list of :term:`block group` IDs that define the :term:`analysis area`.
* A list of :term:`block group` IDs that define the :term:`impact area`.
* A set of one or more :term:`opportunities` for each of the block groups defined in the :term:`analysis area`
* A PBF extract of :term:`OpenStreetMap` that covers the :term:`analysis area`.
* Two sets of one or more :term:`GTFS` files. These "sets" could be identical
  (e.g. if two time periods for the same dataset is being studied)

Analysis Area Block Groups
^^^^^^^^^^^^^^^^^^^^^^^^^^
Often, :term:`analysis areas<analysis area>` are defined at the county level.
For example, a study that includes the `Metropolitan Statistical Area (MSA) of
Baltimore <https://en.wikipedia.org/wiki/Baltimore_metropolitan_area>`_ would need to include block groups in:

* Anne Arundel County
* Baltimore City
* Baltimore County
* Carroll County
* Harford County
* Howard County
* Queen Anne's County

TESCA provides a specific helper function to download block group data county by
county. The `Get Block Groups </counties>`_ page provides a tool to select a
list of counties (in multiple states if needed) and generate block group level
data for those regions.

Analysis areas don't have to include all block groups in a county.

Impact Areas
^^^^^^^^^^^^
Deciding on an appropriate :term:`impact area` is dependent on the desired scope
of the study, and is very context dependent. For example, you may be interested
in the impact across a very small area of the larger city, or want to
specifically look at areas nearby a transit network that has changed. If your
impact area is purely county-based, you can download a list of block groups for
the counties you'd like using the `Get Block Groups </counties>`_ page.
Remember, the list of block groups in the impact area must be a subset of the
analysis area, meaning that there can be no block groups in the impact area that
do not appear in the analysis area.

Some potential impact area approaches are:

* A subset of counties representing a more urban (or rural, or suburban) portion
  of the analysis area
* A set of block groups near a transit stop (e.g. within 1/2 mile). Computing
  this requires GIS software such as QGIS.
* A set of block groups representing communities specifically impacted by the
  change or comparison. For example, if a schedule or route change is planned
  specificaly to improve access for select neighborhoods.

Opportunity Data
^^^^^^^^^^^^^^^^

Opportunities come in many forms, and TESCA allows you to analyze access to
basically any opportunity you can find data on. Common opportunities include the
ones used in the `TransitCenter Equity Dashboard
<https://dashboard.transitcenter.org/>`_, such as jobs, supermarkets, and
hospitals. Good places to look for opportunity data include:

* The US Census (e.g. for job counts).
* A city's Open Data portal (e.g. for city amenities such as parks or libraries)
* OpenStreetMap.

Often, you will need to spatially join your opportunities dataset with the
:term:`analysis area` you are using. This can be done using GIS software such as
QGIS. Your final opportunities dataset must include the following:

* A ``bg_id`` column containing block groups for **all** analysis area zones, 
* A column for each opportunity type (these don't have to be pretty, you will
  have a chance to give them a title later).

.. important::
    Your opportunities file must have a row for each block group in the 
    :term:`analysis area`, even if there are no opportunities there. This can be 
    accomplished by filling in empty block groups with zeroes.

OpenStreetMap Data
^^^^^^^^^^^^^^^^^^

OpenStreetMap is an open-source mapping dataset that provides the underlying
street network needed to compute how long it takes to walk to transit stops,
transfer, and reach a destination. While there are some places that provide
up-to-date extracts of major US cities, the best way to ensure you are getting
the appropriate data coverage is to produce a custom extract from the website
`BBBike <https://extract.bbbike.org/>`_.

Here's how it works:

1. Visit `<https://extract.bbbike.org/>`_.
2. Choose ``Protocolbuffer (PBF)`` from the 'Format' drop-down.
3. Type the name you'd like to give to the area you're extracting.
4. Enter your e-mail address to receive a notification when the data is ready.
5. Move the map on the right to your desired location, and click the ``here``
   button to create a box
6. Roughly adjust the box to cover most of the area you need. Clicking on the
   box will make it blue, and you can drag the orange circles around to adjust
   the shape.
7. Choose the "add points to the polygon" radio button on the left and adjust
   the shape of the rectangle to encompass the boundary of your :term:`analysis
   area`.
8. When you are ready, click the big **extract** button. You will be taken to a
   status page where you can watch as your file is queued for extraction. You
   will receive an email when the extraction is done, and you can follow that
   email's instructiosn to download your ``.pbf`` file.
9. Rename the file you just downloaded to ``osm.pbf``.

.. image:: _static/bbbike.png
  :width: 900
  :alt: A polygonal extract of OpenStreetMap around Indanapolis, Indiana using BBBike.org
  
*A polygonal extract of OpenStreetMap data for Indianapolis, Indiana.*


GTFS Data
^^^^^^^^^
Transit scheduled data can typically be obtained directly from the website of
the transit agency. Additionally, there are websites which host :term:`GTFS` datasets
across the world. Some examples are:

- The MobilityData `Mobility Database <https://database.mobilitydata.org/>`_
- `TransitLand <https://www.transit.land/>`_

To run a comparative transit analysis, you will want to include all the relevant
transit agencies in the analysis area to ensure that the routing calcualtions
consdier all available options.

You will need to assemble two sets of transit schedule data representing the
networks for the two scenarios. If you are comparing the same network across
departure times, you can simply make a copy of the set (or upload the same set
twice when the time comes).

Step 2: Starting and Configuring the Analysis
---------------------------------------------

Analyses can be started by visiting the `home page </>`_ of TESCA. To get
started, upload the :term:`opportunities` file prepared as described in the
`opportunity data`_ section above. This opportunities file not only defines the
:term:`analysis area`, it also provides the destinations that will be studied in
the analysis.

Click the ``Browse...`` button and select the file containing the opportunities,
and click ``Start``. TESCA will fetch the appropriate geospatial data to start
the analysis.

.. note:: 
  Please be patient. You will see a spinning or busy indicator in the tab for
  TESCA as it performs the work. It shouldn't take more than a couple of minutes
  to fetch the appropriate data, depending on the size of the area you are
  studying.

Next, you will be presented with a configuration page, starting with a map of
the uploaded block group centroids, which are used as the origin and destination
points for the travel times in TESCA. On this page you can enter relevant
information about the analyst, project, and organization running the analysis,
label and set parameters for the opportunities, upload :term:`impact area` and
:term:`OpenStreetMap` data, configure the scenarios, and provide GTFS data for
the scenarios.

In the following subsections we will walk through each input field and explain
its meaning, where relevant information will appear in the final report, what
specific type of information you need to provide, and some hints for choosing
parameters and writing descriptions. 

.. hint:: 

  To better see where each field might appear in the final report, you can
  download an :download:`annotated example report <example_report.pdf>`. Each
  field is highlighted in the PDF and labelled with the appropriate field name.

Analysis Details
^^^^^^^^^^^^^^^^

* The ``Analyst Name`` (required) field should contain your name and will be repeated in
  the "notes" section of the final report.
* The ``Project Title`` (required) field specifies the specific project or initative you are
  studying. In the ,
  the project name is used in various places to refer to the project as a whole.
* The ``Project Description`` (optional) is where you can describe in more detail about the
  specific project. This will be included in the introductory section describing
  the details of the project. 
  
  .. hint::

    Some potential things to include in the project description are the location of the analysis (e.g.
    Philadelphia MSA) and the rationale or reasoning for the study (e.g. a
    proposed network redesign).

File Inputs
^^^^^^^^^^^

* Upload :term:`OpenStreetMap` data (required) by browsing to the appropriate ``osm.pbf``
  file extracted as described in the `OpenStreetMap data`_ section.
* Upload the list of block groups in CSV format (required) defining the :term:`impact
  area`. See the `impact areas`_ section for details.

Opportunity Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^
A sub-form is provided for each column in the opportunities dataset. The title
of each opportunity form matches the column titles provided in the uploaded CSV.

* The ``Opportunity Name`` (required) field specifies the display name of the
  opporutnity. The name you provide should be able to be read in the sentence:
  ``Access to <opportunity>`` (e.g. "Access to Employment", or "Access to
  Hospitals"). This field will be auto-populated with the column name provided,
  but should be changed.
* The ``Opportunity Description`` (required) allows you to describe the
  destination or opportunity in more detail.

  .. hint::
    
    Some potential things to include here are the specific reasons for including
    the opportunity, or any caveats in the data (e.g. data coverage liminations).

  .. note::
    
    Employment columns labelled with ``C000`` are auto-populated with a description
    provided by TESCA. You can edit this description if you like.

* The ``Computation Method`` drop-down field lets you choose between
  cumulative and travel time methods of calculating access to that specific
  opportunity. Cumulative measures compute the number of total destinations
  reachable in the specified number of travel minutes, while travel time
  measures compute the time taken to reach the nth closest (e.g. 1st closest
  and 3rd closest) destination of that type.

  .. hint::

    Generally speaking, cumulative measures are useful for "distinguishable"
    destinations, such as jobs or park space, or where it is understandable
    that having access to *more* of that opportunity provides a benefit. For
    example, being able to access more jobs or more park space in 30 minutes
    by transit is generally more desirable.

    Travel time measures are useful when the key is only to reach the nearest
    destination (e.g. hospitals) or when choice is less of a factor.
    Sometimes, striking a balance between choice and proximity is useful: For
    example, measuring the travel time to the third nearest supermarket
    implies that an individual might want some choice in where they shop,
    either for price or food selection reasons. However, computing the total
    number of supermarkets reachable in 30 minutes is not as useful a measure.

* The ``Unit of Measure`` (required) is the name of the unit for what you are
  measuring. For example, access to employment would have a unit of "jobs",
  while access to acres of park space might have a unit of "acres"

  .. note::
    
    If you select a travel time measure in the previous column, you should specify
    minutes, as travel time will always have a unit of minutes in TESCA. If you
    provide a different unit, it will be overwritten with "minutes" once you finish
    the configuration step. Due to a quirk in the software, you will have to specify
    *something* here as it cannot be left blank.

* The ``Parameters`` (required) field should contain a comma-separated list of
  parameters for the corresponding method. For cumulative measures, specify the
  travel time cutoffs you want to use (e.g. 30 and 45 minutes would be
  ``30,45``), and for travel time measures specified the *n* in "nth closest"
  (e.g. ``1,3`` will compute travel times to the closest and 3rd closest
  opportunity).

  .. hint::

    While the choice of parameter is entirely up to you, it is common practice
    to use multiples of 15 minutes (e.g 15, 30, 45, 60 minutes) for cumulative
    measures. When choosing these parameters, consider how far someone might be
    willing to travel for that particular opportunity. For example, it is likely
    that an individual will travel farther for job opportunities than for park
    space, so employment may want to have higher parameters than park space in
    that particular instance.

    For travel time measures, you can specifiy any *n* you would like, but keep
    in mind that the intention of the travel time measure is to provide an
    alternative to the "how many can I reach?" question that is asked by the
    cumulative measure. Higher values will therefore provide diminishing returns
    on clarity and interpretability.

Scenario Definitions
^^^^^^^^^^^^^^^^^^^^
In this section you will be presented with two sub-forms, one for each scenario.
They are labelled "Scenario 0" and "Scenario 1".

* The ``Scenario Name`` (required) field should contain the name of the scenario
  (e.g. "Business as Usual" or "Proposed Redesign"). These are used to label the
  scenarios in the resulting charts, so short and concise names are typically
  better.
* The ``Scenario Description`` (required) field should contain information about
  the particular scenario. These are used to populat the scenario details
  information in the final report.
* The ``Start Date & Time`` (required) field allows you to select a start date
  and time for the analysis. Use the calendar selection widget to choose the
  approprate start time.
  
  .. important::

    The start date and time should be within the coverage of the provided
    transit schedule data. Check the ``calendar.txt`` and ``calendar_dates.txt``
    files in the GTFS data you are using to make sure they cover the desired
    date and time.

* The ``Duration`` (required) field specifies the total number of minutes after
  the ``Start Date & Time`` to examine. To account for the fact that transit
  schedules and routes may run at different times and frequencies, the analysis
  will compute the travel times for each minute following the ``Start Date &
  Time`` for the number of minutes specified in ``Duration``, and use the median
  travel time value as the representative value. This is done as best practice
  to account for variations in departure time. A default value of 120 minutes (2
  hours) provides a broad coverage of a typical travel period (e.g. morning rush
  hour).

* The ``Transit Modes`` (required) selection allows you to specify specific
  modes of transit to use in the analysis. You can select multiple options by
  shift-clicking or control-clicking. If "all modes" is part of the selection,
  all modes will be used regardless of the others chosen.

  .. hint::

    Typically, "all modes" is the appropriate choice to use for an analysis, but
    you can specificy specific modes if you would like to see the impact on
    access between modes (e.g. what would happen to access if the subway system
    shut down in New York City?). These provided modes are `specified
    <https://gtfs.org/schedule/reference/#routestxt>`_ in the ``route_type``
    column of the ``routes.txt`` file of a GTFS set.

* The ``GTFS Files`` (required) input allows you to upload multiple GTFS
  datasets that make up the transit network representing the particular
  scenario.

Once you have completed the form and provided the appropriate input data you can
click the ``Set Up Analysis and Validate`` button to proceed to the validation
stage.

.. important:: 

  After completing this step you will be uploading large files (GTFS files and
  OpenStreetMap data). Depending on the speed of your internet connection and
  the size of the study area this may take upwards of 10+ minutes to upload.
  Please be patient as the files upload (you will see a busy icon in the browser
  tab).

Step 3: Data Validation
-----------------------

After the configuration page is submitted, you will be presented with a running
log of the actions that TESCA is taking. Specifically, TESCA will do the
following:

1. Perform data validation checks on the opportunities, analysis areas, and impact areas provided.
2. For each GTFS feed:
   
  a. Run the `MobilityData GTFS Validator
     <https://gtfs-validator.mobilitydata.org/>`_ on the GTFS file and summarize
     the number of errors, warnings, and information comments provided the
     validator before saving the results.
  b. Check the date of analysis against the data coverage of the GTFS feed.

Once the validation checks are complete two buttons will appear:

* ``Run Analysis`` will start the analysis run and take you to the run tracking page.
* ``View GTFS Validation Reports`` will bring you to a summary page showing the
  number of infos, warnings, and errors for each of the provided GTFS feeds for
  both scenarios. From here you can view the report generated by the
  MobilityData GTFS Validator.
  
  .. hint::

    You can see a list of the rules that are checked and what they mean on the
    `MobilityData website
    <https://gtfs-validator.mobilitydata.org/rules.html>`_. Note that not all
    errors and warnings are relevant to the ability of TESCA to generate useful
    results. Errors and warnings specifically around network elements
    (impossible travel times, missing route or schedule data) are the main
    issues to look out for. If the generated results have potential issues, this
    is a good place to diagnose things.

One you have examined the validation log and are happy with the validation
reports you can click ``Run Analysis`` to start the main analysis portion.


Step 4: Analysis Run and Results
--------------------------------

Once you have submitted the start of the analysis you will be presented with a
page showing live updates of the progress on the run. This includes a log that
explains what step the analysis is on. At a higher level, the analysis needs to
perform the following steps *for each scenario*:

* Build a transport network that includes all the transit schedule data
* Compute a transit travel time matrix from each block group centroid to each
  other block group centroid
* Use the resulting travel time matrix to compute access to opportunity metrics

Once this is done, TESCA will use the results to compute a comparison of the two
scenarios, and to compute a population-group-weighted summary of each access to
opportunity metric. These are the scores reported in the charts in the final report.

TESCA will also compute, for each travel time measure and parameter, the number
of individuals in each population group who cannot reach the specified number of
destinations at all (e.g. cannot reach 3 hospitals).

Editing Results
^^^^^^^^^^^^^^^

There are a number of spaces in the report that you can use to add context or
adjust the langauge you provided in the configuration page. Use the blue button
at near the top of the report to toggle "edit mode" on and off. Places where
text boxes appear can be edited. Once you are ready to create a PDF/print the
report you can toggle edit mode "off" and see your changes reflected.

.. note:: 

  At this time, only a single "line" of text is possible (i.e. no paragraph breaks
  will be captured) in any of the editable boxes. Also, when you refresh the page
  **any changes you made will be reverted**.