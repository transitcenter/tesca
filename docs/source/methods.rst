Methods
=======

The TransitCenter Equity Scenario Comparison Application (TESCA) compares public
transit accessibility to important destinations —like employment, healthcare,
supermarkets, and more — for people of different demographics, given a change in
public transit service in a specific region.

Specifically, TESCA is designed to allow for the comparison of the distributive
accessibility to opportunities between two transit network scenarios. Examples of the
types of scenario comparisons include:

* A current and proposed transit network
* Two times of day or days of the week for the same transit network
* Two different sets of available modes (e.g. to model disruptions)

What is Accessibility?
^^^^^^^^^^^^^^^^^^^^^^

**Accessibility** represents the ease with which people can reach the places
they want and need to go. Accessibility is a function of transportation and land
use (where essential destinations are located). Access to opportunities
measures, which represent the ease of reaching a specific type of destination,
are a commonly used measure of accessibility. TESCA evaluates access to
opportunity on public transit based on the supplied set of opportunities. Common
examples of opportunities are jobs, supermarkets, and healthcare services.

Measures of public transit accessibility can capture many characteristics of
transit systems that affect people's ability to reach their destinations,
including the location of stops and routes, what kinds of destinations can be
reached on those routes, the speed or directness of routes, the frequency of
service, fares, and time spent walking to and from a transit stop or
transferring between routes. TESCA estimates transit accessibility by
calculating transit travel times to the locations of destinations across each
region.

How Does TESCA Compute Accessibility?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Transit travel times between census block groups in each region are estimated
using the `R5 engine built by Conveyal <https://github.com/conveyal/r5>`_. R5
uses a detailed pedestrian network from `OpenStreetMap
<https://www.openstreetmap.org/>`_ (OSM). Transit schedules are represented by
`General Transit Feed Specification <https://gtfs.org/>`_ (GTFS) data for transit operators in each
region. These GTFS data are obtained from TransitLand and OpenMobilityData.
Transit travel times are capped at 120 minutes and include all parts of a
door-to-door trip, including time walking to and from a transit stop, time spent
waiting for a transit vehicle, time spent traveling in vehicle(s), and time
spent transferring between transit vehicles.

TESCA combines transit travel times and the location of these destinations to
estimate how many destinations can be reached in a certain amount of time, e.g.
jobs reachable within 30 minutes. These types of accessibility measures are
estimated for the provided destination types. TESCA also allows a user to
retrieve job counts by block group as a starting point for destinations.

TESCA also allows an analyst to estimate travel times to reach a certain number
of opportunities, e.g. travel time in minutes to one hospital or to three
hospitals. The travel time to one hospital reflects the minimum possible time to
reach a hospital. The travel time to three hospitals measures travel time to the
third-closest hospital, capturing people's need for options, where the closest
hospital may not match someone's needs in terms of the cost or type of care
provided. Users can specify which method to use (cumulative or travel time) when
running an analysis.

**Equity indicators** are computed for a defined area in the study region, and
summarize population-weighted access for groups of people, weighting these
outcomes based on where group members live across the chosen impact area. Data
on race and ethnicity, income level, and zero-car households are obtained from
the 2021 five-year American Community Survey data from the US Census.

TESCA follows an approach similar to that of the `TransitCenter Equity Dashboard
<https://dasboard.transitcenter.org>`_, and you can read a detailed methodology
of the dashboard's construction in `this document
<https://transitcenter.org/wp-content/uploads/2021/07/TransitCenterEquityDashboardTechDocumentation_062421.pdf>`_
(PDF). More detail on the code and structure of the applicaiton can be found in
the :ref:`developer reference <devref>` section.

Acknowledgements
^^^^^^^^^^^^^^^^

TESCA was built by `Klumpentown Consulting <https://www.klumpentown.com/>`_ and
relies on a number of open-source libraries and datasets, including
OpenStreetMap, US Census data, and avaialble public transit feeds.