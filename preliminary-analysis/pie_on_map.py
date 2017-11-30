from __future__ import print_function
import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap as Basemap
from matplotlib.patches import Polygon
from us_states_coords import get_coords_map

def_colours = ['red','blue','green','yellow','magenta','purple']

def draw_pie(ax, ratios=[0.4, 0.3, 0.3], colors=def_colours, X=0, Y=0, size=1000):
    N = len(ratios)

    xy = []

    start = 0.
    for ratio in ratios:
        x = [0] + np.cos(np.linspace(2 * math.pi * start, 2 * math.pi * (start + ratio), 30)).tolist()
        y = [0] + np.sin(np.linspace(2 * math.pi * start, 2 * math.pi * (start + ratio), 30)).tolist()
        xy1 = zip(x, y)
        xy.append(xy1)
        start += ratio

    for i, xyi in enumerate(xy):
        fc = colors[i]
        ax.scatter([X], [Y], marker=(xyi, 0), s=size, facecolor=fc, zorder=4)



fig = plt.figure()

plt.subplots_adjust(left=0.05,right=0.95,top=0.90,bottom=0.05,wspace=0.15,hspace=0.05)
sbp_ax = plt.subplot(111)

# Lambert Conformal map of lower 48 states.
m = Basemap(llcrnrlon=-119,llcrnrlat=22,urcrnrlon=-64,urcrnrlat=49,
            projection='lcc',lat_1=33,lat_2=45,lon_0=-95)


shp_info = m.readshapefile('st99_d00','states',drawbounds=True)
ax = plt.gca() # get current axes instance

for nshape,seg in enumerate(m.states):
    poly = Polygon(seg,facecolor='white')
    ax.add_patch(poly)
# draw meridians and parallels.
m.drawparallels(np.arange(25,65,20),labels=[1,0,0,0])
m.drawmeridians(np.arange(-120,-40,20),labels=[0,0,0,1])

plt.title('Filling State Polygons by Population Density')

from data_proc import sm_df
column = 'gender_dedup'

sm_df.sort_index()
uvals = sm_df[column].value_counts().index
import matplotlib.patches as mpatches

legend_patches = []
colour_mapping = {}
for idx, v in enumerate(uvals):
    c = def_colours[idx]
    colour_mapping[v] = c
    p = mpatches.Patch(color=c, label=v)
    legend_patches.append(p)

plt.legend(handles=legend_patches, loc='lower left')

g_df = sm_df.groupby('state_full')


us_state_center = get_coords_map()


for state, df in g_df:
    vcnt = df[column].value_counts()
    rel_vcnt = vcnt / vcnt.sum()

    colours = map(lambda v: colour_mapping[v], vcnt.index)
    assert(len(colours) == len(rel_vcnt))

    lat, long = us_state_center[state]
    x, y = m(long, lat)
    draw_pie(sbp_ax, colors=colours, ratios=rel_vcnt, X=x, Y=y)


plt.show()