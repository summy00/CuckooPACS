#!/usr/bin/env python
# encoding: utf-8
# Created Time:

import dicom
import mudicom
import numpy as np
import copy
import scipy.misc
import os
import scipy


def adjust_window(pd_in, * window_in):
    window_center, window_width = window_in
    upper_limit = window_center + window_width / 2
    lower_limit = window_center - window_width / 2
    slope = 255. / window_width
    bias = 128. - slope * window_center
    pd_in = pd_in.astype(np.int32)
    pd_out = pd_in.copy()
    for row_in in xrange(pd_out.shape[0]):
        for col_in in xrange(pd_out.shape[1]):
            if pd_out[row_in, col_in] > upper_limit:
                pd_out[row_in, col_in] = 255.
            elif pd_out[row_in, col_in] < lower_limit:
                pd_out[row_in, col_in] = 0.
            else:
                pd_out[row_in, col_in] = slope * pd_out[row_in, col_in] + bias
    pd_out = pd_out.astype(np.uint8)
    return pd_out


def dcm2thumbnail(source_path, target_path, resize_row=128, resize_col=128):
    # define output
    dict_return = {}
    dict_return['status'] = 1
    dict_return['paths'] = target_path
    filename = source_path.split(os.path.sep)[-1]
    if filename.split('.')[-1] == 'dcm':
        filename = filename[0: len(filename)-4]
    if target_path[-1] != os.path.sep:
        target_path += os.path.sep

    # get usefull dicom information
    try:
        dcm_head = dicom.read_file(source_path)
    except IOError:
        dict_return['status'] = 0
        print('read dicom error')
        return dict_return
    rescale_intercept = dcm_head.RescaleIntercept
    rescale_slope = dcm_head.RescaleSlope

    # get original pixel
    try:
        mud = mudicom.load(source_path)
    except mudicom.exceptions.InvalidDicom:
        dict_return['status'] = 0
        print('read mudicom error')
        return dict_return
    pixel_ori = (mud.image).numpy
    pixel_ori = pixel_ori.astype(np.int16)

    # pixel to HU value
    pixel_hu = copy.deepcopy(pixel_ori)
    pixel_hu = (rescale_slope * pixel_hu.astype(np.float64)).astype(np.int16)
    pixel_hu += np.int16(rescale_intercept)
    pixel_hu = np.array(pixel_hu, dtype=np.int16)

    # adjust window
    default_img = adjust_window(pixel_hu, *(40, 400))
    default_img = scipy.misc.imresize(default_img, (resize_row, resize_col), 'nearest')

    # return status
    try:
        scipy.misc.imsave(target_path + filename + '.jpg', default_img)
    except IOError:
        dict_return['status'] = 0
        return dict_return
    dict_return['paths'] = target_path + filename + '.jpg'

    return dict_return

if __name__ == '__main__':
    source = '/Users/wangxiaodong/Project/AIMED/ML/LITS/dicom/CT/CT038'
    target = '/Users/wangxiaodong/Desktop'
    status_dict = dcm2thumbnail(source, target)
    print(status_dict)
