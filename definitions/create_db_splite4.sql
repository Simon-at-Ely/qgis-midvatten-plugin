﻿# -*- coding: utf-8 -*- This line is just for your information, the python plugin will not use the first line
select 'drop table ' || name || ';' from sqlite_master where type = 'table';
select InitSpatialMetadata(1);
create table about_db ("table" text, "column" text, "data_type" text, "not_null" text, "default_value" text, "primary_key" text, "foreign_key" text, "description" text, "upd_date" text, "upd_sign" text);
insert into about_db values('*', '*', '', '', '', '', '', 'This db was created by Midvatten plugin CHANGETOPLUGINVERSION, running QGIS version CHANGETOQGISVERSION on top of SpatiaLite version CHANGETOSPLITEVERSION', '', '');
insert into about_db values('about_db', '*', '', '', '', '', '', 'A status log for the tables in the db', '', '');
insert into about_db values('about_db', 'table', 'text', '', '', '', '', 'Name of a table in the db', '', '');
insert into about_db values('about_db', 'column', 'text', '', '', '', '', 'Name of column', '', '');
insert into about_db values('about_db', 'upd_date', 'text', '', '', '', '', 'Date for last update', '', '');
insert into about_db values('about_db', 'upd_sign', 'text', '', '', '', '', 'Person responsible for update', '', '');
insert into about_db values('about_db', 'contents', 'text', '', '', '', '', 'Contents', '', '');
insert into about_db values('meteo', '*', '', '', '', '', '', 'meteorological observations', '', '');
insert into about_db values('meteo', 'obsid', 'text', '1', '', '1', 'obs_points(obsid)', 'obsid linked to obs_points.obsid', '', '');
insert into about_db values('meteo', 'instrumentid', 'text', '1', '', '1', '', 'Instrument Id, may use several different temperature sensors or precipitaion meters at same station', '', '');
insert into about_db values('meteo', 'parameter', 'text', '1', '', '1', 'zz_meteoparam(parameter)', 'The meteorological parameter, e.g. precipitation, temperature etc', '', '');
insert into about_db values('meteo', 'date_time', 'text', '1', '', '1', '', 'Date and Time for the observation, on format yyyy-mm-dd hh:mm:ss', '', '');
insert into about_db values('meteo', 'reading_num', 'double', '', '', '', '', 'Value (real number) reading for the parameter', '', '');
insert into about_db values('meteo', 'reading_txt', 'text', '', '', '', '', 'Value (text string) reading for the parameter', '', '');
insert into about_db values('meteo', 'unit', 'text', '', '', '', '', 'Unit corresponding to the value reading', '', '');
insert into about_db values('meteo', 'comment', 'text', '', '', '', '', 'Comment', '', '');
insert into about_db values('obs_points', '*', '', '', '', '', '', 'One of the two main tables. This table holds all point observation objects.', '', '');
insert into about_db values('obs_points', 'obsid', 'text', '1', '', '1', '', 'ID for the observation point, eg Well01, Br1201, Rb1201', '', '');
insert into about_db values('obs_points', 'name', 'text', '', '', '', '', 'Ordinary name for the observation, e.g. Pumping well no 1, Brunn 123, Flow gauge A, pegel 3 etc ', '', '');
insert into about_db values('obs_points', 'place', 'text', '', '', '', '', 'Place for the observation. E.g. estate, property, site', '', '');
insert into about_db values('obs_points', 'type', 'text', '', '', '', '', 'Type of observation', '', '');
insert into about_db values('obs_points', 'length', 'double', '', '', '', '', 'Borehole length from ground surface to bottom (equals to depth if vertical)', '', '');
insert into about_db values('obs_points', 'drillstop', 'text', '', '', '', '', 'Drill stop, e.g. probing/direct push drilling stopped against rock', '', '');
insert into about_db values('obs_points', 'diam', 'double', '', '', '', '', 'Inner diameter for casing or upper part of borehol', '', '');
insert into about_db values('obs_points', 'material', 'text', '', '', '', '', 'Well material', '', '');
insert into about_db values('obs_points', 'screen', 'text', '', '', '', '', 'Type of well screen, including description, e.g. 1 m Johnson Well Screen 2,5mm ', '', '');
insert into about_db values('obs_points', 'capacity', 'text', '', '', '', '', 'Well capacity', '', '');
insert into about_db values('obs_points', 'drilldate', 'text', '', '', '', '', 'Date when drilling was completed', '', '');
insert into about_db values('obs_points', 'wmeas_yn', 'integer', '', '', '', '', '1/0 if water level is to be measured for this point or not', '', '');
insert into about_db values('obs_points', 'wlogg_yn', 'integer', '', '', '', '', '1/0 if water level if borehole is equipped with a logger or not', '', '');
insert into about_db values('obs_points', 'east', 'double', '', '', '', '', 'Eastern coordinate (in the corresponding CRS)', '', '');
insert into about_db values('obs_points', 'north', 'double', '', '', '', '', 'Northern coordinate (in the corresponding CRS)', '', '');
insert into about_db values('obs_points', 'ne_accur', 'double', '', '', '', '', 'Approximate inaccuracy for coordinates', '', '');
insert into about_db values('obs_points', 'ne_source', 'text', '', '', '', '', 'Source for the given position, e.g. from an old map or measured in field campaign', '', '');
insert into about_db values('obs_points', 'h_toc', 'double', '', '', '', '', 'Elevation (masl) for the measuring point, the point from which water level is measured, normally Top Of Casing', '', '');
insert into about_db values('obs_points', 'h_tocags', 'double', '', '', '', '', 'Distance from Measuring point to Ground Surface (m), Top Of Casing Above Ground Surface', '', '');
insert into about_db values('obs_points', 'h_gs', 'double', '', '', '', '', 'Ground Surface level (m). ', '', '');
insert into about_db values('obs_points', 'h_accur', 'double', '', '', '', '', 'Inaccuracy (m) for Measuring Point level, h_toc', '', '');
insert into about_db values('obs_points', 'h_syst', 'text', '', '', '', '', 'Reference system for elevation', '', '');
insert into about_db values('obs_points', 'h_source', 'text', '', '', '', '', 'Source for the measuring point elevation (consultancy report or similar)', '', '');
insert into about_db values('obs_points', 'source', 'text', '', '', '', '', 'The source for the observation point, eg full reference to consultancy report or authority and year', '', '');
insert into about_db values('obs_points', 'com_onerow', 'text', '', '', '', '', 'onerow comment, appropriate for map labels', '', '');
insert into about_db values('obs_points', 'com_html', 'text', '', '', '', '', 'multiline formatted comment in html format', '', '');
insert into about_db values('obs_points', 'geometry', 'BLOB point', '', '', '', '', 'The geometry of OGR/FDO type point', '', '');
insert into about_db values('obs_lines', '*', '', '', '', '', '', 'One of the two main tables. This table holds all line observation objects.', '', '');
insert into about_db values('obs_lines', 'obsid', 'text', '1', '', '1', '', 'ID for observation line, e.g. S1.', '', '');
insert into about_db values('obs_lines', 'name', 'text', '', '', '', '', 'Ordinary name for the observation, e.g. Seismic profile no 1', '', '');
insert into about_db values('obs_lines', 'place', 'text', '', '', '', '', 'Place for the observation', '', '');
insert into about_db values('obs_lines', 'type', 'text', '', '', '', '', 'Type of observation, e.g. vlf, seismics or gpr', '', '');
insert into about_db values('obs_lines', 'source', 'text', '', '', '', '', 'The origin for the observation, eg full reference to consultancy report', '', '');
insert into about_db values('obs_lines', 'geometry', 'BLOB linestring', '', '', '', '', 'The geometry of OGR/FDO type linestring', '', '');
insert into about_db values('seismic_data', '*', '', '', '', '', '', 'Interpreted data from seismic measurements', '', '');
insert into about_db values('seismic_data', 'obsid', 'text', '1', '', '1', 'obs_lines(obsid)', 'obsid linked to obs_lines.obsid', '', '');
insert into about_db values('seismic_data', 'length', 'double', '1', '', '1', '', 'Length along line', '', '');
insert into about_db values('seismic_data', 'ground', 'double', '', '', '', '', 'Ground surface level', '', '');
insert into about_db values('seismic_data', 'bedrock', 'double', '', '', '', '', 'Interpreted level for bedrock surface', '', '');
insert into about_db values('seismic_data', 'gw_table', 'double', '', '', '', '', 'Interpreted level for limit between unsaturated/saturated conditions', '', '');
insert into about_db values('seismic_data', 'comment', 'text', '', '', '', '', 'Additional info', '', '');
insert into about_db values('stratigraphy', '*', '', '', '', '', '', 'stratigraphy information from drillings, probings etc', '', '');
insert into about_db values('stratigraphy', 'obsid', 'text', '1', '', '1', 'obs_points(obsid)', 'obsid linked to obs_points.obsid', '', '');
insert into about_db values('stratigraphy', 'stratid', 'integer', '1', '', '1', '', 'Stratigraphy layer ID for the OBSID, starts with layer 1 from ground surface and increases below', '', '');
insert into about_db values('stratigraphy', 'depthtop', 'double', '', '', '', '', 'Depth, from surface level, to top of the stratigraphy layer', '', '');
insert into about_db values('stratigraphy', 'depthbot', 'double', '', '', '', '', 'Depth, from surface level, to bottom of the stratigraphy layer', '', '');
insert into about_db values('stratigraphy', 'geology', 'text', '', '', '', '', 'Full description of geology', '', '');
insert into about_db values('stratigraphy', 'geoshort', 'text', '', '', '', '', 'Short description of geology, should correspond to the dictionaries used. Stratigraphy plot looks in this field and relates to coded dictionaries with fill patterns and colors.', '', '');
insert into about_db values('stratigraphy', 'capacity', 'text', '', '', '', '', 'Well development at the layer, may also be waterloss or similar. If using notations 1, 2, 3, 4-, 4, and so on until 6+ it will match color codes in Midvatten plugin (see midvatten_defs.py). ', '', '');
insert into about_db values('stratigraphy', 'development', 'text', '', '', '', '', 'Well development - Is the flushed water clear and free of suspended solids? ', '', '');
insert into about_db values('stratigraphy', 'comment', 'text', '', '', '', '', 'Comment', '', '');
insert into about_db values('vlf_data', '*', '', '', '', '', '', 'Raw data from VLF measurements', '', '');
insert into about_db values('vlf_data', 'obsid', 'text', '1', '', '1', 'obs_lines(obsid)', 'obsid linked to obs_lines.obsid', '', '');
insert into about_db values('vlf_data', 'length', 'double', '1', '', '1', '', 'Length along line', '', '');
insert into about_db values('vlf_data', 'real_comp', 'double', '', '', '', '', 'Raw data real component (in-phase(%))', '', '');
insert into about_db values('vlf_data', 'imag_comp', 'double', '', '', '', '', 'Raw data imaginary component', '', '');
insert into about_db values('vlf_data', 'comment', 'text', '', '', '', '', 'Additional info', '', '');
insert into about_db values('w_flow', '*', '', '', '', '', '', 'Water flow', '', '');
insert into about_db values('w_flow', 'obsid', 'text', '1', '', '1', 'obs_points(obsid)', 'obsid linked to obs_points.obsid', '', '');
insert into about_db values('w_flow', 'instrumentid', 'text', '1', '', '1', '', 'Instrument Id, may use several flowmeters at same borehole', '', '');
insert into about_db values('w_flow', 'flowtype', 'text', '1', '', '1', '', 'Flowtype must correspond to type in flowtypes - Accumulated volume, momentary flow etc', '', '');
insert into about_db values('w_flow', 'date_time', 'text', '1', '', '1', 'zz_flowtype(type)', 'Date and Time for the observation, on format yyyy-mm-dd hh:mm:ss', '', '');
insert into about_db values('w_flow', 'reading', 'double', '', '', '', '', 'Value (real number) reading for the flow rate, accumulated volume etc', '', '');
insert into about_db values('w_flow', 'unit', 'text', '', '', '', '', 'Unit corresponding to the value reading', '', '');
insert into about_db values('w_flow', 'comment', 'text', '', '', '', '', 'Comment', '', '');
insert into about_db values('w_levels', '*', '', '', '', '', '', 'Manual water level measurements', '', '');
insert into about_db values('w_levels', 'obsid', 'text', '1', '', '1', 'obs_points(obsid)', 'obsid linked to obs_points.obsid', '', '');
insert into about_db values('w_levels', 'date_time', 'text', '1', '', '1', '', 'Date and Time for the observation, on format yyyy-mm-dd hh:mm:ss', '', '');
insert into about_db values('w_levels', 'meas', 'double', '', '', '', '', 'distance from measuring point to water level', '', '');
insert into about_db values('w_levels', 'h_toc', 'double', '', '', '', '', 'Elevation (masl) for the measuring point at the particular date_time (measuring point elevation may vary by time)', '', '');
insert into about_db values('w_levels', 'level_masl', 'double', '', '', '', '', 'Water level elevation (masl) calculated from measuring point and distance from measuring point to water level', '', '');
insert into about_db values('w_levels', 'comment', 'text', '', '', '', '', 'Comment', '', '');
insert into about_db values('w_levels_logger', '*', '', '', '', '', '', 'Automatic Water Level Readings', '', '');
insert into about_db values('w_levels_logger', 'obsid', 'text', '1', '', '1', 'obs_points(obsid)', 'obsid linked to obs_points.obsid', '', '');
insert into about_db values('w_levels_logger', 'date_time', 'text', '1', '', '1', '', 'Date and Time for the observation, on format yyyy-mm-dd hh:mm:ss', '', '');
insert into about_db values('w_levels_logger', 'head_cm', 'double', '', '', '', '', 'pressure (cm water column) on pressure transducer', '', '');
insert into about_db values('w_levels_logger', 'temp_degc', 'double', '', '', '', '', 'temperature degrees C', '', '');
insert into about_db values('w_levels_logger', 'cond_mscm', 'double', '', '', '', '', 'electrical conductivity mS/cm', '', '');
insert into about_db values('w_levels_logger', 'level_masl', 'double', '1', '-999', '', '', 'Corresponding Water level elevation (masl)', '', '');
insert into about_db values('w_levels_logger', 'comment', 'text', '', '', '', '', 'Comment', '', '');
insert into about_db values('w_qual_field', '*', '', '', '', '', '', 'Water quality from field measurements', '', '');
insert into about_db values('w_qual_field', 'obsid', 'text', '1', '', '1', 'obs_points(obsid)', 'obsid linked to obs_points.obsid', '', '');
insert into about_db values('w_qual_field', 'staff', 'text', '', '', '', '', 'Field staff', '', '');
insert into about_db values('w_qual_field', 'date_time', 'text', '1', '', '1', '', 'Date and Time for the observation, on format yyyy-mm-dd hh:mm:ss', '', '');
insert into about_db values('w_qual_field', 'instrument', 'text', '', '', '', '', 'Instrument ID', '', '');
insert into about_db values('w_qual_field', 'parameter', 'text', '1', '', '1', '', 'Measured parameter', '', '');
insert into about_db values('w_qual_field', 'reading_num', 'double', '', '', '', '', 'Value as real number', '', '');
insert into about_db values('w_qual_field', 'reading_txt', 'text', '', '', '', '', 'Value as text, incl more than and less than symbols', '', '');
insert into about_db values('w_qual_field', 'unit', 'text', '', '', '', '', 'Unit', '', '');
insert into about_db values('w_qual_field', 'flow_lpm', 'double', '', '', '', '', 'Sampling flow (l/min)', '', '');
insert into about_db values('w_qual_field', 'comment', 'text', '', '', '', '', 'Comment', '', '');
insert into about_db values('w_qual_lab', '*', '', '', '', '', '', 'Water quality from laboratory analysis', '', '');
insert into about_db values('w_qual_lab', 'obsid', 'text', '1', '', '', 'obs_points(obsid)', 'obsid linked to obs_points.obsid', '', '');
insert into about_db values('w_qual_lab', 'depth', 'double', '', '', '', '', 'Depth (m below h_gs) from where sample is taken', '', '');
insert into about_db values('w_qual_lab', 'report', 'text', '1', '', '1', '', 'Report no from laboratory', '', '');
insert into about_db values('w_qual_lab', 'project', 'text', '', '', '', '', 'Project number', '', '');
insert into about_db values('w_qual_lab', 'staff', 'text', '', '', '', '', 'Field staff', '', '');
insert into about_db values('w_qual_lab', 'date_time', 'text', '', '', '', '', 'Date and Time for the observation, on format yyyy-mm-dd hh:mm:ss', '', '');
insert into about_db values('w_qual_lab', 'anameth', 'text', '', '', '', '', 'Analysis method, preferrably code relating to analysis standard', '', '');
insert into about_db values('w_qual_lab', 'parameter', 'text', '1', '', '1', '', 'Measured parameter', '', '');
insert into about_db values('w_qual_lab', 'reading_num', 'double', '', '', '', '', 'Value as real number', '', '');
insert into about_db values('w_qual_lab', 'reading_txt', 'text', '', '', '', '', 'Value as text, incl more than and less than symbols', '', '');
insert into about_db values('w_qual_lab', 'unit', 'text', '', '', '', '', 'Unit', '', '');
insert into about_db values('w_qual_lab', 'comment', 'text', '', '', '', '', 'Comments', '', '');
insert into about_db values('zz_flowtype', '*', '', '', '', '', '', 'data domain for flowtypes in table w_flow', '', '');
insert into about_db values('zz_flowtype', 'type', 'text', '1', 'Accvol, Aveflow or Momflow', '1', '', 'Existing types of measurements related to water flow', '', '');
insert into about_db values('zz_flowtype', 'explanation', 'text', '', '', '', '', 'Explanation of the flowtypes', '', '');
insert into about_db values('zz_meteoparam', '*', '', '', '', '', '', 'data domain for meteorological parameters in meteo', '', '');
insert into about_db values('zz_meteoparam', 'parameter', 'text', '1', 'precip, temp', '1', '', 'Existing types of parameter related to meteorological observations', '', '');
insert into about_db values('zz_meteoparam', 'explanation', 'text', '', '', '', '', 'Explanation of the parameters', '', '');
insert into about_db values('zz_strat', '*', '', '', '', '', '', 'data domain for stratigraphy classes, plot colors, symbols and geological short names used by the plugin', '', '');
insert into about_db values('zz_strat', 'strat', 'text', '1', 'gravel, sand, silt, clay etc', '1', '', 'stratigraphy classes', '', '');
insert into about_db values('zz_strat', 'color_mplot', 'text', '1', '', '', '', 'color codes for matplotlib plots', '', '');
insert into about_db values('zz_strat', 'hatch_mplot', 'text', '1', '', '', '', 'hatch codes for matplotlib plots', '', '');
insert into about_db values('zz_strat', 'color_qt', 'text', '1', '', '', '', 'color codes for Qt plots', '', '');
insert into about_db values('zz_strat', 'brush_qt', 'text', '1', '', '', '', 'brush types for Qt plots', '', '');
insert into about_db values('zz_strat', 'geoshorts', 'text', '1', '', '', '', 'list of all possible abbreviations for this stratigraphy class', '', '');
create table "obs_points" ( "obsid" text not null, "name" text, "place" text, "type" text, "length" double, "drillstop" text, "diam" double, "material" text, "screen" text, "capacity" text, "drilldate" text, "wmeas_yn" integer, "wlogg_yn" integer, "east" double, "north" double, "ne_accur" double, "ne_source" text,  "h_toc" double, "h_tocags" double, "h_gs" double, "h_accur" double, "h_syst" text, "h_source" text, "source" text, "com_onerow" text, "com_html" text, primary key (obsid));
SELECT AddGeometryColumn("obs_points", "geometry", CHANGETORELEVANTEPSGID, "POINT", "XY", 0);
create table "obs_lines" ("obsid" text  not null, name text, place text, type text, source text, primary key (obsid));
SELECT AddGeometryColumn("obs_lines", "geometry", CHANGETORELEVANTEPSGID, "LINESTRING", "XY", 0);
create table "w_levels" ("obsid" text not null, "date_time" text not null, "meas" double, "h_toc" double, "level_masl" double, "comment" text, primary key (obsid, date_time),  foreign key(obsid) references obs_points(obsid));
create table "w_levels_logger" ("obsid" text not null, "date_time" text not null, "head_cm" double, "temp_degc" double, "cond_mscm" double, "level_masl" double, "comment" text, primary key (obsid, date_time),  foreign key(obsid) references obs_points(obsid));
create table "stratigraphy" (obsid text not null, stratid integer not null, depthtop double, depthbot double, geology text, geoshort text, capacity text, development text,  comment text, primary key (obsid, stratid), foreign key(obsid) references obs_points(obsid));
create table "w_qual_field" (obsid text not null, staff text, date_time text not null, instrument text, parameter text not null, reading_num double, reading_txt text, unit text, flow_lpm double, comment text, primary key(obsid, date_time, parameter), foreign key(obsid) references obs_points(obsid) );
create table "w_qual_lab" ("obsid" text not null, "depth" double, "report" text not null, "project" text, "staff" text, "date_time" text, "anameth" text, "parameter" text not null, "reading_num" double, "reading_txt" text, "unit" text, "comment" text, primary key(report, parameter), foreign key(obsid) references obs_points(obsid));
create table "seismic_data" (obsid text not null, length double not null, ground double, bedrock double, gw_table double, comment text, primary key (obsid, Length), foreign key (obsid) references obs_lines(obsid));
create table "vlf_data" (obsid text not null, length double not null, real_comp double, imag_comp double, comment text, primary key (obsid, Length), foreign key (obsid) references obs_lines(obsid));
create table "zz_flowtype" (type text not null,explanation text, primary key(type));
insert into zz_flowtype(type, explanation) values("Accvol", "Accumulated volume");
insert into zz_flowtype(type, explanation) values("Momflow", "Momentary flow rate");
insert into zz_flowtype(type, explanation) values("Aveflow", "Average flow since last reading");
create table "w_flow" (obsid text not null, instrumentid text not null, flowtype text not null, date_time text not null, reading double, unit text, comment text, primary key (obsid, instrumentid, flowtype, date_time), foreign key(obsid) references obs_points(obsid), foreign key (flowtype) references zz_flowtype(type));
CREATE TABLE "zz_meteoparam" (parameter text not null,explanation text, primary key(parameter));
insert into zz_meteoparam(parameter, explanation) values("precip", "Precipitation");
insert into zz_meteoparam(parameter, explanation) values("temp", "Air temperature");
CREATE TABLE "meteo" (obsid text not null, instrumentid text not null, parameter text not null, date_time text not null, reading_num double, reading_txt text, unit text, comment text, primary key (obsid, instrumentid, parameter, date_time), foreign key(obsid) references obs_points(obsid), foreign key (parameter) references zz_meteoparam(parameter));
CREATE TABLE "zz_strat" (strat text not null, color_mplot text not null, hatch_mplot text not null, color_qt text not null, brush_qt text not null,geoshorts text not null, primary key(strat));
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('unknown','white','','white','NoBrush','not in (''berg'',''b'',''rock'',''ro'',''grovgrus'',''grg'',''coarse gravel'',''cgr'',''grus'',''gr'',''gravel'',''mellangrus'',''grm'',''medium gravel'',''mgr'',''fingrus'',''grf'',''fine gravel'',''fgr'',''grovsand'',''sag'',''coarse sand'',''csa'',''sand'',''sa'',''mellansand'',''sam'',''medium sand'',''msa'',''finsand'',''saf'',''fine sand'',''fsa'',''silt'',''si'',''lera'',''ler'',''le'',''clay'',''cl'',''morän'',''moran'',''mn'',''till'',''ti'',''torv'',''t'',''peat'',''pt'',''fyll'',''fyllning'',''f'',''made ground'',''mg'',''land fill'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('rock','red','x','red','DiagCrossPattern','in (''berg'',''b'',''rock'',''ro'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('coarse gravel','DarkGreen','O','darkGreen','Dense7Pattern','in (''grovgrus'',''grg'',''coarse gravel'',''cgr'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('gravel','DarkGreen','O','darkGreen','Dense7Pattern','in (''grus'',''gr'',''gravel'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('medium gravel','DarkGreen','o','darkGreen','Dense6Pattern','in (''mellangrus'',''grm'',''medium gravel'',''mgr'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('fine gravel','DarkGreen','o','darkGreen','Dense6Pattern','in (''fingrus'',''grf'',''fine gravel'',''fgr'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('coarse sand','green','*','green','Dense5Pattern','in (''grovsand'',''sag'',''coarse sand'',''csa'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('sand','green','*','green','Dense5Pattern','in (''sand'',''sa'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('medium sand','green','.','green','Dense4Pattern','in (''mellansand'',''sam'',''medium sand'',''msa'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('fine sand','DarkOrange','.','orange','Dense4Pattern','in (''finsand'',''saf'',''fine sand'',''fsa'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('silt','yellow','\\','yellow','BDiagPattern','in (''silt'',''si'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('clay','yellow','-','yellow','HorPattern','in (''lera'',''ler'',''le'',''clay'',''cl'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('till','cyan','/','yellow','CrossPattern','in (''morän'',''moran'',''mn'',''till'',''ti'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('peat','DarkGray','+','darkGray','NoBrush','in (''torv'',''t'',''peat'',''pt'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('made ground','white','+','white','DiagCrossPattern','in (''fyll'',''fyllning'',''f'',''made ground'',''mg'',''land fill'')');
create view "w_lvls_last_geom" as select "b"."rowid" as "rowid", "a"."obsid" as "obsid", MAX("a"."date_time") as "date_time",  "a"."meas" as "meas",  "a"."level_masl" as "level_masl", "b"."geometry" as "geometry" from "w_levels" as "a" JOIN "obs_points" as "b" using ("obsid") GROUP BY obsid;
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) values ('w_lvls_last_geom', 'geometry', 'rowid', 'obs_points', 'geometry',1);
create view "w_qual_field_geom" as select "w_qual_field"."rowid" as "rowid", "w_qual_field"."obsid" as "obsid", "w_qual_field"."staff" as "staff", "w_qual_field"."date_time" as "date_time", "w_qual_field"."instrument" as "instrument", "w_qual_field"."parameter" as "parameter", "w_qual_field"."reading_num" as "reading_num", "w_qual_field"."reading_txt" as "reading_txt", "w_qual_field"."unit" as "unit", "w_qual_field"."flow_lpm" as "flow_lpm", "w_qual_field"."comment" as "comment", "obs_points"."geometry" as "geometry" from "w_qual_field" as "w_qual_field" left join "obs_points" using ("obsid");
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) values ('w_qual_field_geom', 'geometry', 'rowid', 'obs_points', 'geometry',1);
create view "w_qual_lab_geom" as select "w_qual_lab".'rowid' as rowid, "w_qual_lab".'obsid', "w_qual_lab".'depth', "w_qual_lab".'report', "w_qual_lab".'staff', "w_qual_lab".'date_time', "w_qual_lab".'anameth', "w_qual_lab".'parameter', "w_qual_lab".'reading_txt', "w_qual_lab".'reading_num', "w_qual_lab".'unit', "obs_points".'geometry' as geometry  from "w_qual_lab", "obs_points" where "w_qual_lab".'obsid'="obs_points".'obsid';
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) values ('w_qual_lab_geom', 'geometry', 'rowid', 'obs_points', 'geometry',1);
create view "w_levels_geom" as select "b"."rowid" as "rowid", "a"."obsid" as "obsid", "a"."date_time" as "date_time",  "a"."meas" as "meas",  "a"."h_toc" as "h_toc",  "a"."level_masl" as "level_masl", "b"."geometry" as "geometry" from "w_levels" as "a" join "obs_points" as "b" using ("obsid");
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) values ('w_levels_geom', 'geometry', 'rowid', 'obs_points', 'geometry',1);
create view w_flow_momflow as select "obsid" as "obsid","instrumentid" as "instrumentid","date_time" as "date_time","reading" as "reading", "unti" as "unit", "comment" as "comment" from w_flow where flowtype="Momflow";
create view w_flow_aveflow as select "obsid" as "obsid","instrumentid" as "instrumentid","date_time" as "date_time","reading" as "reading", "unti" as "unit", "comment" as "comment" from w_flow where flowtype="Aveflow";
create view w_flow_accvol as select "obsid" as "obsid","instrumentid" as "instrumentid","date_time" as "date_time","reading" as "reading", "unti" as "unit", "comment" as "comment" from w_flow where flowtype="Accvol";
CREATE INDEX idx_wquallab_odtp ON w_qual_lab(obsid, date_time, parameter);
CREATE INDEX idx_wquallab_odtpu ON w_qual_lab(obsid, date_time, parameter, unit);
CREATE INDEX idx_wqualfield_odtpu ON w_qual_field(obsid, date_time, parameter, unit);
