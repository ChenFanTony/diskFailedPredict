import json
import sys
from predictor import get_diskfailurepredictor_path, DiskFailurePredictor

def load_smart(outb):
    predict_datas = []
    health_data = json.loads(outb)

    if len(health_data) >= 6:
        o_keys = sorted(health_data.keys(), reverse=True)
        for o_key in o_keys:
            dev_smart = {}
            s_val = health_data[o_key]
            ata_smart = s_val.get('ata_smart_attributes', {})
            for attr in ata_smart.get('table', []):
                if attr.get('raw', {}).get('string'):
                    if str(attr.get('raw', {}).get('string', '0')).isdigit():
                        dev_smart['smart_%s_raw' % attr.get('id')] = \
                            int(attr.get('raw', {}).get('string', '0'))
                    else:
                        if str(attr.get('raw', {}).get('string', '0')).split(' ')[0].isdigit():
                            dev_smart['smart_%s_raw' % attr.get('id')] = \
                                int(attr.get('raw', {}).get('string',
                                                            '0').split(' ')[0])
                        else:
                            dev_smart['smart_%s_raw' % attr.get('id')] = \
                                attr.get('raw', {}).get('value', 0)
            if s_val.get('power_on_time', {}).get('hours') is not None:
                dev_smart['smart_9_raw'] = int(s_val['power_on_time']['hours'])
            if dev_smart:
                predict_datas.append(dev_smart)
            if len(predict_datas) >= 12:
                break
    else:
        print('unable to predict device due to health data records less than 6 days')

    return predict_datas    

def main():
    health_data = {}
    predicted_result = ''

    obj_predictor = DiskFailurePredictor()
    obj_predictor.initialize("{}/models".format(get_diskfailurepredictor_path()))

    with open(sys.argv[1]) as f_read:
        health_data = f_read.read()    # The type of data is a string.

    predict_datas = load_smart(health_data)

    if len(predict_datas) >= 6:
        predicted_result = obj_predictor.predict(predict_datas)
    return predicted_result

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("need a file input")
        sys.exit(0)
    main()
