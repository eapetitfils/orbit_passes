import datetime
import math

import click
import ephem
from dateutil import parser


def next_passes(station, satellite, start_date, end_date, step=1, factor=1):
    steps = {10: math.radians(2),
             1: math.radians(0.1),
             0.1: math.radians(0.01),
             0.01: math.radians(0.001),
             0.001: math.radians(0)}
    start_date = ephem.date(start_date)
    end_date = ephem.date(end_date)
    passes = []
    station.date = start_date
    station.pressure = 0
    pass_on_going = False
    pass_data = {}
    while station.date <= end_date:
        satellite.compute(station)
        if satellite.alt >= math.radians(-0.227):
            if not pass_on_going:
                pass_data = {'start': station.date.datetime(), 'steps': []}
                pass_on_going = True
        else:
            if pass_on_going:
                pass_data['end'] = station.date.datetime()
                passes.append(pass_data)
                pass_on_going = False
        station.date += ephem.second * max([i for i in steps.keys() if abs(satellite.alt) > steps[i]]) / factor
    if pass_on_going:
        pass_data['end'] = end_date.datetime()
        passes.append(pass_data)
    for i in range(len(passes)):
        current_date = passes[i]['start']
        end_date = passes[i]['end']
        station.date = ephem.date(current_date)
        while current_date < end_date:
            satellite.compute(station)
            passes[i]['steps'].append({'time': current_date,
                                       'azimuth': math.degrees(satellite.az),
                                       'elevation': math.degrees(satellite.alt),
                                       'range': satellite.range,
                                       'velocity': satellite.range_velocity})
            current_date = current_date.replace(microsecond=0) + datetime.timedelta(seconds=step)
            station.date = ephem.date(current_date)
        station.date = ephem.date(end_date)
        satellite.compute(station)
        passes[i]['steps'].append({'time': end_date,
                                   'azimuth': math.degrees(satellite.az),
                                   'elevation': math.degrees(satellite.alt),
                                   'range': satellite.range,
                                   'velocity': satellite.range_velocity})
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
    station = ephem.Observer()
    station.lat = math.radians(latitude)
    station.long = math.radians(longitude)
    station.elevation = altitude
    with open(tle, 'r') as f:
        satellite = ephem.readtle(*f.readlines())
    if isinstance(start, str):
        start = parser.parse(start)
    end = start + datetime.timedelta(days=duration)
    passes = next_passes(station, satellite, start, end, step=interval)
    print('time; azimuth; elevation; range; radial velocity')
    for i in passes:
        for entry in i['steps']:
            print('{}; {}; {}; {}; {}'.format(entry['time'].isoformat(),
                                              entry['azimuth'],
                                              entry['elevation'],
                                              entry['range'],
                                              entry['velocity']))


if __name__ == '__main__':
    main()
