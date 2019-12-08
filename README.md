# EISGIS
Democracy Fund Supported GIS election management

# Objective

This project’s objective is for the contractor (Election Information Services, Inc.) to create a suite of open source geospatial tools designed specifically for local and state election administration officials that will validate current electoral district and precinct assignments from address data and district definitions provided by the election administrators and from other sources.  This tool set will be made available to all state and local election officials and will allow for the uploading/processing of address data and ESRI shape files.  The tool will create reports of apparent mismatches of voter district assignments and be able to generate visualizations of assignment anomalies.

# Deliverables

The Voter GIS Audit tool will be made available local and state election administrators at no cost.  It will consume address and district data from the voter registration management system in a standardized (VRI) format.  Voter GIS Audit staff will be available to provide assistance to election officials in generating the appropriate export formats.

The Voter GIS Audit tool will be able to consume geospatial objects in a number of formats.  It will use open source geospatial programming to determine the associations between voter addresses and address ranges and district boundaries.

The Voter GIS Audit tool will provide its users with several interfaces that allow the importing/loading of voter registration data and GIS files.  

Once all voter address data and geospatial boundaries are loaded then the Voter GIS Audit tool will transform the uploaded address data into GIS objects. 

The Voter GIS Audit tool will programmatically compare the addresses and calculate the intersections with the provided district boundaries.  The Voter GIS Audit tool will rely on the U.S. Census Bureau's TIGER/Line files to assist in geocoding and to associate boundaries with the respective geographic entity codes.

The Voter GIS Audit tool will allow for the export of addresses and district associations for audit purposes.   

Once the election official has audited the data, the Voter GIS Audit service will create a standardized data extract that can be returned to the voter registration database with updated precinct split and district assignments.
