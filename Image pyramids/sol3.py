import numpy as np
from scipy.misc import imread
from scipy.ndimage.filters import convolve
from scipy.signal import convolve2d
from skimage.color import rgb2gray
import matplotlib.pyplot as plt
import os

GRAYSCALE = 1
RGB = 2
COLOR_RANGE = 256

def relpath(filename):
    """
    get the absolute path of a given relative path
    :param filename: the relative path
    :return: the absolute path
    """
    return os.path.join(os.path.dirname(__file__), filename)

def read_image(filename, representation):
    """
    opens an image either in rgb or grayscale representation, depending on input
    :param filename: the filename of an image on disk (could be grayscale or RGB).
    :param representation: representation code, either 1 or 2 defining whether the output should be a grayscale
    image (1) or an RGB image (2)
    :return: the image in np.float64 format
    """
    image = imread(filename)
    image = image.astype(np.float64).copy() / (COLOR_RANGE - 1)
    if representation == GRAYSCALE:
        image = rgb2gray(image)
    return image

def reduce_im(im, filter_vec):
    """
    reduces the size of an image by half
    :param im: a grayscale image with double values in [0, 1]
    :param filter_vec: row vector to convolve the image with
    :return: the reduced image
    """
    im = convolve(im, filter_vec, mode='mirror')
    im = convolve(im, filter_vec.T, mode='mirror')
    return im[::2, ::2]

def expand_im(im, filter_vec):
    """
    expands the size of an image by 2
    :param im: a grayscale image with double values in [0, 1]
    :param filter_vec: row vector to convolve the image with
    :return: the expanded image
    """
    expansion = np.zeros((2 * im.shape[0], 2 * im.shape[1]))
    expansion[::2, ::2] = im
    expansion = convolve(expansion, filter_vec, mode='mirror')
    expansion = convolve(expansion, filter_vec.T, mode='mirror')
    return expansion

def generate_gaussian(size):
    """
    creates a gaussian row vector
    :param size: size of the wanted vector
    :return: gaussian vector of shape (1, size)
    """
    if size == 1:
        return np.array([[1]])
    base = np.array([[0.5, 0.5]])
    gaussian = convolve2d(base, base)
    for i in range(size - 3):
        gaussian = convolve2d(gaussian, base)
    return gaussian

def build_gaussian_pyramid(im, max_levels, filter_size):
    """
    creates a gaussian pyramid for an image
    :param im: a grayscale image with double values in [0, 1]
    :param max_levels: the maximal number of levels in the resulting pyramid.
    :param filter_size: the size of the Gaussian filter (an odd scalar that represents a squared
    filter) to be used in constructing the pyramid filter
    :return: a tuple of the resulting pyramid and the filter used
    """
    filter_vec = generate_gaussian(filter_size)
    pyr = [im]
    for i in range(1, max_levels):
        nxt = reduce_im(pyr[i - 1], filter_vec)
        if nxt.shape[0] < 16 or nxt.shape[1] < 16:
            break
        pyr.append(nxt)
    return pyr, filter_vec

def build_laplacian_pyramid(im, max_levels, filter_size):
    """
    creates a laplacian pyramid for an image
    :param im: a grayscale image with double values in [0, 1]
    :param max_levels: the maximal number of levels in the resulting pyramid.
    :param filter_size: the size of the Gaussian filter (an odd scalar that represents a squared
    filter) to be used in constructing the pyramid filter
    :return: a tuple of the resulting pyramid and the filter used
    """
    gaus_pyr, filter_vec = build_gaussian_pyramid(im, max_levels, filter_size)
    filter_vec *= 2
    pyr = []
    for i in range(len(gaus_pyr) - 1):
        cur_lap = gaus_pyr[i] - expand_im(gaus_pyr[i + 1], filter_vec)
        pyr.append(cur_lap)
    pyr.append(gaus_pyr[-1])
    return pyr, filter_vec

def laplacian_to_image(lpyr, filter_vec, coeff):
    """
    reconstructs an image from its laplacian pyramid
    :param lpyr: the laplacian pyramid
    :param filter_vec: the filter used to create the pyramid
    :param coeff: a list of coefficients to multiply levels of the pyramid by
    :return: the reconstructed image
    """
    pyr_depth = len(lpyr)
    for i in range(pyr_depth):
        lpyr[i] *= coeff[i]
    for i in range(pyr_depth - 1):
        lpyr[pyr_depth - i - 2] += expand_im(lpyr[pyr_depth - i - 1], filter_vec)
    return lpyr[0]

def stretch_im(im):
    """
    stretches the pixel values in an image
    :param im: the image to stretch
    :return: the stretched image
    """
    min_val = np.amin(im)
    max_dif = np.amax(im) - min_val
    im = (im - min_val) / max_dif
    return im

def render_pyramid(pyr, levels):
    """
    generates an image display of a pyramid
    :param pyr: the pyramid to display
    :param levels: number of levels in the pyramid to display
    :return: the generated image
    """
    length = pyr[0].shape[0]
    width = 0
    for i in range(levels):
        width += pyr[i].shape[1]
        pyr[i] = stretch_im(pyr[i])
    res = np.zeros((length, width))
    start = 0
    for i in range(levels):
        level_len, level_wid = pyr[i].shape
        res[:level_len, start:start + level_wid] = pyr[i]
        start += level_wid
    return res

def display_pyramid(pyr, levels):
    """
    displays a given amount of levels of a pyramid
    :param pyr: the pyramid to display
    :param levels: number of levels to display
    :return: None
    """
    im = render_pyramid(pyr, levels)
    plt.imshow(im, cmap=plt.get_cmap('gray'))
    plt.show()

def pyramid_blending(im1, im2, mask, max_levels, filter_size_im, filter_size_mask):
    """
    performs pyramid blending on two images
    :param im1: the first input image
    :param im2: the second input image
    :param mask: a boolean (i.e. dtype == np.bool) mask containing True and False representing
    which parts of im1 and im2 should appear in the resulting im_blend.
    :param max_levels: the max_levels parameter you should use when generating the Gaussian and
    Laplacian pyramids
    :param filter_size_im: the size of the Gaussian filter (an odd scalar that represents a
    squared filter) which defining the filter used in the construction of the Laplacian pyramids
    of im1 and im2.
    :param filter_size_mask: the size of the Gaussian filter(an odd scalar that represents a
    squared filter) which defining the filter used in the construction of the Gaussian pyramid of
    mask.
    :return: the blended image
    """
    lap1, filter_vec = build_laplacian_pyramid(im1, max_levels, filter_size_im)
    lap2 = build_laplacian_pyramid(im2, max_levels, filter_size_im)[0]
    mask_gauss = build_gaussian_pyramid(mask.astype(np.double), max_levels, filter_size_mask)[0]
    out_pyr = []
    for i in range(len(lap1)):
        out_i = (mask_gauss[i] * lap1[i]) + ((1 - mask_gauss[i]) * lap2[i])
        out_pyr.append(out_i)
    coeff = [1 for _ in lap1]
    res = laplacian_to_image(out_pyr, filter_vec, coeff)
    res = np.clip(res, 0, 1)
    return res

def rgb_blend(im1, im2, mask, max_levels, filter_size_im, filter_size_mask):
    """
    performs image blending of two rgb images
    :param im1: first input image
    :param im2: second input image
    :param mask: a boolean (i.e. dtype == np.bool) mask containing True and False representing
    which parts of im1 and im2 should appear in the resulting im_blend.
    :param max_levels: the max_levels parameter you should use when generating the Gaussian and
    Laplacian pyramids
    :param filter_size_im: the size of the Gaussian filter (an odd scalar that represents a
    squared filter) which defining the filter used in the construction of the Laplacian pyramids
    of im1 and im2.
    :param filter_size_mask: the size of the Gaussian filter(an odd scalar that represents a
    squared filter) which defining the filter used in the construction of the Gaussian pyramid of
    mask.
    :return: the blended image
    """
    r1, g1, b1 = (im1[:, :, 0], im1[:, :, 1], im1[:, :, 2])
    r2, g2, b2 = (im2[:, :, 0], im2[:, :, 1], im2[:, :, 2])
    new_r = pyramid_blending(r1, r2, mask, max_levels, filter_size_im, filter_size_mask)
    new_g = pyramid_blending(g1, g2, mask, max_levels, filter_size_im, filter_size_mask)
    new_b = pyramid_blending(b1, b2, mask, max_levels, filter_size_im, filter_size_mask)
    res = np.dstack((new_r, new_g, new_b))
    return res

def example_display(im_tuple):
    """
    display the blend of two images
    :param im_tuple: a tuple consisting of four images to display
    :return: None
    """
    plt.figure()
    for i in range(1, 5):
        plt.subplot(220 + i)
        if i == 3:
            plt.imshow(im_tuple[i - 1], cmap=plt.get_cmap('gray'))
        else:
            plt.imshow(im_tuple[i - 1])
    plt.show()

def blending_example1():
    """
    blends an image of an eye with an image of the moon
    :return: a tuple consisting of tangerine image, socket image, the mask used and the result image
    """
    im1 = read_image(relpath("external/eye.jpg"), RGB)
    im2 = read_image(relpath("external/moon.jpg"), RGB)
    msk = read_image(relpath("external/moon_mask.jpg"), GRAYSCALE)
    msk = msk >= 0.5
    res = rgb_blend(im1, im2, msk.astype(np.double), 7, 3, 25)
    ret = (im1, im2, msk, res)
    example_display(ret)
    return ret

def blending_example2():
    """
    blends an image of a tangerine with an image of an electric socket
    :return: a tuple consisting of tangerine image, socket image, the mask used and the result image
    """
    im1 = read_image(relpath("external/tangerine.jpg"), RGB)
    im2 = read_image(relpath("external/socket.jpg"), RGB)
    msk = read_image(relpath("external/tan_mask.jpg"), GRAYSCALE)
    msk = msk >= 0.5
    res = rgb_blend(im1, im2, msk.astype(np.double), 4, 3, 25)
    ret = (im1, im2, msk, res)
    example_display(ret)
    return ret
