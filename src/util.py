
import logging
import time
from datetime import datetime

from pyflink.table import DataTypes
from pyflink.table.udf import udf



@udf(input_types=[DataTypes.DECIMAL(11, 2)], result_type=DataTypes.STRING())
def ts2str(data):
    try:
        data = int(data)
        return datetime.fromtimestamp(data).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        logging.error('parse err:', str(e))
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

