import pygame
import copy


def preprocess_image(path, flip=False):
    img = pygame.image.load(path).convert()
    img: pygame.Surface = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
    img.set_colorkey((0, 0, 0, 255))
    if flip:
        img = pygame.transform.flip(img, True, False)
    return img


def image_generator(images, repeats=3):
    images = copy.copy(images)
    n = 0
    max = len(images) * repeats - 1
    while True:
        if n > max:
            n = 0
        image = images[n // repeats]
        n += 1
        yield image


def generator_from_formatter(formatter, max_index, min_index=0, repeats=3, flip=False):
    paths = [formatter.format(x) for x in range(min_index, max_index)]
    images = [preprocess_image(path, flip) for path in paths]
    return image_generator(images, repeats)


