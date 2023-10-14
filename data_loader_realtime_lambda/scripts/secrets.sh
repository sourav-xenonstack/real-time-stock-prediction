#!/bin/bash

# This script exports environment variables required for InfluxDB connectivity.

# Set the InfluxDB access token for authentication.
export influxdb_token=qHwRxwIgh6sxOCZcDO-7TASrjCAdLT0ZwvkJYPfgA==

# Set the InfluxDB organization name.
export influxdb_org=org

# Set the InfluxDB URL to establish a connection.
export influxdb_url=http://localhost:8086

# Set the InfluxDB bucket where stock data will be stored.
export influxdb_bucket=stock_data

export baseUrl=https://www.alphavantage.co/query

export symbol=IBM

export interval=5min

export apikey=PZ270Q18B48YH9PF

export function=TIME_SERIES_INTRADAY