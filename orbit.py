import datetime
import math
import os

import click
from skyfield.api import EarthSatellite, Topos, earth, load, Timescale, utc
from dateutil import parser

import concurrent.futures

os.environ['HTTP_PROXY'] = 'ait.sstl.co.uk:3128'
os.environ['HTTPS_PROXY'] = 'ait.sstl.co.uk:3128'
os.environ['SSL_CERT_FILE'] = r'C:\Users\Terra\AppData\Roaming\pip\sstl-ca.cer'


def return_pos(station, satellite, current_date):
    ts = load.timescale()
    diff = satellite - station
    _, _, previous_distance = diff.at(ts.utc(current_date - datetime.timedelta(seconds=0.1))).altaz()
    alt, az, distance = diff.at(ts.utc(current_date)).altaz()
    sat_pos = satellite.at(ts.utc(current_date))
    x, y, z = sat_pos.position.m
    lat, lon = math.degrees(sat_pos.subpoint().latitude.radians), math.degrees(sat_pos.subpoint().longitude.radians)
    height = sat_pos.distance().m
    return {'time': current_date,
            'azimuth': math.degrees(az.radians),
            'elevation': math.degrees(alt.radians),
            'range': distance.m,
            'velocity': (distance.m - previous_distance.m) / 0.1,
            'x': x, 'y': y, 'z': z,
            'latitude': lat,
            'longitude': lon,
            'height': height}


def next_passes(station, satellite, start_date, end_date, step=1):
    horizon = math.radians(-0.227)
    ts = load.timescale()
    diff = satellite - station
    passes = []
    station.pressure = 0
    pass_on_going = False
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=utc)
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=utc)
    current_date = start_date
    min_rate = 0.0001
    while current_date <= end_date:
        alt, az, distance = diff.at(ts.utc(current_date)).altaz()
        try:
            elevation_speed = abs(alt.radians - previous_alt.radians) / (current_date - previous_date).total_seconds()
            elevation_speed = max(1e-9, elevation_speed)
            rate = min(max(min_rate, abs(alt.radians - horizon)  / elevation_speed), 86400) / 10
        except:
            rate = min_rate
        finally:
            previous_alt = alt
            previous_date = current_date
        if alt.radians >= horizon:
            if not pass_on_going:
                pass_data = {'start': current_date, 'steps': []}
                pass_on_going = True
        else:
            if pass_on_going:
                pass_data['end'] = current_date
                passes.append(pass_data)
                pass_on_going = False
        current_date += datetime.timedelta(seconds=rate)
    if pass_on_going:
        pass_data['end'] = end_date
        passes.append(pass_data)
    for i in range(len(passes)):
        current_date = passes[i]['start']
        end_date = passes[i]['end']

        dates = []
        while current_date < end_date:
            dates.append(current_date)
            current_date = current_date.replace(microsecond=0) + datetime.timedelta(seconds=step)
        dates.append(end_date)
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [executor.submit(return_pos, station, satellite, d) for d in dates]
            passes[i]['steps'] = [future.result() for future in futures]
    return [sat_pass for sat_pass in passes if max([i['elevation'] for i in sat_pass['steps']]) > 0]


@click.command()
@click.option('--start', default=datetime.datetime.utcnow(), help='start date of the computation')
@click.option('--duration', default=1, help='how many days are computed')
@click.option('--interval', default=60, help='interval in seconds between two recorded points')
@click.argument('latitude', type=float)
@click.argument('longitude', type=float)
@click.argument('altitude', type=float)
@click.argument('tle')
def main(latitude, longitude, altitude, tle, duration, start, interval):
    import time
    t0 = time.time()
    station = Topos(latitude_degrees=latitude, longitude_degrees=longitude, elevation_m=altitude)
    with open(tle, 'r') as f:
        lines = f.read().strip().splitlines()
        satellite = EarthSatellite(lines[1], lines[2], lines[0])
    if isinstance(start, str):
        start = parser.parse(start)
    end = start + datetime.timedelta(days=duration)
    passes = next_passes(station, satellite, start, end, step=interval)
    print('time; azimuth; elevation; range; radial velocity; GCRF_x; GCRF_y; GCRF_z; latitude; longitude; height')
    for i in passes:
        for entry in i['steps']:
            print('{}; {}; {}; {}; {}; {}; {}; {}; {}; {}; {}'.format(entry['time'].isoformat(),
                                                                      entry['azimuth'],
                                                                      entry['elevation'],
                                                                      entry['range'],
                                                                      entry['velocity'],
                                                                      entry['x'],
                                                                      entry['y'],
                                                                      entry['z'],
                                                                      entry['latitude'],
                                                                      entry['longitude'],
                                                                      entry['height']))

if __name__ == '__main__':
    main()
