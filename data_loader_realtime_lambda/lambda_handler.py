"""
This module contains the Lambda handler function to process and send financial data to InfluxDB and SQS.

It imports dependencies such as logger setup, connection initialization, and data loader class.

The lambda will be triggered using Event bridge after a specified amount of time has passed. Based on a cron job.

Modules:
    - src.logger: Provides functions for creating a logger instance.
    - src.utils: Contains classes for initializing AWS connections and loading financial data.

Functions:
    - handler: Lambda handler function to fetch data, process it, and send it to InfluxDB and SQS.

Example usage:
    - This module is intended to be used as a Lambda function handler for processing financial data.
"""

# import dependencies
import json
from src.logger import create_logger
from src.utils import ConnectionInitializer, FinancialDataLoader

# Setup logger
_logger = create_logger("_logger")

# Initialize SQS and InfluxDB connection
Init = ConnectionInitializer()
sqs_client = Init.initialize_aws_connection()
influxdb_client = Init.initialize_influxdb_connection()

# Initialize Data loader class
dataLoader = FinancialDataLoader(
    sqs_client=sqs_client,
    influxdb_client=influxdb_client
)

# Lambda Handler


def handler(event, context):
    """
    Lambda handler function to process and send financial data to InfluxDB and SQS concurrently.

    Args:
        event (dict): AWS Lambda event data.
        context (object): AWS Lambda context object.

    Returns:
        dict: A dictionary containing the status of InfluxDB and SQS write actions.
    """
    try:
        # Retrieve data from the API
        data = dataLoader.getDataFromAPI()
                
        # Process and Write data to InfluxDB and SQS concurrently
        processed_data = dataLoader.prepare_data(data)
        _logger.info(f"Data: {processed_data}")
        sqs_result = dataLoader.send_messages(data)
        influxdb_result = dataLoader.write_to_influxdb(processed_data)
        
        result = {
            "influxdb": influxdb_result,
            "sqs": sqs_result
        }
        
        # Log the result
        _logger.info("Result: %s", result)
        
        # Return a meaningful response indicating the status of the operation
        return {"statusCode": 200, "message": "Data sent successfully.", "result": result}
    except Exception as e:
        # Log any exceptions and return an error response
        _logger.error("Error: %s", str(e))
        return {"statusCode": 500, "message": "Internal Server Error", "error": str(e)}


if __name__=="__main__":
    handler(None, None)