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




@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/selezione", methods=["GET"])
def selezione():
    m = folium.Map(location=[45.46, 9.18], zoom_start=11, tiles='CartoDB positron')
    tooltip = "Click me!"

    folium.Marker(location=[45.46, 9.18], popup="<i>boh</i>", tooltip=tooltip).add_to(m)

    shapes = gpd.GeoSeries(quartieri['geometry']).simplify(tolerance=0.00001)
    shapes = shapes.to_json()
    shapes = folium.GeoJson(data=shapes, style_function=lambda x: {'fillColor': 'blue'})
    shapes.add_to(m)

    return render_template("selezione.html", map=m._repr_html_())


  
#fontanelle




#stazionibici



#supermercato



#tabaccheria



if __name__ == '__main__':
  app.run(host='0.0.0.0', port=1234, debug=True)