from celery import Celery
import os, string, subprocess
from celery.utils.log import get_task_logger
import xml.etree.ElementTree as ET
from collections import deque


app = Celery('tasks', backend='amqp', broker='amqp://guest@localhost//')
logger = get_task_logger(__name__)


@app.task()
def execute_test(**kwargs):
    path = kwargs.get('path')
    folder_name = kwargs.get('test_path')
    command = kwargs.get('options')
    results_folder = kwargs.get('results_folder')
    index = path.rfind(folder_name)
    new_path = path[:index]
    test_path = path[index:]
    folder = string.replace(test_path, '/', '.')
    output_path = new_path + results_folder + '/' + folder
    logger.info('Executing Test %s' % folder)
    FNULL = open(os.devnull, 'w')
    subprocess.call('pybot --outputdir=%s --output=result.xml --report=NONE --log=NONE %s %s' % (output_path, command, path), stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
    tree = ET.parse('%s/result.xml' % output_path)
    count_fail = tree.findall('//total/stat[1]')[0].get('fail')
    if int(count_fail) > 0:
        status = 'FAIL'
    logger.info('Ended Test %s: %s' %(folder, status))