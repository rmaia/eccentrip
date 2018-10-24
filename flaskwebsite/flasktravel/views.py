from flasktravel import app
from flasktravel import auxfxns
from flask import render_template
from flask import request
from gensim.models.doc2vec import Doc2Vec
import pandas as pd
import numpy as np
import re
import pickle
import googlemaps

@app.route('/')
@app.route('/index')

def view_method():
    return render_template('index.html', title='Home')


@app.route('/output', methods=['GET', 'POST'])

def output():

    gmaps = googlemaps.Client(key='') # enter your key

    # Load data and model
    with open('flasktravel/data/AOmasterdata-nodup-week4-clean', 'rb') as infile:
         aotable = pickle.load(infile)

    model = Doc2Vec.load('flasktravel/data/model-week4-clean')

    # pull input data
    usr_select = request.form.get('usrtext')
    filt_dist = request.form.get('usrdist')
    filt_loc = request.form.get('usrloc')
    usertok = auxfxns.usertokens(usr_select)

    if filt_dist is None:
      filt_dist = ''
    if filt_loc is None:
      filt_loc = ''

    # calculate vectors
    tm_infervec = model.infer_vector(usertok, steps=200, alpha=0.025, min_alpha=0.001)
    tm_mostsim = model.docvecs.most_similar(positive=[tm_infervec], topn=model.docvecs.count)

    # merge data
    tm_table = pd.DataFrame(tm_mostsim)
    tm_table.columns = ['id','cosine']

    tm_table['id'] = tm_table['id'].apply(int)

    tm_distinfo = pd.merge(tm_table, aotable[['id', 'lat', 'lng']],
                           on='id', how='left')

    # create tags for good, intermediate and bad recommendations
    tm_distinfo['category'] = pd.cut(
        tm_distinfo['cosine'],
        [-np.inf, tm_distinfo['cosine'].quantile(0.50),
        tm_distinfo['cosine'].quantile(0.99), np.inf],
        labels=['bad', 'meh', 'good']
    )

    # If the user doesn't add a filter:
    if filt_dist != '' and filt_loc != '':
      usrlocation = filt_loc
      try:
        locgeo = gmaps.geocode(usrlocation)[0]['geometry']['location']
        mess = 'Filtering:'
        tm_distinfo['distance'] = [auxfxns.haversine(locgeo['lng'], locgeo['lat'], row['lng'], row['lat']) for index,row in tm_distinfo.iterrows()]
        usrdist = int(filt_dist)
        tabletop10 = tm_distinfo[tm_distinfo['distance'] <= usrdist].reset_index(drop = True).head(8)
      except:
        mess = 'Failed to connect to Google Maps, returning results around the world...'
        tabletop10 = tm_distinfo.head(8)
    elif (filt_dist == '' and filt_loc != '') or (filt_dist != '' and filt_loc == ''):
      tabletop10 = tm_distinfo.head(8)
      mess = 'Incomplete filters! Returning results around the world...'
    else:
      tabletop10 = tm_distinfo.head(8)
      mess = ''

    tm_filter_final = pd.merge(tabletop10, aotable, on='id', how='left').head(8).reset_index(drop = True)

    tm_filter_final['keywords'] = [re.sub(',', ', ', x) for x in tm_filter_final['keywords']]

    auxfxns.generatemap(tm_filter_final)

    return render_template('output.html', usr_t = usertok,
                           f_dist = filt_dist, f_loc = filt_loc,
                           outtable = tm_filter_final,
                           message=mess)

@app.route('/slides')
def view_presentation():
    return render_template('slides.html', title='Demo Presentation')
