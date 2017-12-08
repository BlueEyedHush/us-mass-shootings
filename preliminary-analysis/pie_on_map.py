from __future__ import print_function
import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap as Basemap
from matplotlib.patches import Polygon
from us_states_coords import get_coords_map

def plotit(col_name, back_name):

    def_colours = ['red','blue','green','yellow','magenta','purple', 'brown', 'orange', 'silver', 'gold']

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

    from data_proc import sm_df, vict_df
    # plotting colour
    import matplotlib
    from matplotlib.colors import rgb2hex
    cmap = matplotlib.cm.get_cmap('Spectral')
    total = sm_df['Total victims'].sum()
    victims = sm_df.groupby('state_full')['Total victims'].count()

    statenames = []
    colors = {}
    cmap = plt.cm.hot # use 'hot' colormap
    vmin = 0; vmax = 40 # set range.
    for shapedict in m.states_info:
        statename = shapedict['NAME']
        # skip DC and Puerto Rico.
        if statename not in ['District of Columbia','Puerto Rico']:
            # calling colormap with value between 0 and 1 returns
            # rgba value.  Invert color range (hot colors are high
            # population), take sqrt root to spread out colors more.
            if statename.lower() in victims:
                pop = float(victims.loc[statename.lower()])
                colors[statename] = cmap(1.-np.sqrt((pop-vmin)/(vmax-vmin)))[:3]
                print(pop)
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

    multicolumn_plots = {
        'vict': (['inj_rel', 'killed_rel'], vict_df)
    }


    state_to_ratios = {}
    possible_labels = []

    if col_name in multicolumn_plots:
        columns, g_df = multicolumn_plots[col_name]
        possible_labels = columns

        for state in g_df.index:
            ratios = []
            for c in columns:
                ratios.append(g_df[c].loc[state])
            state_to_ratios[state] = ratios
    else:
        sorted_idx_df = sm_df.sort_index()
        g_df = sorted_idx_df.groupby('state_full')
        possible_labels = sorted_idx_df[col_name].value_counts().index

        for state, df in g_df:
            vcnt = df[col_name].value_counts()
            rel_vcnt = vcnt / vcnt.sum()

            ratios = []
            for lbl in possible_labels:
                if lbl in rel_vcnt.index:
                    ratios.append(rel_vcnt.loc[lbl])
                else:
                    ratios.append(0.0)

            state_to_ratios[state] = ratios

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


    plt.title(col_name)
    plt.show()
