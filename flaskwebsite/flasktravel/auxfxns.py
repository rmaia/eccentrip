from nltk.tokenize import RegexpTokenizer
from math import radians, cos, sin, asin, sqrt
import folium
import numpy as np

'''
Calculate the great circle distance between two points
on the earth (specified in decimal degrees)
'''
def haversine(lon1, lat1, lon2, lat2):

      # convert decimal degrees to radians
      lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
      # haversine formula
      dlon = lon2 - lon1
      dlat = lat2 - lat1
      a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
      c = 2 * asin(sqrt(a))
      # Radius of earth in miles is 3,959
      mi = 3959* c
      return mi


'''
Tokenize the user input search
'''

def usertokens(usrtok):
      usrtok = usrtok.replace(u'\xa0', u' ')
      usrtok = usrtok.replace(u'\xa0', u' ')
      usrtok = usrtok.replace(u'/', u' ')
      usrtok = usrtok.replace(u'\\', u' ')
      usrtok = usrtok.replace(u'\u201C', '"')
      usrtok = usrtok.replace(u'\u201D', '"')
      usrtok = usrtok.replace(u'\u2018', '\'')
      usrtok = usrtok.replace(u'\u2019', '\'')
      usrtok = usrtok.replace('…', '\'')
      usrtok = usrtok.replace('\t', ' ')
      usrtok = usrtok.replace(r"[^A-Za-z0-9(),!?@\'\`\"\_\n]", " ")
      usrtok = usrtok.replace(r"[\'\`]s", "")
      usrtok = usrtok.lower()

      # Pad punctuation with spaces on both sides
      for char in ['.', '"', ',', '(', ')', '!', '?', ';', ':']:
          usrtok = usrtok.replace(char, ' ' + char + ' ')

      usrtok = RegexpTokenizer(r'\w+').tokenize(usrtok)

      return usrtok


'''
Generate the map and the location markers
'''

def generatemap(dframe):

      usrmap = folium.Map(list(dframe[['lat_x','lng_x']].apply(np.mean).values), zoom_start=2, width=1000,height=500)

      for index, row in dframe.iterrows():
          coords = (row['lat_x'], row['lng_x'])

          html = '<center><h2>'+ row['title'] +  '''</h2>
          <h4>''' + row['subtitle'] + '''</h4>
          OddScore: ''' + str(round(row['weirdpct'],2)) + '''% <br>
          <img src="''' + row['imgurl'] + '''" class="center" height="200">
          <br>tags: ''' + row['keywords'] +'''
          </center>'''

          iframe = folium.IFrame(html=html, width=300, height=300)
          popup = folium.Popup(iframe, max_width=2650)

          if row['category'] == 'good':
            iconcol = 'green'
          elif row['category'] == 'meh':
            iconcol = 'orange'
          else:
            iconcol = 'red'


          point = folium.Marker(coords,
                                icon=folium.Icon(color=iconcol, icon='circle'),
                                popup=popup,
                                tooltip=row['title']).add_to(usrmap)

      usrmap.save('flasktravel/templates/map-output.html')

      # clean the bootstrap HTML that is auto-generated
      savedmap = open('flasktravel/templates/map-output.html', 'r')
      smap = savedmap.read()
      savedmap.close()
      smap = smap.replace('<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>','')
      smap = smap.replace('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css"/>','')
      smap = smap.replace('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap-theme.min.css"/>','')
      smap = smap.replace('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.6.3/css/font-awesome.min.css"/>','')

      tosavemap = open('flasktravel/templates/map-output-clean.html', 'w')
      tosavemap.write(smap)
      tosavemap.close()

      return None

