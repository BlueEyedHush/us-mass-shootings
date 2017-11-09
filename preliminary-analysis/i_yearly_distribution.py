
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons

from data_proc import *

bmp = ms_ds.copy()
bins = pd.cut(ms_ds['year'].map(lambda x: int(x)), 10)
bmp['db'] = bins
bmp['count'] = 1

ubins = bins.unique()[::-1]

def for_year_bin(bin_id):
	bmpy = bmp[bmp['db'] == ubins[bin_id]]
	by_month = bmpy.groupby(['month']).sum()
	by_month = by_month[['Fatalities', 'Injured', 'Total victims', 'count']]
	return by_month

def plot(axis, data):
	ax.clear()
	
	ax.set_xticks(range(1,13))
	ax.set_xlim([0,13])

	ax.bar(data.index, data['count'])
	fig.canvas.draw_idle()

fig, ax = plt.subplots()
bm = for_year_bin(0)
plot(ax, bm)
ax_year = plt.axes([0.0, 0.0, 0.98, 0.05])
s_year = Slider(ax_year, 'Year int', 0, len(ubins))

def update(val):
	bin_id = int(s_year.val)
	bm = for_year_bin(bin_id)
	plot(ax, bm)

s_year.on_changed(update)

fig.canvas.draw()
plt.show()