import pandas as pd
import sqlalchemy as sa
import xgboost as xgb
import numpy as np
import plotnine as gg
from pickle import load
from pygam import GAM, te

def draw_homeplate(catcher_perspective = True):
    
    # coordinates for strike zone
    dat = pd.DataFrame([[-.77,.1],[-.8,-.05],[0,-.2],[.8,-.05],[.77,.1]]
                       ,columns = ['x','z'])
    
    if catcher_perspective == False:
        dat['z'] = -1*dat['z']
        
    return(gg.geom_polygon(data = dat, color = 'black'
                           ,fill = None, size = 1))
def draw_strikezone():
    return(gg.geom_rect(xmin = -.77,xmax = .77,ymin = 1.6,ymax = 3.37
           ,color = 'black',fill  = None))

def load_models():
    
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
    
    bin_models.update({'bip':bip_models['multiclass']
                       ,'strike':sz_model})

    return(bin_models)

def query_data(pitcher_id, pitch_type, bat_side):
    
    # read in the query data and add the input values
    query_raw = open('./queries/prediction_data.sql').read()
    query_text = query_raw.format(pitcher_id,pitch_type,bat_side)
    
    # create an SQL Alchemy engine and query the data
    conn_string = 'postgresql://postgres:Melgren1224@localhost:5432/Baseball'
    engine = sa.create_engine(conn_string)
    tm = pd.read_sql_query(query_text,engine)

    # convert character data to one hot encoded columns
    tm = pd.get_dummies(tm,drop_first = False)
    
    # add pitch_side R column if the pitcher in quesiton is a lefty
    for col in ['bat_side_R','pitch_side_R','if_alignment_Infield shift'
                ,'if_alignment_Standard','if_alignment_Strategic'
                ,'of_alignment_4th outfielder','of_alignment_Standard'
                ,'of_alignment_Strategic']:
        if not col in tm.columns:
            tm[col] = 0
            
    return(tm)

def get_pitch_predictions(models,pitches):
    
# create a dict to store individual model predictions
    p = {}
    
    # predict the model on the pitcher data
    for k in models.keys():
        
        # get called strike probability by predicting the GAM model
        if k == 'strike':
            p[k] = models[k].predict(pitches.loc[:,['plate_x','plate_z'
                                                    ,'bat_side_R']])
            continue
        
        # store predictions for all xgboost models
        cols = models[k].feature_names
        pred_dat = xgb.DMatrix(pitches.loc[:,cols])
        p[k] = models[k].predict(pred_dat)
          
    # multiply binary predictions through to get final outcome predictions
    r = pd.DataFrame({
        'ball': (1-p['swing'])*(1-p['strike'])
        ,'called_strike': (1-p['swing'])*p['strike']
        ,'whiff': p['swing']*(1-p['contact'])
        ,'foul': p['swing']*p['contact']*(1-p['fair'])})
    
    # multiply the probability of a fair ball through each of the BIP results
    r_bip = p['bip']*(p['swing']*p['contact']*p['fair'])[:,np.newaxis]
    
    # bring in the BIP result names and weights then join onto r
    rv2 = pd.read_csv('./data/bip_result_run_values.csv')
    r = r.join(pd.DataFrame(r_bip,columns = rv2.play_result2.values))
    
    # get run values and multiply through the results predictions to get run value
    run_values = np.concatenate(([.051,-.064,-.064,-.064],rv2.RV))
    r['runs'] = np.dot(r,run_values)
    
    return(r.join(pitches.loc[:,['plate_x','plate_z']]))

def fill_prediction_space(preds):

    # predict a gam model on the predictions to populate the entire heat map
    smoother = GAM(te(0,1, n_splines=16), distribution='normal'
                   , link='identity')
    smoother.fit(preds.loc[:,['plate_x','plate_z']],preds.runs)
    
    # establish the X-Z plot space
    x = np.linspace(-1.3,1.3,53)
    z = np.linspace(1,4,61)
    
    # fill the runs prediction using the smoother model above
    hm = pd.DataFrame(index = pd.MultiIndex.from_product([x, z]
                                                         , names = ['x', 'z'])
                      ).reset_index()
    hm['runs'] = smoother.predict(hm)
    
    return(hm)

def draw_heatmap(hm,bat_side,catcher_perspective = True):
    plt = (
     gg.ggplot(hm)+gg.aes(x='x',y='z',fill = 'runs')+ gg.geom_tile()+
     gg.scale_fill_gradient2(low = 'blue',mid = 'white', high = 'red',midpoint = 0)+
     gg.labs(x = None,y = None)+
     gg.coord_fixed() + gg.guides(fill = False) + gg.theme_minimal() +
     gg.theme(axis_ticks = gg.element_blank(),panel_grid = gg.element_blank()
              ,axis_text = gg.element_blank()
              ,plot_background = gg.element_rect(fill = 'white', color = 'white'))+
     draw_strikezone()+draw_homeplate(catcher_perspective)
    )
    
    return(plt)

def draw_pitcher_heatmap(pitcher_id,pitch_type,bat_side):
    models = load_models()
    pitches = query_data(pitcher_id,pitch_type,bat_side)
    preds = get_pitch_predictions(models, pitches)
    plot_dat = fill_prediction_space(preds)
    heat_map = draw_heatmap(plot_dat,bat_side)
    heat_map.draw()
    
draw_pitcher_heatmap(434671,'FF','L')