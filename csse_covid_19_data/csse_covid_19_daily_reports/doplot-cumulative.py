import csv
import sys

import itertools 

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.dates import (YEARLY, DateFormatter, WEEKLY, DayLocator, date2num, num2date,
                              rrulewrapper, RRuleLocator, drange)
import matplotlib.colors as colors
import matplotlib.cm as cmx

import datetime

rule = rrulewrapper(WEEKLY, interval=1)
loc = RRuleLocator(rule)
formatter = DateFormatter('%y-%m-%d')
date1 = datetime.date(2020, 1, 22)
# date2 = datetime.date.today()
delta = datetime.timedelta(days=1)

with open(sys.argv[1], 'r') as f:
    covid_cols, covid_rows = np.loadtxt(f, delimiter=',', usecols=(0, 1), unpack=True, dtype={'names': ('date', 'deaths'), 'formats': ('datetime64[D]', 'f4')})  # np.datetime64, np.float))  # skip_header=1

with open(sys.argv[2], 'r') as f:
    us_2017_cols, us_2017_rows = np.loadtxt(f, delimiter=';', usecols=(0, 2), unpack=True, dtype={'names': ('cause', 'deaths'), 'formats': ('|U64', 'f4')}, skiprows=2)  # remove header and all causes
    us_2017_cols, us_2017_rows = us_2017_cols[:-1], us_2017_rows[:-1]  # remove other causes
#    us_2017_cols, us_2017_rows = us_2017_cols[::-1], us_2017_rows[::-1]  # reverse

date2 = max(covid_cols) + np.timedelta64(1, 'D')
dates = drange(date1, date2, delta)

my_dpi = 96
width, height = 1280, 860

fig, ax = plt.subplots(figsize=(width/my_dpi, height/my_dpi), dpi=my_dpi)

plt.gca().xaxis.set_major_formatter(formatter)
plt.gca().xaxis.set_major_locator(loc)

plt.plot(dates, covid_rows, label='COVID-19 US Deaths', color='0', lw=2)

#plt.hlines(us_2017_rows, dates[0], dates[-1], linestyles='dotted')
#for label, y in zip(us_2017_cols, us_2017_rows):
#    va = 'bottom' if label == 'Septicemia' else 'top'
#    plt.text(dates[0], y, f'Avg. monthly deaths by {label} in 2017', ha='left', va=va, fontsize=10)

def estimate_deaths(yearly, date):
    end_date = datetime.date(2020, 12, 31)
    date_diff = end_date - num2date(date).date()
    return yearly * (1 - date_diff.days / 364.25)

cm_name = 'tab20c'  # twilight jet bwr
cm = plt.get_cmap(cm_name)

value_cNorm  = colors.Normalize(vmin=0, vmax=max(us_2017_rows))
value_scalarMap = cmx.ScalarMappable(norm=value_cNorm, cmap=cm)
index_cNorm  = colors.Normalize(vmin=0, vmax=len(us_2017_cols))
index_scalarMap = cmx.ScalarMappable(norm=index_cNorm, cmap=cm)

all_d_ys = []
all_colors = []
all_labels = []
d_xs = [dates[0], dates[-1] + np.timedelta64(2, 'W').astype('float64')]
for i, label, y in zip(itertools.count(), us_2017_cols, us_2017_rows):
    d_ys = [estimate_deaths(y, x) for x in d_xs]
    colorVal = index_scalarMap.to_rgba(i)
    linestyle = 'dashed' if d_ys[-1] < max(covid_rows) else 'solid'
    marker = None  # 'x' if d_ys[-1] < max(covid_rows) else None
    label = f'2017 Avg. Deaths: {label}'
    all_d_ys.append(d_ys)
    all_colors.append(colorVal)
    all_labels.append(label)

plt.stackplot(d_xs, all_d_ys, labels=all_labels, colors=all_colors, )

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left', ncol=3, mode="expand", borderaxespad=0., fontsize='x-small')

plt.gcf().autofmt_xdate()
plt.gca().set_ylim([0, covid_rows[-1] * 1.5])

fig.savefig("cumulative.png", dpi=my_dpi * 2)
plt.show()
