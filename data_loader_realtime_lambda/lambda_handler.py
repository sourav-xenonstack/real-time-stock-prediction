from src.utils import ConnectionInitializer, FinancialDataLoader

c = ConnectionInitializer()
influx_client = c.initialize_influxdb_connection()
sqs_client = c.initialize_aws_connection()

f = FinancialDataLoader(influx_client)
data = f.getDataFromAPI()
response = f.prepare_data(data)
f.write_to_influxdb(response)
print(response)