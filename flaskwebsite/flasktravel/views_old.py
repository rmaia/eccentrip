from flasktravel import app
from flask import render_template
from flask import request
import pickle
import gensim
import re
import codecs
import json
from bs4 import BeautifulSoup as bs


@app.route('/')
@app.route('/index')

def view_method():
    with open('flasktravel/Doc2VecModelStuff', 'rb') as inusrfile:
      aotable = pickle.load(inusrfile)

    dropdown_list = sorted(list(aotable['title']))
    return render_template('index.html', title='Home', dropdown_list=dropdown_list)


@app.route('/output', methods=['GET', 'POST'])

def output():
    with open('flasktravel/Doc2VecModelStuff', 'rb') as inusrfile:
      aotable = pickle.load(inusrfile)
      allao = pickle.load(inusrfile)
      model = pickle.load(inusrfile)

    # pull the input location
    usr_select = request.form.get('inputform')

    # pull the data from the input location
    usr_descript = aotable[aotable['title'] == usr_select]['description'].values[0]
    usr_keywords = aotable[aotable['title'] == usr_select]['keywords'].values[0]
    usr_keywords = re.sub(',', ', ', usr_keywords)

    try:
      # pull in thumbnail
      usrurlpath = usr_select.lower().replace(' ','-')
      usrurlpath = 'jsons/'+usrurlpath+'.html'
      usrurlpath = usrurlpath.replace('-.','.')
      usrfile = codecs.open(usrurlpath, 'r')
      bsusrfile = bs(usrfile, 'html.parser')
      bsusrfilejson = bsusrfile.find('script', string=re.compile('AtlasObscura.current_place')).text
      bsusrfilejson =  re.sub('(\s+)|(;)|(AtlasObscura.current_place = )', ' ', bsusrfilejson)
      usrimgurl = json.loads(bsusrfilejson)['thumbnail_url']
    except:
      usrimgurl = ''


    # FIND THE TOP MATCH

    # get the index
    doc_id = aotable[aotable['title']== usr_select].index.values[0]
    # use the index to get the most similar places
    top_rec = model.docvecs.most_similar(doc_id, topn = 1)
    top_name = top_rec[0][0]

    top_descript = aotable[aotable['title'] == top_name]['description'].values[0]
    top_keywords = aotable[aotable['title'] == top_name]['keywords'].values[0]
    top_keywords = re.sub(',', ', ', top_keywords)

    try:
      # pull in thumbnail
      topurlpath = top_name.lower().replace(' ','-')
      topurlpath = 'jsons/'+topurlpath+'.html'
      topurlpath = topurlpath.replace('-.','.')
      topfile = codecs.open(topurlpath, 'r')
      bstopfile = bs(topfile, 'html.parser')
      bstopfilejson = bstopfile.find('script', string=re.compile('AtlasObscura.current_place')).text
      bstopfilejson =  re.sub('(\s+)|(;)|(AtlasObscura.current_place = )', ' ', bstopfilejson)
      topimgurl = json.loads(bstopfilejson)['thumbnail_url']
    except:
      topimgurl = ''






    return render_template('output.html',
                           usrselection = usr_select,
                           usrkeywords = usr_keywords,
                           usrdescription = usr_descript,
                           usrimgurl=usrimgurl,

                           topselection = top_name,
                           topkeywords = top_keywords,
                           topdescription = top_descript,
                           topimgurl=topimgurl
                           )

