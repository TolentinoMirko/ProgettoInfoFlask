from flask import Flask, render_template, send_file, make_response, url_for, Response,request,redirect
app = Flask(__name__)

import io
import geopandas as gpd
import contextily
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import folium

# pip install flask geopandas matplotlib contextily pandas folium

quartieri = gpd.read_file('/workspace/ProgettoInfoFlask/static/ds964_nil_wm-20220502T120333Z-001.zip')
scuole = gpd.read_file('/workspace/ProgettoInfoFlask/static/ds1305_elenco_scuole_statali_as2020_21_def_final_.geojson')
impianti_sportivi = gpd.read_file('/workspace/ProgettoInfoFlask/static/impianti_sportivi_11_06_2020.geojson')
fermate_tram = gpd.read_file('/workspace/ProgettoInfoFlask/static/tpl_fermate.geojson')
fermate_metro = gpd.read_file('/workspace/ProgettoInfoFlask/static/tpl_metrofermate.geojson')


scuole.to_crs(4326)
scuole['lon'] = scuole['geometry'].x
scuole['lat'] = scuole['geometry'].y 


@app.route("/", methods=["GET"])
def home():

    scuolelista = scuole.DENOMINAZIONESCUOLA.drop_duplicates()
    scuolelista = scuolelista.to_list()
    scuolelista.sort()
    
    return render_template("home.html",istituti = scuolelista)

@app.route("/selezione", methods=["GET"])
def selezione():
    global scuolautente
    scuolascelta = request.args['scuoledropdown']
    
    m = folium.Map(location=[45.46, 9.18], zoom_start=11, tiles='CartoDB positron')
    
    tooltip = "Cliccami!",
    
    scuolautente = scuole[scuole['DENOMINAZIONESCUOLA']==scuolascelta]
    scuola_long = scuolautente['LONG_X']
    scuola_lat = scuolautente['LAT_Y']
    scuola_nome = scuolautente['DENOMINAZIONESCUOLA']
    info = [scuola_nome,scuola_lat,scuola_long]

    folium.Marker(location=[scuola_lat,scuola_long], popup=info, tooltip=tooltip).add_to(m)

    shapes = gpd.GeoSeries(quartieri['geometry']).simplify(tolerance=0.00001)
    shapes = shapes.to_json()
    shapes = folium.GeoJson(data=shapes, style_function=lambda x: {'fillColor': 'blue'})
    shapes.add_to(m)

    return render_template("selezione.html", map=m._repr_html_())


  
#campi sportivi
@app.route("/campisportivi", methods=["GET"])
def campi():
    dist_campi = impianti_sportivi.distance(scuolautente)
    min_dist = impianti_sportivi[impianti_sportivi.distance(scuolautente) <= dist_campi.min()]
    print(min_dist)
    return render_template("mappa.html")



#ristoranti
@app.route("/ristoranti", methods=["GET"])
def ristoranti():


    return render_template("mappa.html")



#tram
@app.route("/tram", methods=["GET"])
def tram():


    return render_template("mappa.html")



#metropolitane
@app.route("/metropolitane", methods=["GET"])
def metropolitane():


    return render_template("mappa.html")




if __name__ == '__main__':
  app.run(host='0.0.0.0', port=2000, debug=True)