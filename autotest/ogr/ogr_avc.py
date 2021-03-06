#!/usr/bin/env python
###############################################################################
# $Id$
#
# Project:  GDAL/OGR Test Suite
# Purpose:  Test OGR AVCE00 and AVCBin drivers
# Author:   Even Rouault, <even dot rouault at mines dash paris dot org>
#
###############################################################################
# Copyright (c) 2008-2012, Even Rouault <even dot rouault at mines-paris dot org>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
###############################################################################

import sys

sys.path.append('../pymod')

import gdaltest
import ogrtest
from osgeo import ogr
from osgeo import gdal

###############################################################################
#


def check_content(ds):

    lyr = ds.GetLayerByName('ARC')
    expect = ['1', '2', '3', '4', '5', '6', '7']

    tr = ogrtest.check_features_against_list(lyr, 'UserID', expect)
    if not tr:
        return 'fail'

    lyr.ResetReading()

    feat = lyr.GetNextFeature()
    if ogrtest.check_feature_geometry(feat, 'LINESTRING (340099.875 4100200.0,340400.0625 4100399.5,340900.125 4100200.0,340700.03125 4100199.5)',
                                      max_error=0.01) != 0:
        return 'fail'

    return 'success'

###############################################################################
# Open AVCE00 datasource.


def ogr_avc_1():

    # Example given at Annex A of http://avce00.maptools.org/docs/v7_e00_cover.html
    avc_ds = ogr.Open('data/test.e00')
    if avc_ds.GetLayer(0).GetSpatialRef() is None:
        gdaltest.post_reason('expected SRS')
        return 'fail'

    if avc_ds is not None:
        return check_content(avc_ds)
    return 'fail'

###############################################################################
# Open AVCBin datasource.


def ogr_avc_2():

    avc_ds = ogr.Open('data/testavc/testavc')
    if avc_ds.GetLayer(0).GetSpatialRef() is None:
        gdaltest.post_reason('expected SRS')
        return 'fail'

    if avc_ds is not None:
        return check_content(avc_ds)
    return 'fail'

###############################################################################
# Try opening a compressed E00 (which is not supported)


def ogr_avc_3():

    gdal.PushErrorHandler('CPLQuietErrorHandler')
    avc_ds = ogr.Open('data/compressed.e00')
    gdal.PopErrorHandler()
    last_error_msg = gdal.GetLastErrorMsg()

    if avc_ds is not None:
        gdaltest.post_reason('expected failure')
        return 'fail'

    if last_error_msg == '':
        gdaltest.post_reason('expected error message')
        return 'fail'

    return 'success'

###############################################################################
# Open larger AVCBin datasource.


def ogr_avc_4():

    for filename in ['data/testpointavc/testpointavc', 'data/testpoint.e00']:
        avc_ds = ogr.Open(filename)
        lyr = avc_ds.GetLayer(0)
        last_feature = None
        count = 0
        for f in lyr:
            count += 1
            last_feature = f
        if count != 80:
            gdaltest.post_reason('fail')
            print(filename)
            print(count)
            return 'fail'
        count = lyr.GetFeatureCount()
        if count != 80:
            gdaltest.post_reason('fail')
            print(filename)
            print(count)
            return 'fail'
        if last_feature.GetFieldCount() != 7:
            gdaltest.post_reason('fail')
            print(filename)
            f.DumpReadable()
            return 'fail'
        if filename == 'data/testpointavc/testpointavc':
            fld_name = 'TESTPOINTAVC-ID'
        else:
            fld_name = 'WELLS-ID'
        if last_feature.GetField('ValueId') != 80 or last_feature.GetField(fld_name) != 80:
            gdaltest.post_reason('fail')
            print(filename)
            f.DumpReadable()
            return 'fail'

    return 'success'

###############################################################################
# Open AVCBin datasource with polygon


def ogr_avc_5():

    for filename in ['data/testpolyavc/testpolyavc', 'data/testpoly.e00']:
        avc_ds = ogr.Open(filename)
        lyr = avc_ds.GetLayerByName('PAL')
        last_feature = None
        count = 0
        for f in lyr:
            count += 1
            last_feature = f
        if count != 3:
            gdaltest.post_reason('fail')
            print(filename)
            print(count)
            return 'fail'
        count = lyr.GetFeatureCount()
        if count != 3:
            gdaltest.post_reason('fail')
            print(filename)
            print(count)
            return 'fail'
        if last_feature.GetFieldCount() != 5:
            gdaltest.post_reason('fail')
            print(filename)
            f.DumpReadable()
            return 'fail'
        if last_feature.GetField('ArcIds') != [-4, -5] or abs(last_feature.GetField('AREA') - 9939.059) > 1e-3:
            gdaltest.post_reason('fail')
            print(filename)
            f.DumpReadable()
            return 'fail'
        if filename == 'data/testpolyavc/testpolyavc':
            expected_wkt = 'POLYGON ((340700.03125 4100199.5,340500.0 4100199.75,340599.96875 4100100.25,340700.03125 4100199.5))'
        else:
            # Likely a bug in AVCE00 driver
            expected_wkt = 'POLYGON ((340299.94 4100199.8,340099.88 4100200.0,340299.94 4100199.8))'
        if last_feature.GetGeometryRef().ExportToWkt() != expected_wkt:
            gdaltest.post_reason('fail')
            print(filename)
            f.DumpReadable()
            return 'fail'

    return 'success'


gdaltest_list = [
    ogr_avc_1,
    ogr_avc_2,
    ogr_avc_3,
    ogr_avc_4,
    ogr_avc_5
]

if __name__ == '__main__':

    gdaltest.setup_run('ogr_avc')

    gdaltest.run_tests(gdaltest_list)

    sys.exit(gdaltest.summarize())
