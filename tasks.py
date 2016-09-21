from celery import Celery
import os, string, subprocess
from celery.utils.log import get_task_logger


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
	logger.info('Ended Test %s' % folder)