from tasks import execute_test
import sys, string, os, time
import subprocess
from celery.task.sets import TaskSet
import xml.etree.ElementTree as ET


command = sys.argv[1:]
test_folder = sys.argv.pop()
options = sys.argv[1:]

if '-d' in options:
	ind = options.index('-d')
	ind1 = command.index('-d')
	options.pop(ind)
	results_folder = options.pop(ind)
	command.pop(ind1)
	command.pop(ind1)

command = ' '.join(command)
options = ' '.join(options)


def run_tests(command, test_folder, options, results_folder):
	if command:
		print '#########################################################'
		print 'Triggering dry run'
		print '#########################################################'
		suites = initiate_dry_run(command)
		job = TaskSet(tasks=[execute_test.subtask(kwargs={'path': suite, 'test_path': test_folder, 'command': options, 'results_folder': results_folder}) for suite in suites])
		print '#########################################################'
		print 'Executing Tests'
		print '#########################################################'
		result = job.apply_async()

		while not result.ready():
			time.sleep(0.1)

		print '#########################################################'
		print 'Finished tests, generating report'
		print '#########################################################'
		merge_results(suites, test_folder, results_folder)		

	else:
		raise ValueError('No test folder provided')


def initiate_dry_run(command):
	subprocess.call("pybot --dryrun --output=suites.xml --report=NONE --log=NONE %s" % command, shell=True)
	tree = ET.parse('suites.xml')
	root = tree.getroot()
	suites = []
	for suite in root.iter('suite'):
		attrs = suite.attrib
		if 'source' in attrs:
		 	path = attrs['source']
		 	if '.robot' in path:
		 		suites.append(path)
	os.remove('suites.xml')
	return suites


def merge_results(suites, test_folder, results_folder):
	for i in range(len(suites)):
		suite = suites[i]
		index = suite.rfind(test_folder)
		new_suite = suite[:index]
		test_path = suite[index:]
		folder = string.replace(test_path, '/', '.')
		suites[i] = new_suite + results_folder + '/' + folder + '/result.xml'
		output_directory = new_suite + results_folder
	subprocess.call('rebot --outputdir=%s --name=Tests --output output.xml %s' % (output_directory, ' '.join(suites)), shell=True)



if __name__ == '__main__':
    run_tests(command, test_folder, options, results_folder)


