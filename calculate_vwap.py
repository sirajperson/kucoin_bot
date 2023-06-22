import pandas as pd

def calculate_vwap(data):
    vwap = (data['Close'] * data['Volume']).cumsum() / data['Volume'].cumsum()
    return vwap
