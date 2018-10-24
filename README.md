# orbit_passes

The module can be used standalone, or through the python function for further integration.

```
Usage: orbit.exe [OPTIONS] LATITUDE LONGITUDE ALTITUDE TLE

Options:
  --start TEXT        start date of the computation (the tool will try to adapt, but "YYYY-MM-DD HH:MM:SS.FFFFFF" works best)
  --duration FLOAT    how many days are computed. Can be a float. Defautl is 7 days
  --interval INTEGER  interval in seconds between two recorded points. Default is 60 seconds
  --help              Show this message and exit.
```

Example: `orbit.exe -- 51.41 -0.195 50 viasat.tle`

Note that the `--` after the the main arguments is needed if there is a negative number in the latitude, lagitude, altitude definition.
The TLE variable is the path to a tle file, which is typically a text file containing 3 lines, like this:

```
0 VIASAT 2
1 42740U 17029A   18291.12046305 -.00000274  00000-0  00000+0 0  9991
2 42740   0.0202 223.9076 0000226 266.9878 229.1065  1.00269850  5122
```

By default, the computation will be done from the current date and for the next seven days. These values can be tweaked with the option duration and start. The interval option is used to tweak how many points are printed by the tool.
