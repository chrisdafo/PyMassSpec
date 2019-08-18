from pyms.Peak import Peak
from timeit import timeit
from copy import copy, deepcopy

import pytest

import os

from pyms.TopHat import tophat
from pyms.BillerBiemann import BillerBiemann, rel_threshold, num_ions_threshold
from pyms.GCMS.Function import build_intensity_matrix, build_intensity_matrix_i
from pyms.GCMS.IO.JCAMP.Function import JCAMP_reader
from pyms.Noise.SavitzkyGolay import savitzky_golay
from pyms.Peak.Function import peak_sum_area, peak_top_ion_areas
from pyms.Peak.Class import Peak
from pyms.Experiment.Class import Experiment

from copy import deepcopy


data = JCAMP_reader(os.path.join("data", "ELEY_1_SUBTRACT.JDX"))
im_i = build_intensity_matrix_i(data)
scan_i = im_i.get_index_at_time(31.17 * 60.0)
ms = im_i.get_ms_at_index(scan_i)
peak = Peak(12.34, ms)


def copy_peak():
	return copy(peak)

def deepcopy_peak():
	return deepcopy(peak)

print(timeit(copy_peak))
print(timeit(deepcopy_peak))

def copy_ms():
	return copy(ms)

def deepcopy_ms():
	return deepcopy(ms)

print(timeit(copy_ms))
print(timeit(deepcopy_ms))