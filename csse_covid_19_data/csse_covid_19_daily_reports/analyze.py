from collections import namedtuple, defaultdict
import glob
import csv
import itertools
import sys

RowA = namedtuple('RowA', 'filename,province_state,country_region,last_update,confirmed,deaths,recovered')
RowB = namedtuple('RowB', 'filename,province_state,country_region,last_update,confirmed,deaths,recovered,latitude,longitude')
RowC = namedtuple('RowC', 'filename,FIPS,Admin2,province_state,country_region,Last_Update,Lat,Long_,confirmed,deaths,recovered,Active,Combined_Key')
RowD = namedtuple('RowC', 'filename,FIPS,Admin2,province_state,country_region,Last_Update,Lat,Long_,confirmed,deaths,recovered,Active,Combined_Key,Incidence_Rate,Case_Fatality_Ratio')

row_cls_map = {
    tuple('\ufeffProvince/State,Country/Region,Last Update,Confirmed,Deaths,Recovered,Latitude,Longitude'.split(',')): RowB,
    tuple('Province/State,Country/Region,Last Update,Confirmed,Deaths,Recovered,Latitude,Longitude'.split(',')): RowB,
    tuple('\ufeffProvince/State,Country/Region,Last Update,Confirmed,Deaths,Recovered'.split(',')): RowA,
    tuple('Province/State,Country/Region,Last Update,Confirmed,Deaths,Recovered'.split(',')): RowA,
    tuple('\ufeffFIPS,Admin2,Province_State,Country_Region,Last_Update,Lat,Long_,Confirmed,Deaths,Recovered,Active,Combined_Key'.split(',')): RowC,
    tuple('FIPS,Admin2,Province_State,Country_Region,Last_Update,Lat,Long_,Confirmed,Deaths,Recovered,Active,Combined_Key'.split(',')): RowC,
    ('FIPS', 'Admin2', 'Province_State', 'Country_Region', 'Last_Update', 'Lat', 'Long_', 'Confirmed', 'Deaths', 'Recovered', 'Active', 'Combined_Key', 'Incidence_Rate', 'Case-Fatality_Ratio'): RowD,
    ('FIPS', 'Admin2', 'Province_State', 'Country_Region', 'Last_Update', 'Lat', 'Long_', 'Confirmed', 'Deaths', 'Recovered', 'Active', 'Combined_Key', 'Incident_Rate', 'Case_Fatality_Ratio'): RowD,
}

def readrows():
    for filename in glob.glob('*.csv'):
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            row_cls = row_cls_map[tuple(next(reader))]
            for line in reader:
                yield row_cls(filename, *line)

allrows = sorted(readrows(), key=lambda x: (x.country_region, x.filename))
# rows = itertools.groupby(allrows, lambda x: x.country_region)
rows = [row for row in allrows if row.country_region == 'US']

total_deaths_by_day = defaultdict(int)
for filename, us_rows in itertools.groupby(rows, lambda x: x.filename):
    date = filename[:-4].split('-')
    date = '{2}-{0}-{1}'.format(*date)
    total_deaths_by_day[date] += sum(int(x.deaths) if x.deaths else 0 for x in us_rows)

output = dict(total_deaths_by_day)

writer = csv.writer(sys.stdout)
for date, deaths in sorted(output.items()):
    writer.writerow((date, deaths))
