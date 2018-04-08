import mudicom
from PIL.Image import fromarray
import pydicom
import os
import copy
import numpy as np
from pydicom import uid
from PIL.Image import fromarray


class CuckooImage:
    def __init__(self, cuckooParser=None):
        self.pixel = None
        self.ts = cuckooParser.transferSyntax
        self.ds = cuckooParser.dcm_dataset
        self.fPath = cuckooParser.file_path
        self.intercept = cuckooParser.intercept
        self.slope = cuckooParser.slope
        # self.window_in = cuckooParser.window_in
        self.ww = cuckooParser.wWidth
        self.wc = cuckooParser.wCenter

    def GetPixelByTransferSyntax(self):
        if self.ts == uid.ImplicitVRLittleEndian or self.ts== uid.JPEGLossless:
            self.ds.decompress()
            self.pixel = self.ds.pixel_array

        elif self.ts == uid.ExplicitVRLittleEndian or self.ts == uid.JPEG2000Lossy:
            import mudicom
            mu = mudicom.load(self.fPath)
            # returns array of data elements as dicts
            mu.read()
            # creates image object
            img = mu.image  # before v0.1.0 this was mu.image()
            # returns numpy array
            self.pixel = img.numpy  # before v0.1.0 this was mu.numpy()fileFolder
        else:
            print self.ts + " can not support Transfer Syntax"
            return

        return self.pixel

    def ApplyModalityLUT(self, pixel, intercept, slope):

        if intercept is None or slope is None:
            print 'No intercept or slope'
            return pixel
        # pixel to HU value
        pixel_hu = copy.deepcopy(pixel)
        pixel_hu = slope * pixel_hu.astype(np.float64) + np.float64(intercept)
        pixel_hu = np.int16(pixel_hu)
        pixel_hu = np.array(pixel_hu, dtype=np.int16)
        return pixel_hu

    def ApplyVOILUT(self, pixel, ww, wc):
        if ww is None or wc is None:
            print 'No ww/wc'
            return pixel
        window_center = wc
        window_width = ww
        upper_limit = window_center + window_width / 2
        lower_limit = window_center - window_width / 2
        slope = 255. / window_width
        bias = 128. - slope * window_center
        pd_in = pixel.astype(np.int32)
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

    def SetDefaultWindow(self, pixel):
        pixelM = self.ApplyModalityLUT(pixel, self.intercept, self.slope)
        pixelP = self.ApplyVOILUT(pixelM, self.ww, self.wc)
        return pixelP

    def SetWindow(self, pixel, ww, wc):
        # from PIL import Image
        have_PIL = True
        try:
            import PIL.Image
        except:
            have_PIL = False

        have_numpy = True
        try:
            import numpy as np
        except:
            have_numpy = False

        have_numpy = True
        try:
            import numpy as np
        except:
            have_numpy = False

        def get_LUT_value(data, window, level):
            """Apply the RGB Look-Up Table for the given data and window/level value."""
            if not have_numpy:
                raise ImportError, "Numpy is not available. See http://numpy.scipy.org/ to download and install"

            return np.piecewise(data,
                                [data <= (level - 0.5 - (window - 1) / 2),
                                 data > (level - 0.5 + (window - 1) / 2)],
                                [0, 255, lambda data: ((data - (level - 0.5)) / (window - 1) + 0.5) * (255 - 0)])

        image = get_LUT_value(pixel, ww, wc)

    def Convert2Pic(self, pixel, out_Path):
        im = fromarray(pixel)
        im.save(out_Path)