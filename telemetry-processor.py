from kafka import KafkaConsumer
from arango import ArangoClient
import concurrent.futures
import time
import json 
from json import loads
import re

def vrf():
    # Connect to Arango
    user = "root"
    pw = "jalapeno"
    dbname = "jalapeno"

    # client = ArangoClient(hosts='http://198.18.133.104:30852')
    client = ArangoClient(hosts='http://arangodb.jalapeno:8529')
    db = client.db(dbname, username=user, password=pw)

    # Create Arango collection if it doesn't already exist
    print("vrfs connecting to arango")
    if db.has_collection('vrf'):
        vrf = db.collection('vrf')
    else:
        vrf = db.create_collection('vrf')

    # define Kafka consumer and topic to monitor
    consumer = KafkaConsumer(
        'jalapeno.vrf',
        # bootstrap_servers=['198.18.133.104:30092'],
        bootstrap_servers=['broker.jalapeno:9092'],
        auto_offset_reset='latest',
        enable_auto_commit=False,
        group_id='jalapeno',
        max_poll_records=20,
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    # for loop subscribes to Kafka messages and uploads docs to DB
    print("starting vrfs loop")
    for message in consumer:
        consumer.commit() 
        message = message.value
        msgobj = json.dumps(message, indent=4)
        #print(msgobj)
        # beware, regex'ing follows
        msg = msgobj.replace("/", "_" )
        msg = (re.sub("af_af_name", "af_name", msg))
        msg = (re.sub("af_route_target_route_target_type", "af_route_target_type", msg))
        msg = (re.sub("af_route_target_route_target_value", "af_route_target_value", msg))
        msg = (re.sub("interface_interface_name", "interface_name", msg))
        #print("message object: ", msg)
        
        # convert json string to dict
        msgdict = json.loads(msg)
        vrf_name = msgdict['fields']['vrf_name_xr']
        name = msgdict['tags']['source']
        #print(name, vrf_name)

        # generate DB ID and Key
        key = name + "_" + vrf_name
        id = "vrf/" + key
        msgdict['_key'] = key

        # upload document to DB
        if db.has_document(id):
            metadata = vrf.update(msgdict)
            print("document exists, updating timestamp: ", id)
        else:
            metadata = vrf.insert(msgdict)
            print("document added: ", msgdict['_key'])


def srv6localsids():

    # Connect to Arango
    user = "root"
    pw = "jalapeno"
    dbname = "jalapeno"

    client = ArangoClient(hosts='http://arangodb.jalapeno:8529')
    # client = ArangoClient(hosts='http://198.18.133.104:30852')
    db = client.db(dbname, username=user, password=pw)

    # Create Arango collection if it doesn't already exist
    print("srv6 localsids connecting to arango")

    if db.has_collection('srv6_local_sids'):
        srv6_local_sids = db.collection('srv6_local_sids')
    else:
        srv6_local_sids = db.create_collection('srv6_local_sids')

    # define Kafka consumer and topic to monitor
    consumer = KafkaConsumer(
        'jalapeno.srv6',
        # bootstrap_servers=['198.18.133.104:30092'],
        bootstrap_servers=['broker.jalapeno:9092'],
        auto_offset_reset='latest',
        enable_auto_commit=False,
        group_id='jalapeno',
        max_poll_records=20,
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    # for loop subscribes to Kafka messages and uploads docs to DB
    print("starting srv6 localsids loop")
    for message in consumer:
        consumer.commit() 
        message = message.value
        msgobj = json.dumps(message, indent=4)
        #print("message object: ", msgobj)

        # beware, regex'ing follows
        msg = msgobj.replace("/", "_" )
        msg = (re.sub("owner_owner", "owner", msg))
        msg = (re.sub("sid_context_key_u_dt4_u_dt_base_ctx_table_id", "table_id", msg))
        msg = (re.sub("sid_context_key_u_dt6_u_dt_base_ctx_table_id", "table_id", msg))
        
        # convert json string to dict
        msgdict = json.loads(msg)
        sid = msgdict['fields']['sid']
        name = msgdict['tags']['source']
        #print(name, sid)

        # generate DB ID and Key
        key = name + "_" + sid
        id = "srv6_local_sids/" + key
        msgdict['_key'] = key

        # upload document to DB
        if db.has_document(id):
            metadata = srv6_local_sids.update(msgdict)
            print("document exists, updating timestamp: ", id)
        else:
            metadata = srv6_local_sids.insert(msgdict)
        
            print("document added: ", msgdict['_key'])


    # Using ThreadPoolExecutor to execute functions in parallel
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Submit functions for execution
    futures = [executor.submit(vrf), executor.submit(srv6localsids)]

    # Wait for all functions to complete
    #concurrent.futures.wait(futures)

    # Alternatively, you can retrieve results if functions return values
    results = [future.result() for future in futures]
    #print(results)