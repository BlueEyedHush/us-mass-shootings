
import pandas as pd
import calmap
import matplotlib.pyplot as plt

json = pd.read_json('../gva-analysis/logs.json')

gva_dt = json.copy()
gva_dt["count"] = 1
gva_dt = gva_dt.groupby('date').sum()

fig,ax = calmap.calendarplot(gva_dt["count"])

fig.colorbar(ax[0].get_children()[1], ax=ax.ravel().tolist())
plt.show()