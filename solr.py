#!/usr/bin/python3

import json
import argparse
from jmxquery import JMXConnection
from jmxquery import JMXQuery

# if any impacting changes to this plugin kindly increment the plugin version here.
PLUGIN_VERSION = 1

# Setting this to true will alert you when there is a communication problem while posting plugin data to server
HEARTBEAT = "true"

# Enter the host name configures for the Solr JMX
HOST_NAME = ""

# Enter the port configures for the Solr JMX
PORT = ""

# Enter the domain name configures for the Solr Instance
DOMAIN = ""

URL = ""
QUERY = ""

result_json = {}

METRIC_UNITS = {
    "document_cache_evictions": "evictions/second",
    "document_cache_hits": "hits/second",
    "document_cache_inserts": "sets/second",
    "document_cache_lookups": "gets/second",
    "filter_cache_evictions": "evictions/second",
    "filter_cache_hits": "hits/second",
    "filter_cache_inserts": "sets/second",
    "filter_cache_lookups": "gets/second",
    "query_result_cache_evictions": "evictions/second",
    "query_result_cache_hits": "hits/second",
    "query_result_cache_inserts": "sets/second",
    "query_result_cache_lookups": "gets/second",
    "cache_evictions": "evictions/second",
    "cache_hits": "hits/second",
    "cache_inserts": "sets/second",
    "cache_lookups": "gets/second",
    "searcher_maxdoc": "documents",
    "searcher_numdocs": "documents",
    "searcher_warmup": "documents",
    "request_times_50percentile": "requests/second",
    "request_times_75percentile": "requests/second",
    "request_times_95percentile": "requests/second",
    "request_times_98percentile": "requests/second",
    "request_times_999percentile": "requests/second",
    "request_times_99percentile": "requests/second",
    "request_times_mean": "milliseconds/request",
    "request_times_mean_rate": "requests/second",
    "request_times_one_minute_rate": "requests/second"
}


metric_map = {
    "evictions": "evictions",
    "hits": "hits",
    "inserts": "inserts",
    "lookups": "lookups",
    "Value": "value",
    "50thPercentile": "50percentile",
    "75thPercentile": "75percentile",
    "95thPercentile": "95percentile",
    "98thPercentile": "98percentile",
    "99thPercentile": "999percentile",
    "999thPercentile": "99percentile",
    "Mean": "mean",
    "MeanRate": "mean_rate",
    "OneMinuteRate": "one_minute_rate"
}


# JMX Query is executed and getting the Performance metric data after filtering the output
def get_metrics_from_jmx(jmxConnection, QUERY, prefix):
    try:
        jmxQuery = [JMXQuery(QUERY)]
        metrics = jmxConnection.query(jmxQuery)

        for metric in metrics:
            output = str(f"{metric.to_query_string()} = {metric.value}")
            output = output.split('/')
            output = output[1]
            output = output.split(' = ')
            if output[0] == "Value":
                result_json[prefix] = output[1]
                break
            if output[0] in metric_map.keys():
                result_json[prefix + metric_map[output[0]]] = output[1]

    except Exception as e:
        result_json["status"] = 0
        result_json["msg"] = str(e)

    return result_json


# JMX url is defined and JMX connection is established, Query and metric keys are passed to process
def get_output():
    URL = "service:jmx:rmi:///jndi/rmi://" + HOST_NAME + ":" + PORT + "/jmxrmi"
    try:
        jmxConnection = JMXConnection(URL)

        QUERY = "solr:dom1=core,dom2="+DOMAIN + \
            ",category=CACHE,scope=searcher,name=filterCache"
        result_json = get_metrics_from_jmx(
            jmxConnection, QUERY, "filter_cache_")

        QUERY = "solr:dom1=core,dom2="+DOMAIN + \
            ",category=CACHE,scope=searcher,name=fieldValueCache"
        result_json = get_metrics_from_jmx(jmxConnection, QUERY, "cache_")

        QUERY = "solr:dom1=core,dom2="+DOMAIN + \
            ",category=CACHE,scope=searcher,name=queryResultCache"
        result_json = get_metrics_from_jmx(
            jmxConnection, QUERY, "result_cache_")

        QUERY = "solr:dom1=core,dom2="+DOMAIN + \
            ",category=CACHE,scope=searcher,name=documentCache"
        result_json = get_metrics_from_jmx(
            jmxConnection, QUERY, "document_cache_")

        QUERY = "solr:dom1=core,dom2="+DOMAIN + \
            ",category=SEARCHER,scope=searcher,name=maxDoc"
        result_json = get_metrics_from_jmx(
            jmxConnection, QUERY, "searcher_maxdoc")

        QUERY = "solr:dom1=core,dom2="+DOMAIN + \
            ",category=SEARCHER,scope=searcher,name=numDocs"
        result_json = get_metrics_from_jmx(
            jmxConnection, QUERY, "searcher_numdocs")

        QUERY = "solr:dom1=core,dom2="+DOMAIN + \
            ",category=SEARCHER,scope=searcher,name=warmupTime"
        result_json = get_metrics_from_jmx(
            jmxConnection, QUERY, "searcher_warmup")

        QUERY = "solr:dom1=core,dom2="+DOMAIN + \
            ",category=UPDATE,scope=update,name=requestTimes"
        result_json = get_metrics_from_jmx(
            jmxConnection, QUERY, "request_times_")

        QUERY = "solr:dom1=core,dom2="+DOMAIN + \
            ",category=UPDATE,scope=update,name=requestTimes"
        result_json = get_metrics_from_jmx(
            jmxConnection, QUERY, "request_times_")

    except Exception as e:
        result_json["status"] = 0
        result_json["msg"] = str(e)

    return result_json


# arguments are parsed from solr.cfg file and assigned with the variables
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--host_name', help="solr host_name", type=str)
    parser.add_argument('--port', help="solr port", type=str)
    parser.add_argument('--domain_name', help="solr domain", type=str)
    args = parser.parse_args()
    if args.host_name:
        HOST_NAME = args.host_name
    if args.port:
        PORT = args.port
    if args.domain_name:
        DOMAIN = args.domain_name

    result_json = get_output()

    result_json['plugin_version'] = PLUGIN_VERSION
    result_json['heartbeat_required'] = HEARTBEAT
    result_json['units'] = METRIC_UNITS

    print(json.dumps(result_json, indent=4, sort_keys=True))
