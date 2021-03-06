# -*- coding: utf-8 -*-
#import telebot
import xml.etree.ElementTree as ET

class Config():

    def __init__(self, path=None):
        print('init config')
        self.config = dict()
        self.path=''
        if path:
            self.path=''.join([path.rstrip(), '/'])

    def get_config(self):
        tree = ET.parse(f'{self.path}config/config.xml')
        root = tree.getroot()
        # все данные
        #print('Expertise Data:')
        result = dict()

        for elem in root:
            # print(elem.tag + ' - ' + str(len(list(elem))) )
            # print(type(elem))
            if (len(list(elem)) > 0):
                result[elem.tag] = dict()
                for subelem in elem:
                    result[elem.tag][subelem.tag] = subelem.text
            else:
                result[elem.tag] = elem.text
        return result

    def get_url(self, config=None):
        if not config:
            config = self.get_config()
        try:
            system = config['system']
            url = f"{config[system]['proto']}://{config[system]['host']}:{config[system]['port']}/"
            print(f"preurl: {url}")
            if (config[system]['proto']=='http' and config[system]['port']=='80') or \
                (config[system]['proto'] == 'https' and config[system]['port'] == '443'):
                url = f"{config[system]['proto']}://{config[system]['host']}/"
                print(f"post url: {url}")
            return url
        except:
            return None
