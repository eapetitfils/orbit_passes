This folder contains a comparison between STK and Skyfield results.

For each software, the range between ground stations located at `51deg 24' 36.0" N -00deg 11' 42.0" E` and `51deg 24' 50.4" N -00deg 11' 42.0" E`, both at an altitude of 50m, and tghe Viasat-2 geostationnary satellite defined by the TLE below, was computed over 3 months.
```
0 VIASAT 2
1 42740U 17029A   18291.12046305 -.00000274  00000-0  00000+0 0  9991
2 42740   0.0202 223.9076 0000226 266.9878 229.1065  1.00269850  5122
```
Then , the difference between this two ranges is plotted (**skyfield_delta_range.png** and **stk_delta_range.png**), which shows very similar trends, contrary to what was observed with the ephem library.

Finally, a plot showing the difference between these two libraries is displayed in **skyfield_vs_stk.png**. It shows that the error in the next 3 months stays below 1.5cm