# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import os

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Precipitation = Base.classes.precipitation
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
#    """List all available routes."""
     return (
         f"Available Routes:<br/>"
         f"/api/v1.0/precipitation<br/>"
         f"/api/v1.0/stations<br/>"
         f"/api/v1.0/tobs<br/>"
         f"/api/v1.0/<start><br/>"
         f"/api/v1.0/<start>/<end><br/>")

@app.route("/api/v1.0/precipitation")
def precipitation():
#     """Return the JSON representation of precipitation data for the last 12 months."""
    # Query the last 12 months of precipitation data
    last_12_months = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').all()
    # Convert the query results to a dictionary with date as the key and prcp as the value
    precipitation_data = {date: prcp for date, prcp in last_12_months}
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
#     """Return a JSON list of stations from the dataset."""
#   # Query all the unique station names
    stations = session.query(Station.station).all()
    # Convert the query results to a list
    station_list = [station[0] for station in stations]
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
#     """Return a JSON list of temperature observations for the previous year."""
#     # Query the dates and temperature observations of the most-active station for the previous year of data
     last_12_months_temps = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= '2016-08-23').all()
     # Convert the query results to a list of dictionaries
     temperature_data = []
     for date, tobs in last_12_months_temps:
         temperature_data.append({"Date": date, "Temperature": tobs})
     return jsonify(temperature_data)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start=None, end=None):
#     """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range."""
#     # Define the query based on the provided start and end dates
     if end:
         temperature_data = session.query(func.min(Measurement.tobs).label("TMIN"),
                                          func.avg(Measurement.tobs).label("TAVG"),
                                          func.max(Measurement.tobs).label("TMAX")).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
     else:
         temperature_data = session.query(func.min(Measurement.tobs).label("TMIN"),
                                          func.avg(Measurement.tobs).label("TAVG"),
                                          func.max(Measurement.tobs).label("TMAX")).filter(Measurement.date >= start).all()
     # Create a dictionary to hold the results
     temperature_stats = {
         "Start Date": start,
         "End Date": end,
         "TMIN": temperature_data[0][0],
         "TAVG": temperature_data[0][1],
         "TMAX": temperature_data[0][2]
     }
     return jsonify(temperature_stats)

if __name__ == "__main__":
    app.run(debug=True)
