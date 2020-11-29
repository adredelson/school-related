from scipy.misc import imread
from skimage.color import rgb2gray
from tensorflow.keras.layers import Add, Conv2D, Input, Activation
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
import numpy as np
import random
from . import sol5_utils
from scipy.ndimage.filters import convolve

GRAYSCALE = 1
RGB = 2
COLOR_RANGE = 256

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


def load_dataset(filenames, batch_size, corruption_func, crop_size):
    """
    Generates random pairs of clean and corrupted image batches
    :param filenames: A list of filenames of clean images
    :param batch_size: The size of the batch of images for each iteration of Stochastic Gradient Descent
    :param corruption_func: – A function receiving a numpy’s array representation of an image as
            a single argument, and returns a randomly corrupted version of the input image
    :param crop_size: A tuple (height, width) specifying the crop size of the patches to extract.
    :return: A tuple of the form (source_batch, target_batch), where each output variable is an
    array of shape (batch_size, height, width, 1), target_batch is made of clean images,
    and source_batch is their respective randomly corrupted version according to corruption_func(im)
    """
    cache = {}
    while True:
        target = np.empty((batch_size, crop_size[0], crop_size[1], 1), dtype=np.float64)
        source = np.empty((batch_size, crop_size[0], crop_size[1], 1), dtype=np.float64)
        for i in range(batch_size):
            name = random.choice(filenames)
            if name in cache:
                im = cache[name]
            else:
                im = read_image(name, 1)
                cache[name] = im
            r_y = np.random.randint(im.shape[0] - (3 * crop_size[0]) - 1)
            r_x = np.random.randint(im.shape[1] - (3 * crop_size[1]) - 1)
            rand_crop = im[r_y:r_y + (3 * crop_size[0]), r_x:r_x + (3 * crop_size[1])]
            r_y = np.random.randint(2 * crop_size[0] - 1)
            r_x = np.random.randint(2 * crop_size[1] - 1)
            target[i] = (rand_crop[r_y:r_y + crop_size[0], r_x:r_x + crop_size[1]] -
                         0.5).reshape(*crop_size, 1)
            rand_crop = corruption_func(rand_crop)
            source[i] = (rand_crop[r_y:r_y + crop_size[0], r_x:r_x + crop_size[1]] -
                         0.5).reshape(*crop_size, 1)
        yield (source, target)


def resblock(input_tensor, num_channels):
    """
    Generates a residual block
    :param input_tensor: Symbolic input tensor
    :param num_channels: number of channels for each convolutional layer in the block
    :return: a resblock tensor
    """
    b = Conv2D(num_channels, 3, padding='same')(input_tensor)
    c = Activation('relu')(b)
    o = Conv2D(num_channels, 3, padding='same')(c)
    d = Add()([input_tensor, o])
    e = Activation('relu')(d)
    return e


def build_nn_model(height, width, num_channels, num_res_blocks):
    """
    Generates an untrained neural network
    :param height: height of input
    :param width: width of input
    :param num_channels: number of output channels
    :param num_res_blocks: number of resblocks in the network
    :return: an untrained network
    """
    a = Input(shape=(height, width, 1))
    b = Conv2D(num_channels, 3, padding='same')(a)
    c = Activation('relu')(b)
    for i in range(num_res_blocks):
        d = resblock(c, num_channels)
        c = d
    e = Conv2D(1, 3, padding='same')(d)
    f = Add()([a, e])
    model = Model(inputs=a, outputs=f)
    return model


def train_model(model, images, corruption_func, batch_size, steps_per_epoch, num_epochs,
                num_valid_samples):
    """
    Trains a neural network
    :param model: a general neural network model for image restoration
    :param images: a list of file paths pointing to image files.
    :param corruption_func: A function receiving a numpy’s array representation of an image as
            a single argument, and returns a randomly corrupted version of the input image
    :param batch_size: the size of the batch of examples for each iteration of SGD
    :param steps_per_epoch: The number of update steps in each epoch.
    :param num_epochs: The number of epochs for which the optimization will run.
    :param num_valid_samples: – The number of samples in the validation set to test on after every epoch
    """
    seperation_ind = int(0.8 * len(images))
    training = images[:seperation_ind]
    validation = images[seperation_ind:]
    train_gen = load_dataset(training, batch_size, corruption_func, model.input_shape[1:3])
    valid_gen = load_dataset(validation, batch_size, corruption_func, model.input_shape[1:3])
    model.compile(loss='mean_squared_error', optimizer=Adam(beta_2=0.9))
    model.fit_generator(train_gen, steps_per_epoch=steps_per_epoch, epochs=num_epochs,
                        validation_data=valid_gen, validation_steps=num_valid_samples / batch_size)


def restore_image(corrupted_image, base_model):
    """
    Restores a corrupted image
    :param corrupted_image: a grayscale image of shape (height, width) and with values in the [0, 1]
                        range of type float64
    :param base_model: a neural network trained to restore small patches
    :return: the restored image
    """
    corrupted_image = corrupted_image[..., np.newaxis] - 0.5
    a = Input(shape=(corrupted_image.shape[0], corrupted_image.shape[1], 1))
    b = base_model(a)
    new_model = Model(inputs=a, outputs=b)
    restored = new_model.predict(corrupted_image[np.newaxis, ...])[0] + 0.5
    restored = np.squeeze(restored, axis=2)
    return restored


def add_gaussian_noise(image, min_sigma, max_sigma):
    """
    Adds random gaussian noise to an image
    :param image: a grayscale image with values in the [0, 1] range of type float64.
    :param min_sigma: a non-negative scalar value representing the minimal variance of the gaussian
                      distribution
    :param max_sigma: a non-negative scalar value larger than or equal to min_sigma, representing
                      the maximal variance of the gaussian distribution.
    :return: the image with the added noise
    """
    sigma = np.random.uniform(min_sigma, max_sigma)
    noise = np.random.normal(0, sigma, image.shape)
    corrupted = np.clip(image + noise, 0, 1)
    corrupted = np.around(corrupted * 255) / 255
    return corrupted


def learn_denoising_model(num_res_blocks=5, quick_mode=False):
    """
    Generates a trained model for denoising images
    :param num_res_blocks: number of residual blocks to have in the model
    :param quick_mode: boolean value to determine whether or not to use smaller data
    :return: a trained denoising model
    """
    if quick_mode:
        batch_size = 10
        steps_per_epoch = 3
        num_epochs = 2
        num_valid_samples = 30
    else:
        batch_size = 100
        steps_per_epoch = 100
        num_epochs = 5
        num_valid_samples = 1000
    images = sol5_utils.images_for_denoising()
    corrupt = lambda im: add_gaussian_noise(im, 0, 0.2)
    model = build_nn_model(24, 24, 48, num_res_blocks)
    train_model(model, images, corrupt, batch_size, steps_per_epoch, num_epochs, num_valid_samples)
    return model


def add_motion_blur(image, kernel_size, angle):
    """
    Adds a motion blur to an image
    :param image: a grayscale image with values in the [0, 1] range of type float64.
    :param kernel_size: an odd integer specifying the size of the kernel
    :param angle: an angle in radians in the range [0, π)
    :return: the image with the added motion blur
    """
    kernel = sol5_utils.motion_blur_kernel(kernel_size, angle)
    blurred = np.clip(convolve(image, kernel), 0, 1)
    blurred = np.around(blurred * 255) / 255
    return blurred


def random_motion_blur(image, list_of_kernel_sizes):
    """
    Adds a random motion blur to an image
    :param image: a grayscale image with values in the [0, 1] range of type float64.
    :param list_of_kernel_sizes: a list of odd integers
    :return: the image with the added motion blur
    """
    size = np.random.choice(list_of_kernel_sizes)
    angle = np.random.uniform(0, np.pi)
    return add_motion_blur(image, size, angle)


def learn_deblurring_model(num_res_blocks=5, quick_mode=False):
    """
    Generates a trained model for removing motion blur from images
    :param num_res_blocks: number of residual blocks to have in the model
    :param quick_mode: boolean value to determine whether or not to use smaller data
    :return: a trained deblurring model
    """
    if quick_mode:
        batch_size = 10
        steps_per_epoch = 3
        num_epochs = 2
        num_valid_samples = 30
    else:
        batch_size = 100
        steps_per_epoch = 100
        num_epochs = 10
        num_valid_samples = 1000
    images = sol5_utils.images_for_deblurring()
    corrupt = lambda im: random_motion_blur(im, [7])
    model = build_nn_model(16, 16, 32, num_res_blocks)
    train_model(model, images, corrupt, batch_size, steps_per_epoch, num_epochs, num_valid_samples)
    return model
