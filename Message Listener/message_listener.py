import os
import subprocess
import sys
from sqs_listener.daemon import Daemon
from sqs_listener import SqsListener
import logging

LOG_FILENAME = 'process-logs.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)
sqs_logger = logging.getLogger('sqs_listener')
inputImageDirectory = '/home/ubuntu/Ilios-3D-model-generation/demo/input'

class MyListener(SqsListener):
    def handle_message(self, message):
        receipt_handle = message['ReceiptHandle']

        file_bin_data = message['MessageAttributes']['File']['BinaryValue']
        filename = message['MessageAttributes']['FileName']['StringValue']

        recontructedImage = open(inputImageDirectory + '/' + str(filename), 'wb')
        recontructedImage.write(bytearray(file_bin_data))
        recontructedImage.close()

        if os.path.exists(inputImageDirectory + '/' + str(filename)):

            # Delete received message from queue
            self._client.delete_message(
                QueueUrl=self._queue_url,
                ReceiptHandle=receipt_handle
            )
            sqs_logger.info('Received and deleted message for file: %s' % filename)

        num_files = len([f for f in os.listdir(inputImageDirectory) if os.path.isfile(os.path.join(inputImageDirectory, f))])
        sqs_logger.info( "Number of files found :" + str(num_files))
        if (num_files == 4):
            sqs_logger.info("Invoking model after 4 messages have been received!")
            subprocess_cmd('cd ~/Ilios-3D-model-generation/; python ./src/demo.py;')

def subprocess_cmd(command):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    sqs_logger.info(proc_stdout)

class MyDaemon(Daemon):
    def run(self):
        print('Initializing listener')

        listener = MyListener('input_image_queue',
                              max_number_of_messages=4,
                              attribute_names=[
                                  'All',
                              ],
                              message_attribute_names=[
                                  'All',
                              ],
                              wait_time=10,
                              region_name='us-west-2')

        listener.listen()

if __name__ == "__main__":
    daemon = MyDaemon('/home/ubuntu/Ilios-3D-model-generation/sqs_daemon.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print('Starting listener daemon')
            daemon.start()
        elif 'stop' == sys.argv[1]:
            print('Attempting to stop the daemon')
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print('Unknown command')
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
