from django.http import JsonResponse
from pyhive import hive
import pandas as pd
from pyhive import hive
from thrift.transport.TSocket import TSocket
from thrift.transport.TTransport import TBufferedTransport
from thrift.protocol.TBinaryProtocol import TBinaryProtocol
from thrift_sasl import TSaslClientTransport
import socket


def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(ip_address)
    return ip_address


def get_hive_connection():
    socket = TSocket(get_ip_address(), 10000)
    transport = TBufferedTransport(socket)
    sasl_transport = TSaslClientTransport(transport, "PLAIN", None)
    protocol = TBinaryProtocol(sasl_transport)

    conn = hive.Connection(
        host=get_ip_address(),
        port=10000,
        username="hive",
        database="ecommerce",
        auth="NOSASL",
    )
    return conn


def fetch_customer_data(request):
    conn = get_hive_connection()
    query = "SELECT * FROM customer LIMIT 10"
    df = pd.read_sql(query, conn)
    data = df.to_dict(orient="records")
    return JsonResponse(data, safe=False)


def fetch_product_data(request):
    conn = get_hive_connection()
    query = "SELECT * FROM product LIMIT 10"
    df = pd.read_sql(query, conn)
    data = df.to_dict(orient="records")
    return JsonResponse(data, safe=False)


def fetch_transaction_data(request):
    conn = get_hive_connection()
    query = "SELECT * FROM transaction LIMIT 10"
    df = pd.read_sql(query, conn)
    data = df.to_dict(orient="records")
    return JsonResponse(data, safe=False)


def fetch_click_stream_data(request):
    conn = get_hive_connection()
    query = "SELECT * FROM click_stream LIMIT 20"
    df = pd.read_sql(query, conn)
    data = df.to_dict(orient="records")
    return JsonResponse(data, safe=False)


def hello_world(request):
    return JsonResponse({"message": "Hello World!"})