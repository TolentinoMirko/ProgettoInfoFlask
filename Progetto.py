import folium
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import contextily
import geopandas as gpd
import io
from shapely.geometry import Point, MultiPoint
from shapely.ops import nearest_points
from flask import Flask, render_template, send_file, make_response, url_for, Response, request, redirect
app = Flask(__name__)

matplotlib.use('Agg')

# pip install flask geopandas matplotlib contextily pandas folium

quartieri = gpd.read_file(
    '/workspace/ProgettoInfoFlask/static/ds964_nil_wm-20220502T120333Z-001.zip')
scuole = gpd.read_file(
    '/workspace/ProgettoInfoFlask/static/ds1305_elenco_scuole_statali_as2020_21_def_final_.geojson')
impianti_sportivi = gpd.read_file(
    '/workspace/ProgettoInfoFlask/static/impianti_sportivi_11_06_2020.geojson')
ristoranti_GPD = gpd.read_file(
    '/workspace/ProgettoInfoFlask/static/economia_pubblici_esercizi_in_piano.geojson')
fermate_tram = gpd.read_file(
    '/workspace/ProgettoInfoFlask/static/tpl_fermate.geojson')
fermate_metro = gpd.read_file(
    '/workspace/ProgettoInfoFlask/static/tpl_metrofermate.geojson')

#creazione colonne longitudine latitudine nel geodatagrame fermate_tram

fermate_tram['lon'] = fermate_tram['geometry'].x
fermate_tram['lat'] = fermate_tram['geometry'].y

#creazione colonne longitudine latitudine nel geodatagrame fermate_metro

fermate_metro['lon'] = fermate_metro['geometry'].x
fermate_metro['lat'] = fermate_metro['geometry'].y

@app.route("/", methods=["GET"])
def home():
    scuolelista = scuole.DENOMINAZIONESCUOLA.drop_duplicates()
    scuolelista = scuolelista.to_list()
    scuolelista.sort()

    return render_template("home.html", istituti=scuolelista)

@app.route("/selezione", methods=["GET"])
def selezione():
    global scuolautente, info, scuola_lat, scuola_long 

    scuolascelta = request.args['scuoledropdown']
    #creazione mappa 
    m = folium.Map(location=[45.4654219, 9.1859243],
                   zoom_start=11, tiles='CartoDB positron')

    tooltip = "Cliccami!",

    scuolautente = scuole[scuole['DENOMINAZIONESCUOLA'] == scuolascelta]
    
    scuola_long = scuolautente['LONG_X']
    scuola_lat = scuolautente['LAT_Y']
    scuola_nome = scuolautente['DENOMINAZIONESCUOLA']
    scuola_via = scuolautente['INDIRIZZOSCUOLA']
    info = [scuola_nome,scuola_via]

    folium.Marker(location=[scuola_lat, scuola_long],
                  popup=info, tooltip=tooltip).add_to(m)

    shapes = gpd.GeoSeries(quartieri['geometry']).simplify(tolerance=0.00001)
    shapes = shapes.to_json()
    shapes = folium.GeoJson(data=shapes, style_function=lambda x: {
                            'fillColor': 'blue'})
    shapes.add_to(m)
    return render_template("selezione.html", map=m._repr_html_())
#____________________________________________________________________________________________________________________________

# campi sportivi
@app.route("/campisportivi", methods=["GET"])
def campi():

    puntoscuola = scuolautente['geometry'].to_crs(32632).values[0]
    dist_campi = impianti_sportivi.to_crs(32632).distance(puntoscuola)
    min_dist = impianti_sportivi[impianti_sportivi.to_crs(
        32632).distance(puntoscuola) <= dist_campi.min()].iloc[0]

    campo_lat = min_dist['Latitudine']
    campo_long = min_dist['Longitudine']
    campo_via = min_dist['VIA']
    campo_nome = min_dist['SPECIFICA_LOCALITA']
    campo_localita = min_dist['LOCALITA']
   
    info2 = [campo_nome,campo_via,campo_localita]
    m = folium.Map(location=[45.4654219, 9.1859243],
                   zoom_start=12, tiles='CartoDB positron')

    tooltip = "Cliccami!",
   
    folium.Marker(location=[scuola_lat, scuola_long],popup=info
                  , tooltip=tooltip).add_to(m)
    folium.Marker(location=[campo_lat, campo_long],popup=info2, tooltip=tooltip).add_to(m)

    shapes = gpd.GeoSeries(quartieri['geometry']).simplify(tolerance=0.00001)
    shapes = shapes.to_json()
    shapes = folium.GeoJson(data=shapes, style_function=lambda x: {
                            'fillColor': 'blue'})
    shapes.add_to(m)
    return render_template("mappa.html", map=m._repr_html_())
#____________________________________________________________________________________________________________________________

# ristoranti
@app.route("/ristoranti", methods=["GET"])
def ristoranti():
    puntoscuola = scuolautente['geometry'].to_crs(32632).values[0]
    dist_ristorante = ristoranti_GPD.to_crs(32632).distance(puntoscuola)
    min_ristorante = ristoranti_GPD[ristoranti_GPD.to_crs(
        32632).distance(puntoscuola) <= dist_ristorante.min()].iloc[0]

    ris_lat = min_ristorante['LAT_WGS84']
    ris_long = min_ristorante['LONG_WGS84']
    nome_ristorante = min_ristorante['insegna']
    print(nome_ristorante)
    rist_via = min_ristorante['Ubicazione']
    info2 = [nome_ristorante,rist_via]
    m = folium.Map(location=[45.4654219, 9.1859243],
                   zoom_start=12, tiles='CartoDB positron')

    tooltip = "Cliccami!",
    folium.Marker(location=[scuola_lat, scuola_long],
                  popup=info, tooltip=tooltip).add_to(m)
    folium.Marker(location=[ris_lat, ris_long],popup= info2 ,tooltip=tooltip).add_to(m)

    shapes = gpd.GeoSeries(quartieri['geometry']).simplify(tolerance=0.00001)
    shapes = shapes.to_json()
    shapes = folium.GeoJson(data=shapes, style_function=lambda x: {
                            'fillColor': 'blue'})
    shapes.add_to(m)
    return render_template("mappa.html", map=m._repr_html_())
#____________________________________________________________________________________________________________________________

# tram
@app.route("/tram", methods=["GET"])
def tram():
    lista_linee_tram = fermate_tram.linee.drop_duplicates()
    lista_linee_tram = lista_linee_tram.to_list()
    lista_linee_tram.sort()
    return render_template("scelta_linea_tram.html", fermate=lista_linee_tram)

@app.route("/trampunto", methods=["GET"])
def trampunto():
    linea_utente = request.args['fermatedropdown']
    linea_scelta = fermate_tram.loc[fermate_tram['linee'].str.contains(linea_utente,case=False)]

    puntoscuola = scuolautente['geometry'].to_crs(32632).values[0]
    dist_fermate_tram = linea_scelta.to_crs(32632).distance(puntoscuola)
    min_fermata_tram = linea_scelta[linea_scelta.to_crs(32632).distance(puntoscuola) <= dist_fermate_tram.min()].iloc[0]
    
    ris_lat = min_fermata_tram['lat']
    ris_long = min_fermata_tram['lon']
    num_linea = min_fermata_tram['linee']
    via_fermata = min_fermata_tram['ubicazione']
    info2 = [num_linea,via_fermata]

    m = folium.Map(location=[45.4654219, 9.1859243],
                   zoom_start=12, tiles='CartoDB positron')

    tooltip = "Cliccami!",
    folium.Marker(location=[scuola_lat, scuola_long],
                  popup=info, tooltip=tooltip).add_to(m)
    folium.Marker(location=[ris_lat, ris_long],popup= info2 ,tooltip=tooltip).add_to(m)

    shapes = gpd.GeoSeries(quartieri['geometry']).simplify(tolerance=0.00001)
    shapes = shapes.to_json()
    shapes = folium.GeoJson(data=shapes, style_function=lambda x: {
                            'fillColor': 'blue'})
    shapes.add_to(m)
    return render_template("mappa.html", map=m._repr_html_())
#____________________________________________________________________________________________________________________________

# metropolitane
@app.route("/metropolitane", methods=["GET"])
def metropolitane():
    lista_linee_metro = fermate_metro.linee.drop_duplicates()
    lista_linee_metro = lista_linee_metro.to_list()
    lista_linee_metro.sort()

    return render_template("scelta_linea_metro.html",fermate = lista_linee_metro)

@app.route("/metropunto", methods=["GET"])
def metropunto():
    linea_utente = request.args['fermatedropdown']
    linea_scelta = fermate_metro.loc[fermate_metro['linee'].str.contains(linea_utente,case=False)]

    puntoscuola = scuolautente['geometry'].to_crs(32632).values[0]
    dist_fermate_metro = linea_scelta.to_crs(32632).distance(puntoscuola)
    min_fermata_metro = linea_scelta[linea_scelta.to_crs(32632).distance(puntoscuola) <= dist_fermate_metro.min()].iloc[0]

    ris_lat = min_fermata_metro['lat']
    ris_long = min_fermata_metro['lon']
    num_linea = min_fermata_metro['linee']
    nome_linea = min_fermata_metro['nome']
    info2 = [num_linea,nome_linea]
    m = folium.Map(location=[45.4654219, 9.1859243],
                   zoom_start=12, tiles='CartoDB positron')

    tooltip = "Cliccami!",
    folium.Marker(location=[scuola_lat, scuola_long],
                  popup=info, tooltip=tooltip).add_to(m)
    folium.Marker(location=[ris_lat, ris_long],popup = info2,tooltip=tooltip).add_to(m)

    shapes = gpd.GeoSeries(quartieri['geometry']).simplify(tolerance=0.00001)
    shapes = shapes.to_json()
    shapes = folium.GeoJson(data=shapes, style_function=lambda x: {
                            'fillColor': 'blue'})
    shapes.add_to(m)
    return render_template("mappa.html", map=m._repr_html_())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2000, debug=True)
