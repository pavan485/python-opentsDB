import yaml
import log
import requests,json
import dateutil.parser as dp
from influxdb_client.client.write_api import SYNCHRONOUS
creds = yaml.safe_load(open('./config/config_mongo.yaml'))
conf = yaml.safe_load(open('./config/config_catchpoint.yaml'))
logger = log.get_logger(__name__,conf['log_file'],conf['log_level'])


class Utils():
    @staticmethod
    def parse_raw(structure):
        logger.info("Parsing data for OpentsDB")
        char_map = {'#':'numOf','%':'percent','(':'.',')':'',' ':''}
        chars = "#%() " 
        
        synthetic_metrics = []
        if 'error' in structure:
            logger.error(structure['error'])
        if 'detail' not in structure:
            logger.error('No data available')
            return None    
        test_params = []
        final_list = [] #list of all jsons
        synthetic_metrics = structure['detail']['fields']['synthetic_metrics']
        
        for i in synthetic_metrics:
            for char in chars:
                i['name'] = i['name'].replace(char,char_map[char])
            metrics = 'catchpoint.testdata.{0}'.format(i['name'])
            test_params.append(metrics)
        
        for value in structure['detail']['items']:
            values = {} # json which contains tags fields time 
            tag = {
                'TestId' : value['breakdown_1']['id'],
                'NodeId' : value['breakdown_2']['id']
            }
            

            if 'step' in value:
                tag['StepNumber'] = value['step']
            if 'hop_number' in value:
                tag['HopNumber'] = value['hop_number']
        
            values['tags'] = tag

            values['timestamp'] = dp.parse(value['dimension']['name']).timestamp()

            metric_values = value['synthetic_metrics']
            
            for i in range(0,len(metric_values),1):
                values['metric'] = test_params[i]
                values['value'] = metric_values[i]
            final_list.append(values)
        return final_list
       
                
        
        

    @staticmethod
    def write_data(data):
        logger.info("Pushing data to OpentsDB")
        
        try:
            r = requests.post("http://localhost:4242/api/put?details", json=data)
            return r.text
        except Exception as e:
            logger.exception(str(e))
            logger.exception('Error while writing data')


    @staticmethod
    def validate_configurations():
        if 'client_id' not in conf or conf['client_id'] is None:
            return False
        if 'client_secret' not in conf or conf['client_secret'] is None:
            return False
        if 'protocol' not in conf or conf['protocol'] is None: 
            return False
        if 'domain' not in conf or conf['domain'] is None:
            return False 
        if 'token_endpoint' not in conf or conf['token_endpoint'] is None: 
            return False
        if 'rawdata_endpoint' not in conf or conf['rawdata_endpoint'] is None:
            return False
        return True