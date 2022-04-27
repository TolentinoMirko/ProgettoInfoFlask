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

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")





if __name__ == '__main__':
  app.run(host='0.0.0.0', port=1234, debug=True)