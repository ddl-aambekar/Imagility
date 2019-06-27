from model_unet import Network as Unet_Model
from model_recgan import Network as RecGan_Model
from config import config
import binvox_rw as binvox
import time
import glob
import numpy as np
import boto3
import ntpath
import os
from multiprocessing import Pool
import logging
sqs_logger = logging.getLogger('sqs_listener')
PROCESSED_IMAGE_BUCKET_NAME = 'processedimagesyoukea'

def run_process(_process, process_name):
    '''
    Necessary because tensorflow allocates gpu memory
    till calling process ends
    '''
    start = time.time()
    p = Pool(1)
    p.map(_process, [()])
    p.close()
    p.join()
    end = time.time()
    print('{} took {}s...'.format(process_name, end-start))

def unet_inference(_):
    unet = Unet_Model(config)
    unet.build_graph()
    unet.demo()

def recgan_inference(_):
    recgan = RecGan_Model(config)
    recgan.build_graph()
    recgan.demo()

def pred_to_binvox(voxel_file):
    s3 = boto3.resource('s3')
    voxel = np.load(voxel_file)[:, :, :, 0]
    voxel = voxel > config['voxel_pred_threshold']
    bvox = binvox.Voxels(voxel, voxel.shape, [0.0, 0.0, 0.0], 0.684696, 'xyz')

    fname = voxel_file.replace('npy', 'binvox')
    with open(fname, 'wb') as f:
        bvox.write(f)
        print('Sending file to s3 : '+str(fname))
        s3.meta.client.upload_file(fname, PROCESSED_IMAGE_BUCKET_NAME, ntpath.basename(fname))
        print('Deleting file '+str(ntpath.basename(fname))+'raw input files')
        os.remove('./demo/input/'+ntpath.basename(fname)[:-7])

def binvox_generation(_):
    voxel_files = glob.glob('./demo/voxel/*.npy')
    for voxel_file in voxel_files:
        pred_to_binvox(voxel_file)

if __name__ == '__main__':

    # Depth inference
    run_process(unet_inference, 'Depth inference')

    # Voxel inference
    run_process(recgan_inference, 'Voxel inference')

    # Convert voxel npy files to binvox files
    run_process(binvox_generation, 'Binvox generation')
