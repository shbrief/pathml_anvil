import numpy as np
import pytest

from pathml.preprocessing.transforms import (
    MedianBlur, GaussianBlur, BoxBlur, BinaryThreshold,
    MorphOpen, MorphClose, ForegroundDetection, SuperpixelInterpolation,
    StainNormalizationHE, NucleusDetectionHE, TissueDetectionHE,
    BackgroundSubtractMIF, DriftCompensateCODEX, DeconvolveMIF,
    QuantifyMIF, SegmentMIF
)
from pathml.utils import RGB_to_GREY


@pytest.mark.parametrize('ksize', [3, 7, 21])
@pytest.mark.parametrize('transform', [MedianBlur, BoxBlur])
def test_median_box_blur(tileHE, ksize, transform):
    t = transform(kernel_size = ksize)
    orig_im = tileHE.image
    t.apply(tileHE)
    assert np.array_equal(tileHE.image, t.F(orig_im))


@pytest.mark.parametrize('ksize', [3, 7, 21])
@pytest.mark.parametrize('sigma', [0.1, 3, 0.999])
def test_gaussian_blur(tileHE, ksize, sigma):
    t = GaussianBlur(kernel_size = ksize, sigma = sigma)
    orig_im = tileHE.image
    t.apply(tileHE)
    assert np.array_equal(tileHE.image, t.F(orig_im))


@pytest.mark.parametrize('thresh', [0, 0.5, 200])
@pytest.mark.parametrize('otsu', [True, False])
def test_binary_thresholding(tileHE, thresh, otsu):
    t = BinaryThreshold(use_otsu = otsu, threshold = thresh, mask_name = "testing")
    t.apply(tileHE)
    assert np.array_equal(tileHE.masks["testing"], t.F(RGB_to_GREY(tileHE.image)))


@pytest.mark.parametrize('n_iter', [1, 3])
@pytest.mark.parametrize('ksize', [3, 21])
@pytest.mark.parametrize('transform', [MorphOpen, MorphClose])
def test_open_close(tileHE, transform, ksize, n_iter):
    t = transform(kernel_size = ksize, n_iterations = n_iter, mask_name = "testmask")
    orig_mask = np.copy(tileHE.masks["testmask"])
    m = t.F(orig_mask)
    t.apply(tileHE)
    assert np.array_equal(tileHE.masks["testmask"], m)


@pytest.mark.parametrize('min_reg_size', [0, 10])
@pytest.mark.parametrize('max_hole_size', [0, 10])
@pytest.mark.parametrize('outer_contours_only', [True, False])
def test_foreground_detection(tileHE, min_reg_size, max_hole_size, outer_contours_only):
    t = ForegroundDetection(min_region_size = min_reg_size, max_hole_size = max_hole_size,
                            outer_contours_only = outer_contours_only, mask_name = "testmask")
    orig_mask = tileHE.masks["testmask"]
    t.apply(tileHE)
    assert np.array_equal(tileHE.masks["testmask"], t.F(orig_mask))


@pytest.mark.parametrize('n_iter', [1, 30])
@pytest.mark.parametrize('region_size', [10, 20])
def test_superpix_interp(tileHE, region_size, n_iter):
    t = SuperpixelInterpolation(region_size = region_size, n_iter = n_iter)
    orig_im = tileHE.image
    t.apply(tileHE)
    assert np.array_equal(tileHE.image, t.F(orig_im))


@pytest.mark.parametrize('target', ["normalize", "hematoxylin", "eosin"])
@pytest.mark.parametrize('method', ["vahadane", "macenko"])
def test_stain_normalization_he(tileHE, method, target):
    t = StainNormalizationHE(target = target, stain_estimation_method = method)
    orig_im = tileHE.image
    t.apply(tileHE)
    if method == "vahadane":
        # theres an element of randomness in vahadane implementation, haven't been able to figure
        # out how to set a seed
        assert tileHE.image.shape == t.F(orig_im).shape
    else:
        assert np.allclose(tileHE.image, t.F(orig_im))


def test_nuc_detectionHE(tileHE):
    t = NucleusDetectionHE(mask_name = "testing", stain_estimation_method = "macenko")
    orig_im = tileHE.image
    t.apply(tileHE)
    assert np.array_equal(tileHE.masks["testing"], t.F(orig_im))


@pytest.mark.parametrize('use_saturation', [True, False])
@pytest.mark.parametrize('threshold', [None, 100])
def test_tissue_detectionHE(tileHE, threshold, use_saturation):
    t = TissueDetectionHE(mask_name = "testing", threshold = threshold, use_saturation = use_saturation)
    orig_im = tileHE.image
    m = t.F(orig_im)
    t.apply(tileHE)
    assert np.array_equal(tileHE.masks["testing"], m)

def test_deconvolveMIF():
    pass

def test_segmentMIF():
    pass

def test_quantifyMIF():
    pass

# TODO: backgroundsubstractmif, driftcompensatecodex


@pytest.mark.parametrize("transform", [MedianBlur(),
                                       GaussianBlur(),
                                       BoxBlur(),
                                       BinaryThreshold(),
                                       MorphOpen(),
                                       MorphClose(),
                                       ForegroundDetection(),
                                       SuperpixelInterpolation(),
                                       StainNormalizationHE(),
                                       NucleusDetectionHE(),
                                       TissueDetectionHE(),
                                       BackgroundSubtractMIF(),
                                       DriftCompensateCODEX(),
                                       DeconvolveMIF(),
                                       QuantifyMIF(),
                                       SegmentMIF()])
def test_repr(transform):
    repr(transform)
