from celery import Celery
import os, string, subprocess

app = Celery('tasks', backend='amqp', broker='amqp://guest@localhost//')

@app.task
def execute_test(**kwargs):
	path = kwargs.get('path')
	folder_name = kwargs.get('test_path')
	command = kwargs.get('command')
	results_folder = kwargs.get('results_folder')
	index = path.rfind(folder_name)
	new_path = path[:index]
	test_path = path[index:]
	folder = string.replace(test_path, '/', '.')
	output_path = new_path + results_folder + '/' + folder
	subprocess.call('pybot --outputdir=%s --output=result.xml --report=NONE --log=NONE %s %s' % (output_path, command, path), shell=True)
