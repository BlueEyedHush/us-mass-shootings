import numpy as np
import pandas as pd

# Original dataset

ms2 = pd.read_csv('../datasets/mass-shootings-v2.csv')

# Gender unification

ms_gender = ms2.copy()

def gender_mapper(g):
    ng = g.lower()
    if ng == 'unknown':
        return np.nan
    elif ng == 'm':
        return 'male'
    elif ng == 'm/f':
        return 'male/female'
    else:
        return ng

ms_gender['gender_dedup'] = ms_gender['Gender'].map(gender_mapper)

# Mental issues

ms_missues = ms_gender.copy()

def mhi_mapper(mhi):
    mhi = mhi.lower()
    if mhi in ['unclear', 'unknown']:
        return np.nan
    else:
        return mhi
    
ms_missues['missues_dedup'] = ms_missues['Mental Health Issues'].map(mhi_mapper)

# Races

ms_races = ms_missues.copy()

# 'White', 'Asian', nan, 'Black', 'Latino', 'Other', 'Unknown',
#       'Black American or African American',
#       'White American or European American', 'Asian American',
#       'Some other race', 'Two or more races',
#       'Black American or African American/Unknown',
#       'White American or European American/Some other Race',
#       'Native American or Alaska Native', 'white', 'black',
#       'Asian American/Some other race'
#
def race_mapper(mhi):
    if isinstance(mhi, float) and np.isnan(mhi):
        return mhi
    
    races = []
    mhi = mhi.lower()
    if 'unknown' in mhi:
        races.append('u')
    if 'black' in mhi or 'african' in mhi:
        races.append('black')
    if 'white' in mhi or 'european' in mhi:
        races.append('white')
    if 'asian' in mhi:
        races.append('asian')
    if 'other' in mhi:
        races.append('other')
    if 'latino' in mhi:
        races.append('latino')
    if 'two or more' in mhi or '/' in mhi:
        races.append('>1')
    if 'native' in mhi:
        races.append('native')
    
    if races == ['u']:
        return np.nan
    elif not races:
        return '!' + mhi
    else:
        return '; '.join(races)
    
ms_races['races_dedup'] = ms_races['Race'].map(race_mapper)

# States

ms_states = ms_races.copy()
ms_states['state'] = ms_states['Location'].str.split(',').map(lambda l: l[-1].strip(), 'ignore')

ms_sf = ms_states.copy()

def state_mapper(s):
    mapping = {'nv': 'nevada', 'ca': 'california', 'pa': 'pensylvania', 'wa': 'washington', 'la': 'louisiana'}
    s = s.lower()
    if s in mapping:
        return mapping[s]
    else:
        return s

ms_sf['state_full'] = ms_sf['state'].map(state_mapper, na_action='ignore')

# Keep only necessary columns
ms_cfilter = ms_sf[['S#', 'Title', 'Date', 'Summary', 'Fatalities', 'Injured', 'Total victims', 'Latitude', 
                    'Longitude', 'gender_dedup', 'missues_dedup', 'races_dedup', 'state_full']]


# Date
split_date = ms_cfilter['Date'].str.extract('^(?P<month>[0-9]+)/(?P<day>[0-9]+)/(?P<year>[0-9]+)$')
for c in ['day', 'month', 'year']:
    split_date[c] = split_date[c].map(lambda x: int(x))

ms_ds = pd.concat([ms_cfilter, split_date], axis=1)
del ms_ds['Date']

# Date bins
date_bins = pd.cut(ms_ds['year'].map(lambda x: int(x)), 17)

ms_dbin = ms_ds.copy()
ms_dbin['year_bin'] = date_bins
ms_dbin_cnts = ms_dbin['year_bin'].value_counts()

# Distribution over the year
bmp = ms_ds.copy()
bmp['count'] = 1
by_month = bmp.groupby(['month']).sum()
by_month = by_month[['Fatalities', 'Injured', 'Total victims', 'count']]

# appropriate for state-based groupping
state_name_map = {
    'pensylvania': 'pennsylvania',
    'washington d.c.': 'maryland'
}
race_map = {
    '>1': float('NaN'),
    'asian; other; >1': 'asian',
    'u; black; >1': 'black',
    'white; other; >1': 'white',
}
sm_df = ms_ds.copy()
sm_df.replace({'state_full': state_name_map}, inplace=True)
sm_df.replace({'races_dedup': race_map}, inplace=True)
