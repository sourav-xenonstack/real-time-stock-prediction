# Financial Data Loader Project

This project demonstrates a Python application for fetching financial data from the Alpha Vantage API, processing it, and storing it in InfluxDB while concurrently sending the data to an SQS queue. The application is organized into a `FinancialDataLoader` class that encapsulates the functionality for data processing and sending.

## Prerequisites

- Python 3.6 or higher
- Required Python packages (install using `pip`):
  - `requests`: For making HTTP requests to the Alpha Vantage API.
  - `influxdb-client`: For interacting with InfluxDB.
  - `boto3`: For interacting with AWS SQS.

## Configuration

Ensure you have the necessary environment variables set up in your system or in a configuration file. The following environment variables are required for the application to run:

- `baseUrl`: URL for Alpha Vantage API to get stock data.
- `function`: Time series function to get stock data (e.g., Intraday).
- `symbol`: Symbol of stock data (e.g., AAPL for Apple).
- `interval`: Time series interval (e.g., 5 minutes).
- `apikey`: API key for Alpha Vantage API.
- `influxUrl`: URL for InfluxDB instance.
- `token`: Token for InfluxDB instance.
- `org`: Organization for InfluxDB.
- `bucket`: Bucket name of InfluxDB.
- `aws_access_key`: AWS access key for SQS.
- `aws_secret_key`: AWS secret key for SQS.
- `aws_region`: AWS region for SQS.

## Usage

1. **Initialize Connection:**

   Initialize necessary connections before using the `FinancialDataLoader` class. The `ConnectionInitializer` class is provided to handle AWS and InfluxDB connections. Example usage:

   ```python
   from connection_initializer import ConnectionInitializer

   connection_initializer = ConnectionInitializer()
   sqs_client = connection_initializer.initialize_aws_connection()
   influxdb_client = connection_initializer.initialize_influxdb_connection()
   ```

2. **Fetch and Process Data:**

   ```python
   from financial_data_loader import FinancialDataLoader

   data_loader = FinancialDataLoader(sqs_client, influxdb_client)
   data = data_loader.get_data_from_api()
   data_loader.process_and_send_data_concurrently(data)
   ```

   The `process_and_send_data_concurrently` method of `FinancialDataLoader` class processes data and sends it to both InfluxDB and SQS concurrently.

## Run the Application

Run the Python script to fetch, process, and send financial data:

```bash
python lambda_handler.py
```

Make sure the necessary environment variables are set before running the script.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.