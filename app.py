
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify
from collections import Counter
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
# Create the inspector and connect it to the engine
inspector = inspect(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#################################################
# Flask Routes
#################################################

climate_app = "..............."
precipitation_app = "http://127.0.0.1:5000/api/v1.0/precipitation"
station_app = "http://127.0.0.1:5000/api/v1.0/stations" 
tobs_app = "http://127.0.0.1:5000/api/v1.0/tobs"
start_date = "http://127.0.0.1:5000/api/v1.0/2018-08-23"
start_end_date =  "http://127.0.0.1:5000/api/v1.0/2017-08-23/2018-08-23"

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    """Return the precipitation data for the last year"""
    # Retrieve the last 12 months of precipitation data
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    session.close()
    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    
    return jsonify(precip)

    
    # one_year = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).order_by(Measurement.date.desc()).all()
    # precip = []
    # for date, prcp in one_year:
    #     date_dict = {}
    #     date_dict['date'] = date
    #     date_dict['prcp']= prcp
    #     precip.append(date_dict)

    # return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    session = Session(engine)

    station_act = session.query(Measurement.station, Station.name, func.count(Measurement.tobs)).\
        filter(Measurement.station == Station.station).group_by(Measurement.station).\
        order_by(func.count(Measurement.tobs).desc()).all()

    # Convert dictionary data form into list using list(np.ravel())
    list_station = list(np.ravel(station_act))
    
    session.close()
    
    return jsonify(list_station)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    session = Session(engine)
    """Return the temperature observations (tobs) for previous year."""

    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    session.close()
    # Query the last 12 months of temperature observation data for these stations
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    
    # Return the results
    return jsonify(temps)
 

@app.route("/api/v1.0/<start>")
def temp1_start(start):
    start_date = start
    end_date = dt.date.today()

    results = calc_temps(start_date, end_date)

    return jsonify(results)


@app.route("/api/v1.0/<start>/<end>")
def temp2_start(start, end):
    start_date = start
    end_date = end 

    results = calc_temps(start_date, end_date)

    return jsonify(results)

def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

    return results


if __name__ == '__main__':
    app.run(debug = True)