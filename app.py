import numpy as np

import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/%3Cstart%3E<br/>"
        f"/api/v1.0/%3Cstart%3E/%3Cend%3E"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    results = session.query(Measurement.date,Measurement.prcp).all()

    session.close()

     # Create a dictionary from the row data and append to a list of all_prcp
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #first_row = session.query(Station).first()
    results = session.query(Station.station).all()

    session.close()
    
    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    most_active = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).\
    first().station

    date_str = session.query(Measurement.date).filter(Measurement.station == most_active).order_by(Measurement.date.desc()).first().date


    year_ago = dt.date(2017,8, 18) - dt.timedelta(days=365)

    tobs_of_mostactive = session.query(Measurement.tobs).\
                        filter(Measurement.date > year_ago ).\
                        filter(Measurement.station == most_active).all()

    session.close()
    
    return jsonify(tobs_of_mostactive)

@app.route("/api/v1.0/<start>")
def temp_min_max_avg_start(start):
    session = Session(engine)

    #start = '2016-08-23'

    min_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date > start).all()

    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date > start).all()

    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date > start).all()

    result = [min_temp[0],avg_temp[0],max_temp[0]]

    session.close()
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
