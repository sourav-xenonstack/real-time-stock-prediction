"""
financial_data_loader.py

This module provides classes and functions for loading financial data from the Alpha Vantage API,
sending it to an SQS queue, and storing it in InfluxDB. It also includes a utility class for initializing
connections to AWS services and InfluxDB.

Classes:
    - FinancialDataLoader: A class for loading financial data and interacting with AWS SQS and InfluxDB.
    - ConnectionInitializer: A class for initializing connections to AWS SQS and InfluxDB.

Module Dependencies:
    - os: Provides a way to access environment variables.
    - botocore.client.SQS: AWS SDK for Python (Boto3) client for Simple Queue Service (SQS).
    - influxdb_client.client.write_api.WriteApi: InfluxDB Python client for writing data to InfluxDB.

Usage:
    1. Create an instance of ConnectionInitializer to initialize AWS and InfluxDB connections.
    2. Create an instance of FinancialDataLoader, providing initialized SQS and InfluxDB clients.
    3. Use the methods of FinancialDataLoader to fetch data from Alpha Vantage API, send messages to SQS,
       and store data in InfluxDB.

Example:
    # Initialize SQS and InfluxDB clients
    connection_initializer = ConnectionInitializer()
    sqs_client = connection_initializer.initialize_aws_connection()
    influxdb_client = connection_initializer.initialize_influxdb_connection()

    # Create an instance of FinancialDataLoader
    data_loader = FinancialDataLoader(sqs_client, influxdb_client)

    # Use the methods of data_loader to handle financial data.
"""
# TODO:
# FIXME:

# Import Dependencies
import json
import os

import boto3
import requests
import influxdb_client
import concurrent.futures
from botocore.exceptions import ClientError
from influxdb_client.rest import ApiException

from src.logger import create_logger

# Set up logger
logger = create_logger("info", "logger")

class ConnectionInitializer:
    """
    A class responsible for initializing AWS SQS and InfluxDB connections.

    Attributes:
        aws_access_key (str): AWS Access Key ID obtained from environment variables.
        aws_secret_key (str): AWS Secret Access Key obtained from environment variables.
        aws_region (str): AWS region name obtained from environment variables.
        influxdb_url (str): URL of the InfluxDB instance obtained from environment variables.
        influxdb_token (str): Token for authenticating with InfluxDB obtained from environment variables.
        influxdb_org (str): Organization name in InfluxDB obtained from environment variables.
        influxdb_bucket (str): Bucket name in InfluxDB obtained from environment variables.
    """

    def __init__(self):
        """
        Initializes the ConnectionInitializer class with environment variables.
        """
        self.aws_access_key = os.getenv("aws_access_key")
        self.aws_secret_key = os.getenv("aws_secret_key")
        self.aws_region = os.getenv("aws_region")
        self.influxdb_url = os.getenv("influxdb_url")
        self.influxdb_token = os.getenv("influxdb_token")
        self.influxdb_org = os.getenv("influxdb_org")
        self.influxdb_bucket = os.getenv("influxdb_bucket")

    def initialize_aws_connection(self):
        """
        Initializes and returns an AWS SQS client using the provided credentials and region.

        Returns:
            botocore.client.SQS: Initialized AWS SQS client.
        """
        sqs_client = boto3.client(
            'sqs',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region
        )
        return sqs_client

    def initialize_influxdb_connection(self):
        """
        Initializes and returns an InfluxDB client using the provided URL, token, and organization.

        Returns:
            influxdb_client.client.write_api.WriteApi: Initialized InfluxDB client.
        """
        client = influxdb_client.InfluxDBClient(
            url=self.influxdb_url,
            token=self.influxdb_token,
            org=self.influxdb_org
        )
        write_api = client.write_api()
        return write_api

class FinancialDataLoader:
    """
    A class for loading financial data from Alpha Vantage API and storing it in InfluxDB
    and write the response to SQS Queue.

    Attributes:
        url (str): URL for Alpha Vantage API to get stock data.
        function (str): Time series function to get stock data, e.g., Intraday.
        symbol (str): Symbol of stock data, e.g., AAPL for Apple.
        interval (str): Time series interval, e.g., 5 minutes.
        apikey (str): API key for Alpha Vantage API.
        sqs_client (botocore.client.SQS): Initialized AWS SQS client.
        influxdb_client (influxdb_client.client.write_api.WriteApi): Initialized InfluxDB client.
    """

    def __init__(self, sqs_client, influxdb_client):
        """
        Initializes the FinancialDataLoader with necessary attributes and clients.

        Args:
            sqs_client (botocore.client.SQS): Initialized AWS SQS client.
            influxdb_client (influxdb_client.client.write_api.WriteApi): Initialized InfluxDB client.
        """
        self.url = os.getenv("baseUrl")  # Fetch base URL from environment variables
        self.function = os.getenv("function")  # Fetch function from environment variables
        self.symbol = os.getenv("symbol")  # Fetch symbol from environment variables
        self.interval = os.getenv("interval")  # Fetch interval from environment variables
        self.apikey = os.getenv("apikey")  # Fetch API key from environment variables
        self.queue_url = os.getenv("queue_url") # Fetch queue url (sqs) from environment variables
        self.sqs_client = sqs_client  # Assign initialized SQS client
        self.influxdb_client = influxdb_client  # Assign initialized InfluxDB client


    def getDataFromAPI(self) -> requests.Response:
        """
        Fetches financial data from the Alpha Vantage API.

        Returns:
            requests.Response: Response object containing data from the API.
        """
        try:
            payload = {}
            headers = {}
            response = requests.request("GET", self.url, headers=headers, data=payload)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response
        except requests.exceptions.HTTPError as errh:
            logger.exception(f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            logger.exception(f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            logger.exception(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            logger.exception(f"Request Exception: {err}")

    def prepare_data(self, data: dict) -> list:
        """
        Prepares data in dictionary format for insertion into InfluxDB.

        Args:
            data (dict): Raw financial data in dictionary format.

        Returns:
            list: List of dictionaries containing formatted data for InfluxDB insertion.
        """
        influxdb_data = []
        time_series_data = data.get("Time Series (5min)")
        for timestamp, values in time_series_data.items():
            influxdb_point = {
                "measurement": "stock_prices",
                "tags": {"symbol": data["Meta Data"]["2. Symbol"]},
                "time": timestamp,
                "fields": {
                    "open": float(values["1. open"]),
                    "high": float(values["2. high"]),
                    "low": float(values["3. low"]),
                    "close": float(values["4. close"]),
                    "volume": int(values["5. volume"]),
                },
            }
            influxdb_data.append(influxdb_point)
        return influxdb_data

    def write_to_influxdb(self, data: dict) -> None:
        """
        Writes formatted data to InfluxDB.

        Args:
            data (dict): Raw financial data in dictionary format.
        """
        try:
            formatted_data = self.prepare_data(data)
            self.write_api.write(
                bucket=self.bucket, org=self.org, record=formatted_data
            )
        except ApiException as e:
            logger.exception(f"Error while writing to InfluxDB: {e}")

    def send_messages(self, messages):
        """
        Send a batch of messages in a single request to an SQS queue.
        This request may return overall success even when some messages were not sent.
        The caller must inspect the Successful and Failed lists in the response and
        resend any failed messages.

        :param queue_url: The URL of the queue to receive the messages.
        :param messages: The messages to send to the queue. List of dictionaries.
        :return: The response from SQS that contains the list of successful and failed
                messages.
        """
        try:
            sqs_client = boto3.client("sqs")
            entries = [
                {
                    "Id": str(ind),
                    "MessageBody": json.dumps(msg),
                }
                for ind, msg in enumerate(messages)
            ]
            response = sqs_client.send_message_batch(
                QueueUrl=self.queue_url, Entries=entries
            )

            if "Successful" in response:
                for msg_meta in response["Successful"]:
                    logger.info("Message sent: %s", msg_meta["MessageId"])
            if "Failed" in response:
                for msg_meta in response["Failed"]:
                    logger.warning("Failed to send: %s", msg_meta["MessageId"])
        except ClientError as error:
            logger.exception("Send messages failed to queue: %s", self.queue_url)
            raise error
        else:
            return response

    def process_and_send_data_concurrently(self, data: dict) -> None:
        """
        Prepare and send data to InfluxDB and SQS concurrently.

        Args:
            data (dict): Raw financial data in dictionary format.
        """
        def process_data():
            """
            Prepare data for InfluxDB and SQS and send it concurrently.
            """
            formatted_data = self.prepare_data(data)
            self.write_to_influxdb(formatted_data)
            self.send_messages(self.queue_url, formatted_data)

        # Use ThreadPoolExecutor to run functions concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit the function to executor
            future = executor.submit(process_data)

            # Wait for the function to complete
            concurrent.futures.wait([future])
