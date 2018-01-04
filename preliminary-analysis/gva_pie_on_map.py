from __future__ import print_function
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap as Basemap
from matplotlib.patches import Polygon
from us_states_coords import get_coords_map

json = pd.read_json('../gva-analysis/logs.json')
rowsWithGuns = json[json.apply(lambda x: len(x['guns']) > 0, axis=1)][['state', 'guns']]

unique_vals = set()
gunStateDict = {}
for index, row in rowsWithGuns.iterrows():
    for gun in row.guns:
        gt = gun["type"].lower()
        st = row["state"].lower()

        if gt != "unknown" and gt != 'other':
            gt = gun["type"].lower()
            # mapping
            m = {
                'gauge': u'shotgun',
                '22 lr': u'r/p',
                'ar-15': u'rifle',
                '25 auto': u'r/p',
                '357': u'r/p',
                '38 spl': u'r/p',
                '380 auto': u'r/p',
                '40': u'r/p',
                '45': u'rifle',
                '7.62': u'rifle',
                '9mm': 'pistol',
                'handgun': 'pistol',
            }
            
            for phrase, final_gt in m.iteritems():
                if phrase in gt.lower():
                    gt = final_gt

            unique_vals.add(gt)
            if st not in gunStateDict:
                gunStateDict[st] = {gt: 1}
            elif gun["type"] not in gunStateDict[st]:
                gunStateDict[st][gt] = 1
            else:
                gunStateDict[st][gt] = gunStateDict[st][gt] + 1

gun_labels = list(unique_vals)

json['count'] = 1
json['state'] = json['state'].map(lambda x: x.lower())
counts = json.groupby('state').count()['count']

def plotit(col_name, back_name):

    def_colours = ['red','blue','yellow', 'orange', 'magenta','purple', 'brown', 'silver', 'gold']

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

    # plotting colour
    import matplotlib
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import rgb2hex, Normalize

    statenames = []
    colors = {}
    cmap = ScalarMappable(cmap='YlGn', norm=plt.Normalize(vmin=0.0, vmax=counts.max()))
    for shapedict in m.states_info:
        statename = shapedict['NAME']
        # skip DC and Puerto Rico.
        if statename not in ['District of Columbia','Puerto Rico']:
            if statename.lower() in counts:
                v = float(counts[statename.lower()])
            else:
                v = 0.0
                
        colors[statename] = cmap.to_rgba(v)[:3]
        statenames.append(statename)

    for nshape,seg in enumerate(m.states):
        sname = statenames[nshape]
        if sname in colors:
            c = rgb2hex(colors[sname])
            ec = c 
        else:
            c = 'white'
            ec = 'black'

        poly = Polygon(seg,facecolor=c, edgecolor=ec)
        ax.add_patch(poly)

    # draw meridians and parallels.
    m.drawparallels(np.arange(25,65,20),labels=[1,0,0,0])
    m.drawmeridians(np.arange(-120,-40,20),labels=[0,0,0,1])

    import matplotlib.patches as mpatches


    state_to_ratios = {}
    possible_labels = gun_labels

    for statename, gun_dict in gunStateDict.iteritems():
        s = float(sum(gun_dict.values()))
        ratios = map(lambda x: gun_dict[x]/s if x in gun_dict else 0.0, gun_labels)
        state_to_ratios[statename] = ratios


    legend_patches = []
    for idx, lval in enumerate(possible_labels):
        c = def_colours[idx]
        p = mpatches.Patch(color=c, label=lval)
        legend_patches.append(p)

    plt.legend(handles=legend_patches, loc='lower left')

    us_state_center = get_coords_map()


    for state in us_state_center:
        if state in state_to_ratios:
            r = state_to_ratios[state]
            lat, long = us_state_center[state]
            x, y = m(long, lat)
            draw_pie(sbp_ax, colors=def_colours, ratios=r, X=x, Y=y)

    cax = fig.add_axes([0.9, 0.1, 0.03, 0.8])
    # fake up the array of the scalar mappable. Urgh...
    cmap._A = []
    fig.colorbar(cmap, cax=cax)

    plt.title(col_name)
    plt.show()

plotit("","")