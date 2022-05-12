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


# scuole.to_crs(4326)
#scuole['lon'] = scuole['geometry'].x
#scuole['lat'] = scuole['geometry'].y


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

    m = folium.Map(location=[45.46, 9.18],
                   zoom_start=11, tiles='CartoDB positron')

    tooltip = "Cliccami!",

    scuolautente = scuole[scuole['DENOMINAZIONESCUOLA'] == scuolascelta]
    print(scuolautente)

    scuola_long = scuolautente['LONG_X']
    scuola_lat = scuolautente['LAT_Y']
    scuola_nome = scuolautente['DENOMINAZIONESCUOLA']
    info = [scuola_nome, scuola_lat, scuola_long]

    folium.Marker(location=[scuola_lat, scuola_long],
                  popup=info, tooltip=tooltip).add_to(m)

    shapes = gpd.GeoSeries(quartieri['geometry']).simplify(tolerance=0.00001)
    shapes = shapes.to_json()
    shapes = folium.GeoJson(data=shapes, style_function=lambda x: {
                            'fillColor': 'blue'})
    shapes.add_to(m)

    return render_template("selezione.html", map=m._repr_html_())


# campi sportivi
@app.route("/campisportivi", methods=["GET"])
def campi():

    puntoscuola = scuolautente['geometry'].to_crs(32632).values[0]
    dist_campi = impianti_sportivi.to_crs(32632).distance(puntoscuola)
    min_dist = impianti_sportivi[impianti_sportivi.to_crs(
        32632).distance(puntoscuola) <= dist_campi.min()].iloc[0]

    print(min_dist)

    campo_lat = min_dist['Latitudine']
    campo_long = min_dist['Longitudine']
    m = folium.Map(location=[45.46, 9.18],
                   zoom_start=11, tiles='CartoDB positron')

    tooltip = "Cliccami!",
   
    folium.Marker(location=[scuola_lat, scuola_long],
                  popup=info, tooltip=tooltip).add_to(m)
    folium.Marker(location=[campo_lat, campo_long], tooltip=tooltip).add_to(m)

    shapes = gpd.GeoSeries(quartieri['geometry']).simplify(tolerance=0.00001)
    shapes = shapes.to_json()
    shapes = folium.GeoJson(data=shapes, style_function=lambda x: {
                            'fillColor': 'blue'})
    shapes.add_to(m)

    return render_template("mappa.html", map=m._repr_html_())


# ristoranti
@app.route("/ristoranti", methods=["GET"])
def ristoranti():
    puntoscuola = scuolautente['geometry'].to_crs(32632).values[0]
    dist_ristorante = ristoranti_GPD.to_crs(32632).distance(puntoscuola)
    min_ristorante = ristoranti_GPD[ristoranti_GPD.to_crs(
        32632).distance(puntoscuola) <= dist_ristorante.min()].iloc[0]

    print(min_ristorante)

    ris_lat = min_ristorante['LAT_WGS84']
    ris_long = min_ristorante['LONG_WGS84']
    nome_campo = min_ristorante['VIA']

    m = folium.Map(location=[45.46, 9.18],
                   zoom_start=11, tiles='CartoDB positron')

    tooltip = "Cliccami!",
    folium.Marker(location=[scuola_lat, scuola_long],
                  popup=info, tooltip=tooltip).add_to(m)
    folium.Marker(location=[ris_lat, ris_long],popup= nome_campo ,tooltip=tooltip).add_to(m)

    shapes = gpd.GeoSeries(quartieri['geometry']).simplify(tolerance=0.00001)
    shapes = shapes.to_json()
    shapes = folium.GeoJson(data=shapes, style_function=lambda x: {
                            'fillColor': 'blue'})
    shapes.add_to(m)

    return render_template("mappa.html", map=m._repr_html_())


# tram
@app.route("/tram", methods=["GET"])
def tram():
    lista_linee_tram = fermate_tram.drop_duplicates()
    lista_linee_tram = lista_linee_tram.to_list()
    lista_linee_tram.sort_values()
    return render_template("sceltalinee.html", fermate=lista_linee_tram)


@app.route("/trampunto", methods=["GET"])
def trampunto():

    return render_template("mappa.html")


# metropolitane
@app.route("/metropolitane", methods=["GET"])
def metropolitane():

    return render_template("mappa.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2000, debug=True)
