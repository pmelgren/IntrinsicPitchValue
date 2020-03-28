from pickle import load
import pandas as pd
import sqlalchemy as sa

# load the swing/take, whiff/contact, and fair/foul models
f = open('./models/binary_models','rb')
bin_models = load(f)
f.close()

# load the bip model
f = open('./models/BIP_models','rb')
bip_models = load(f)
f.close()

# load the strike zone model
f = open('./models/sz_model','rb')
sz_model = load(f)
f.close()

pitcher_id = 571510
pitch_type = 'SL'
bat_side = 'L'

query_raw = open('./queries/prediction_data.sql').read()
query_text = query_raw.format(pitcher_id,pitch_type,bat_side)
engine = sa.create_engine('postgresql://postgres:Melgren1224@localhost:5432/Baseball')
tm = pd.read_sql_query(query_text,engine)

# convert character data to one hot encoded columns
X = pd.get_dummies(tm,drop_first = False)

# add pitch_side R column if the pitcher in quesiton is a lefty
for col in ['bat_side_R','pitch_side_R','if_alignment_Infield shift'
            ,'if_alignment_Standard','if_alignment_Strategic'
            ,'of_alignment_4th outfielder','of_alignment_Standard'
            ,'of_alignment_Strategic']:
    if not col in X.columns:
        X[col] = 0
        

X.head()\n


import xgboost as xgb

# create dataframe of each binary prediction
p = pd.DataFrame()
for k in bin_models.keys():
    cols = bin_models[k].feature_names
    pred_dat = xgb.DMatrix(X.loc[:,cols])
    p[k] = bin_models[k].predict(pred_dat)
    
# get strike probability for each pitch 
p['called_strike'] = sz_model.predict(X.loc[:,['plate_x','plate_z','bat_side_R']])
    
# multiply binary predictions to get terminal outcome predictions
r = pd.DataFrame({'ball':(1-p.swing)*(1-p.called_strike)})
r['called_strike'] = (1-p.swing)*p.called_strike
r['whiff'] = p.swing*(1-p.contact)
r['foul'] = p.swing*p.contact*(1-p.fair)

import numpy as np

# now predict the BIP results
cols = bip_models['multiclass'].feature_names
pred_dat = xgb.DMatrix(X.loc[:,cols])
bip_preds = bip_models['multiclass'].predict(pred_dat)

# bring in the BIP result run value info to get feature names
rv2 = pd.read_csv('./data/bip_result_run_values.csv')

# multiply the probability of a fair ball through each of the BIP results
r_bip = bip_preds*(p.swing*p.contact*p.fair)[:,np.newaxis]

# make this into a df and join onto the results df
r = r.join(pd.DataFrame(r_bip,columns = rv2.play_result2.values))

r

# get a list of run values to multiply through the above df
run_values = np.concatenate(([.051,-.064,-.064,-.064],rv2.RV))

# multiply through the predictions to get predicted run values
r['runs'] = np.dot(r,run_values)

hmdat = pd.DataFrame({'x':X.plate_x,'z':X.plate_z,'runs':r.runs})
hmdat.head()

from time import time
from pygam import GAM, te

starttime = time()

X = hmdat.loc[:,['x','z']]
y = hmdat.runs

smoother = GAM(te(0,1, n_splines=16), distribution='normal', link='identity').fit(X,y)

print(time() - starttime)

import numpy as np
x = np.linspace(-1.3,1.3,53)
z = np.linspace(1,4,61)
hm = pd.DataFrame(index = pd.MultiIndex.from_product([x, z], names = [\x\, \z\])).reset_index()
hm['runs'] = smoother.predict(hm)\n

import plotnine as gg

homeplate = pd.DataFrame([[-.77,.1],[-.8,-.05],[0,-.2],[.8,-.05],[.77,.1]]
                         ,columns = ['x','z'])
plt = (
 gg.ggplot(hm)+gg.aes(x='x',y='z',fill = 'runs')+
 gg.geom_tile()+
 gg.scale_fill_gradient2(low = \blue\,mid = \white\, high = \red\,midpoint = 0)+
 gg.geom_rect(xmin = -.77,xmax = .77,ymin = 1.6,ymax = 3.37
              ,color = \black\,fill  = None)+
 gg.labs(x = None,y = None,title = \Matthew Boyd Slider vs \+bat_side+\HH\)+
 gg.geom_polygon(data = homeplate,color = \black\,fill = None, size = 1)+
 gg.coord_fixed() + gg.guides(fill = False) + gg.theme_minimal() +
 gg.theme(axis_ticks = gg.element_blank(),panel_grid = gg.element_blank()
          ,axis_text = gg.element_blank()
          ,plot_background = gg.element_rect(fill = 'white', color = 'white'))
)
plt
   

plt.save(\./plots/Matthew_Boyd_Slider_\+bat_side+\HH.jpg\)
