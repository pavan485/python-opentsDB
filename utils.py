import yaml
import log
import requests,json
import dateutil.parser as dp
creds = yaml.safe_load(open('./config/config_opents.yaml'))
conf = yaml.safe_load(open('./config/config_catchpoint.yaml'))
logger = log.get_logger(__name__,conf['log_file'],conf['log_level'])


class Utils():
    @staticmethod
    def parse_raw(structure):
        logger.info("Parsing data for OpentsDB")
        char_map = {'#':'numOf','%':'percent','(':'.',')':'',' ':''}
        chars = "#%() " 
        metric_values = []
        items = []
        test_metric_values = []
        metric_values = []
        solution = {}
        lines = []
        synthetic_metrics = []
        test_params = []
        if 'error' in structure:
            logger.error(structure['error'])
        if 'detail' not in structure:
            logger.error('No data available')
            return None    
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
            metric_values.append(values)
            test_metric_values.append(metric_values)
        
        for test_metric_value in test_metric_values:
            temp = {}
            temp['fields'] = {}
            for i in range(0,len(test_metric_value),1):
                # if test_metric_value[i] is None:
                #     continue
                if type(test_metric_value[i]) is dict:
                    for value in test_metric_value[i]:
                        temp[value] = test_metric_value[i][value]
                else:    
                    temp['fields'][test_params[i]] = test_metric_value[i]                    

            items.append(temp)   
        solution['items'] = items
    
        for item in solution['items']:
            for metric in item['fields']:
                line = {
                    'metric' : metric,
                    'timestamp' : item['timestamp'],
                    'value' : item['fields'][metric],
                    'tags' : item['tags']
                }
                lines.append(line)
        return lines  
        

    @staticmethod
    def write_data(data):
        logger.info("Pushing data to OpentsDB")
        tsdb_url = '{0}:{1}/api/put?summary'.format(creds['tsdb_host'],creds['tsdb_port'])
        try:
            r = requests.post(tsdb_url, json=data)
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
