# Python-OpenTSDB
Catchpoint Integration with OpenTSDB
---
OpenTSDB is a highly scalable Time Series Database built on top of HBase. It is perfect for storing high volume data generated by Synthetic Tests.

This integration relies on a Python script that runs every 15 minutes to pull raw synthetic test performance data from Catchpoint's REST API and store it in OpenTSDB. Once the data has been successfully inserted, it can be viewed and analyzed using any compatible analytics tool (e.g. Grafana). 

**Note: Right now, it has ability to pull data from one division per script setup**

# Prerequisites

1. Python v3.x
2. [OpenTSDB v2.4.x](http://opentsdb.net/)
3. Catchpoint account with a REST API consumer

# Installation and Configuration

Copy the Open folder to your machine
Run following commands in the directory /OpenTSDB-Python
   - python -m pip install requests
   - pip install pyyaml
   - pip install logger

### Configuration
In the 'config_catchpoint.yaml' file under config sub-directory, enter your [Catchpoint API consumer key and secret](https://portal.catchpoint.com/ui/Content/Administration/ApiDetail.aspx)
In the test_ids object of the 'config_catchpoint.yaml' file, enter the test IDs you want to pull the data for in a dictionary of array format.

*Example:*

    test_ids: { 
              web : [],
              traceroute : [], 
              api : [],
              transaction: [],
              dns : [],
              smtp : [],
              websocket: [],
              ping : []
              
          }
---       
3. In the "config_opents.js" file, enter your openTSDB hostname with http scheme and the port number.

### How to run

- Create a cronjob to run the application.py file every 15 minutes.

*Example crontab entry, if the file resides in /usr/local/bin/application.py*

`*/15 * * * * cd /usr/local/bin/ && python /usr/local/bin/application.py > /usr/local/bin/logs/cronlog.log 2>&1`

## File Structure

    OpenTSDB-Python/
    ├── request_handler.py          ## Contains APIs related to authentication       
    ├── config
    | ├── config_catchpoint.yaml    ## Configuration file for Catchpoint 
    | ├── config_opents.yaml        ## Configuration file for OpenTSDB
    ├── log
    | ├── app.log                   ## Contains informational and error logs. 
    ├── application.py              ## main file
    ├── log.py                      ## custom logger
    ├── request_handler.py          ## Contains API requests for token and raw endpoint 
    ├── utils.py                    ##  utility fot parsing data, inserting it to OpenTSDB and validating configurations

The data stored in OpenTSDB can be viewed via its Web UI or we can connect OpenTSDB to an analytics tool such as Grafana and [explore the data](https://grafana.com/docs/grafana/latest/datasources/graphite/).


   
