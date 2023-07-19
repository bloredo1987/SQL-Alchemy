# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import os
import pandas as pd

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
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
         f"/api/v1.0/&lt;start&gt;<br/>"
         f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
     )

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
    """Return a JSON list of stations from the dataset."""
    # Create a new session within the function to ensure thread safety
    session = Session(engine)
    
    # Query all unique station names
    results = session.query(Station.station).distinct().all()
    # Convert the query results to a list
    stations_data = [station[0] for station in results]

    # Close the session to release resources
    session.close()
    
    return jsonify(stations_data)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most-active station for the previous year of data."""
    # Calculate the date one year from the last date in the data set
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = pd.to_datetime(most_recent_date).strftime('%Y-%m-%d')
    one_year_ago = (pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
    
    # Query temperature data for the most-active station for the last 12 months
    most_active_station = session.query(Measurement.station)\
                                 .group_by(Measurement.station)\
                                 .order_by(func.count(Measurement.station).desc())\
                                 .first()
    most_active_station = most_active_station[0]
    
    temperature_data = session.query(Measurement.tobs)\
                              .filter(Measurement.station == most_active_station,
                                      Measurement.date >= one_year_ago,
                                      Measurement.date <= most_recent_date)\
                              .all()
    
    # Convert the query results to a list
    temperatures = [temp[0] for temp in temperature_data]
    
    return jsonify(temperatures)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_summary(start, end=None):
    """Query the temperature summary (TMIN, TAVG, TMAX) for a specified start or start-end range."""
    # Perform the query based on the provided start and end dates
    if end:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).all()
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    # Create a summary dictionary
    summary_data = {
        "start_date": start,
        "end_date": end,
        "min_temperature": results[0][0],
        "avg_temperature": results[0][1],
        "max_temperature": results[0][2]
    }
    
    return jsonify(summary_data)

if __name__ == "__main__":
    app.run(debug=True)
