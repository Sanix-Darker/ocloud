import configparser as ConfigParser

# Configs parameters
configParser = ConfigParser.RawConfigParser()   
configFilePath = r'config.txt'
configParser.read(configFilePath)

# Filling parameters
TOKEN = configParser.get('ogram-config', 'TOKEN')
UPLOAD_FOLDER = configParser.get('ogram-config', 'UPLOAD_FOLDER')
