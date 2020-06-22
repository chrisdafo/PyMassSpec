"""
Provides functions for simulation of GCMS data
"""

################################################################################
#                                                                              #
#    PyMassSpec software for processing of mass-spectrometry data              #
#    Copyright (C) 2005-2012 Vladimir Likic                                    #
#    Copyright (C) 2019 Dominic Davis-Foster                                   #
#                                                                              #
#    This program is free software; you can redistribute it and/or modify      #
#    it under the terms of the GNU General Public License version 2 as         #
#    published by the Free Software Foundation.                                #
#                                                                              #
#    This program is distributed in the hope that it will be useful,           #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#    GNU General Public License for more details.                              #
#                                                                              #
#    You should have received a copy of the GNU General Public License         #
#    along with this program; if not, write to the Free Software               #
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.                 #
#                                                                              #
################################################################################

# stdlib
import math

# 3rd party
from typing import List

import numpy

# this package
from pyms import Peak
from pyms.IntensityMatrix import IntensityMatrix
from pyms.IonChromatogram import IonChromatogram


def add_gaussc_noise(im: IntensityMatrix, scale: float):
    """
    Adds noise to an IntensityMatrix object

    :param im: the intensity matrix object
    :type im: pyms.IntensityMatrix.IntensityMatrix

    :param scale: the scale of the normal distribution from which the noise is drawn
    :type scale: float

    :author: Sean O'Callaghan
    """

    n_scan, n_mz = im.size

    for i in range(n_mz):
        ic = im.get_ic_at_index(i)
        add_gaussc_noise_ic(ic, scale)
        im.set_ic_at_index(i, ic)


def add_gaussc_noise_ic(ic: IonChromatogram,  scale: float):
    """
    Adds noise drawn from a normal distribution with constant scale to an ion chromatogram

    :param ic: The ion Chromatogram
    :type ic: pyms.IonChromatogram.IonChromatogram
    :param scale: The scale of the normal distribution
    :type scale: float

    :author: Sean O'Callaghan
    """

    noise = numpy.random.normal(0.0, scale, (len(ic)))

    i_array_with_noise = ic.get_intensity_array() + noise
    ic.set_intensity_array(i_array_with_noise)


def add_gaussv_noise(im: IntensityMatrix, scale: float, cutoff: int, prop: float):
    """
    adds noise to an IntensityMatrix object

    :param im: the intensity matrix object
    :type im: pyms.IntensityMatrix.IntensityMatrix
    :param scale: the scale of the normal distribution from which the noise is drawn
    :type scale: float
    :param cutoff: The level below which the intensity of the ic at that point
        has no effect on the scale of the noise distribution
    :type cutoff: int
    :param scale: The scale of the normal distribution for ic values
    :type scale: int
    :param prop: For intensity values above the cutoff, the scale is
        multiplied by the ic value multiplied by prop
    :type prop: float

    :author: Sean O'Callaghan
    """

    n_scan, n_mz = im.size

    for i in range(n_mz):
        ic = im.get_ic_at_index(i)
        add_gaussv_noise_ic(ic, scale, cutoff, prop)
        im.set_ic_at_index(i, ic)


def add_gaussv_noise_ic(ic: IonChromatogram, scale: int, cutoff: int, prop: float):
    """
    Adds noise to an ic. The noise value is drawn from a normal
    distribution, the scale of this distribution depends on the
    value of the ic at the point where the noise is being added

    :param ic: The IonChromatogram
    :type ic: pyms.IonChromatogram.IonChromatogram
    :param cutoff: The level below which the intensity of the ic at that point
        has no effect on the scale of the noise distribution
    :type cutoff: int
    :param scale: The scale of the normal distribution for ic values below the cutoff
        is modified for values above the cutoff
    :type scale: int
    :param prop: For ic values above the cutoff, the scale is multiplied by the ic
        value multiplied by prop
    :type prop: float

    :author: Sean O'Callaghan
    """

    noise = numpy.zeros(len(ic))

    i_array = ic.get_intensity_array()
    # time_list = ic.get_time_list()

    for i in range(len(ic)):
        if i_array[i] < cutoff:
            noise[i] = numpy.random.normal(0.0, scale, 1)
        else:
            noise[i] = numpy.random.normal(0.0, scale * i_array[i] * prop, 1)

    i_array_with_noise = noise + i_array
    ic.set_intensity_array(i_array_with_noise)


def chromatogram(n_scan: int, x_zero: int, sigma: float,peak_scale: float) -> List:
    """
    Returns a simulated ion chromatogram of a pure component
    The ion chromatogram contains a single gaussian peak.

    :param n_scan: the number of scans
    :type n_scan: int
    :param x_zero: The apex of the peak
    :type x_zero: int
    :param sigma: The standard deviation of the distribution
    :type sigma: float
    :param: peak_scale: the intensity of the peak at the apex
    :type peak_scale: float

    :return: a list of intensities
    :rtype: list

    :author: Sean O'Callaghan
    """

    ic = numpy.zeros(n_scan, 'd')

    for i in range(n_scan):
        x = float(i)

        ic[i] = gaussian(x, x_zero, sigma, peak_scale)

    return ic


def gaussian(point: float, mean: int, sigma: float, scale: float) -> float:
    """
    calculates a point on a gaussian density function

    f = s*exp(-((x-x0)^2)/(2*w^2));

    :param point: The point currently being computed
    :type point: float
    :param mean: The apex of the peak
    :type mean: int
    :param sigma: The standard deviation of the gaussian
    :type sigma: float
    :param scale: The height of the apex
    :type scale: float

    :return: a single value from a normal distribution
    :rtype: float

    :author: Sean O'Callaghan
    """

    return scale * math.exp((-(point - mean) ** 2) / (2 * (sigma ** 2)))


def gcms_sim(time_list: List, mass_list: List, peak_list: Peak) -> IntensityMatrix:
    """
    Simulator of GCMS data

    :param time_list: the list of scan times
    :type time_list: list
    :param mass_list: the list of m/z channels
    :type mass_list: list
    :param peak_list: A list of peaks
    :type peak_list: :class:`list` of :class:`pyms.Peak.Class.Peak` objects

    :return: A simulated Intensity Matrix object
    :rtype: pyms.IntensityMatrix.IntensityMatrix

    :author: Sean O'Callaghan
    """

    n_mz = len(mass_list)
    n_scan = len(time_list)

    t1 = time_list[0]
    period = time_list[1] - t1

    # initialise a 2D numpy array for intensity matrix
    i_array = numpy.zeros((n_scan, n_mz), 'd')

    for peak in peak_list:
        print("-", end='')
        index = int((peak.rt - t1) / period)
        height = sum(peak.get_mass_spectrum().mass_spec)
        # standard deviation = area/(height * sqrt(2/pi))
        sigma = peak.area / (height * (math.sqrt(2 * math.pi)))
        print("width", sigma)
        for i in range(len(peak.get_mass_spectrum().mass_list)):
            ion_height = peak.get_mass_spectrum().mass_spec[i]
            ic = chromatogram(n_scan, index, sigma, ion_height)
            i_array[:, i] += ic

    im = IntensityMatrix(time_list, mass_list, i_array)

    return im
