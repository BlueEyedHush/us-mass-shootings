
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from math import floor, ceil

from data_proc import *

bmp = ms_dow.copy()
bins = pd.cut(ms_ds['year'].map(lambda x: int(x)), 17)
bmp['db'] = bins
bmp['count'] = 1

ubins = bins.unique()[::-1]

def calc_max():
	g = bmp.groupby(['db', 'month'])
	fat = g['Fatalities'].sum()
	inj = g['Injured'].sum()

	cnt = g['count'].sum()

	return (cnt.max(), (fat + inj).max())

max_cnt, max_vic = calc_max()

def bin_text_repr(b):
	nlow = int(ceil(b.left))
	nhigh = int(floor(b.right))
	return "[{}, {}]".format(nlow, nhigh)
bins_txt = map(bin_text_repr, ubins)

def for_year_bin(bin_id):
	bmpy = bmp[bmp['db'] == ubins[bin_id]]
	by_month = bmpy.groupby(['dow']).sum()
	by_month = by_month[['Fatalities', 'Injured', 'Total victims', 'count']]
	return by_month

fig = plt.figure()
ax_up = fig.add_subplot(211)
ax_down = fig.add_subplot(212)
plt.subplots_adjust(bottom=0.25)

# (h_left, v_left, len, height)
ax_year = plt.axes([0.15, 0.1, 0.65, 0.03])
s_year = Slider(ax_year, 'Year', 0, len(ubins) - 0.1, valfmt = "%d")

scale_fixed = False
btn_ax = plt.axes([0.8, 0.025, 0.1, 0.04])
btn_fix_scale = Button(btn_ax, 'Fix scale', hovercolor='0.975')

import calendar

def plot(bin_id):
	data = for_year_bin(bin_id)

	for ax, maxv in [(ax_up, max_vic), (ax_down, max_cnt)]:
		ax.clear()
		
		ax.set_xticks(range(0,7))
		ax.set_xticklabels(calendar.day_abbr)
		ax.set_xlim([-1,8])
		if scale_fixed:
			ax.set_ylim([0, maxv+1])

	s_year.valtext.set_text(bins_txt[bin_id])

	ax_up.bar(data.index, data['Fatalities'])
	ax_up.bar(data.index, data['Injured'])

	ax_down.bar(data.index, data['count'])

	fig.canvas.draw_idle()

def update(val):
	bin_id = int(s_year.val)
	plot(bin_id)

def on_fix_button_click(event):
	global scale_fixed
	scale_fixed = not scale_fixed
	update("")

s_year.on_changed(update)
btn_fix_scale.on_clicked(on_fix_button_click)

plot(0)

fig.canvas.draw()
plt.show()