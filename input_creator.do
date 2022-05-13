 * name: Andrew Lou
* date: 05/11/2022
* This .do file creates a manageable .csv file to run trips on TomTom.
version 17
use "trips_highway_test_timezone_conversion.dta", clear

drop if strpos(category, "20 km")
drop if strpos(category, "30 km")

export delimited test_input, clear
