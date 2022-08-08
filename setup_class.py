import cv2 as cv

import face_recognition as fr
import os
import contextlib
import sys
import numpy as np
from tqdm import tqdm
from tqdm.contrib import DummyTqdmFile
from xlsx import xlsx_file_create_new


@contextlib.contextmanager
def std_out_err_redirect_tqdm():
    orig_out_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = map(DummyTqdmFile, orig_out_err)
        yield orig_out_err[0]
    # Relay exceptions
    except Exception as exc:
        raise exc
    # Always restore sys.stdout/err if necessary
    finally:
        sys.stdout, sys.stderr = orig_out_err


def print_red(text):
    print("\033[1m\033[36m\033[41m{}\033[0m".format(text))


def print_green(text):
    print("\033[32m{}\033[0m".format(text))


def setup_class(path):
    class_images = []  # LIST CONTAINING ALL THE IMAGES IN FOLDER.
    known_face_names = []  # LIST CONTAINING ALL THE CORRESPONDING CLASS Names
    known_face_encodings = []  # LIST CONTAINING ALL THE CORRESPONDING KNOWN FACE
    img_list = []  # List containing images in target directory

    # List of files in target directory. There are different types of files.
    # Not only images
    file_list = os.listdir(path)

    # Iterate directory
    for file in file_list:
        # check only image files
        if file.endswith('.jpg'):
            img_list.append(file)
    print('img_list', img_list)
    img_list_len = len(img_list)

    print("Total People Detected in Class:", img_list_len)

    with std_out_err_redirect_tqdm() as orig_stdout:
        pbar = tqdm(total=img_list_len, file=orig_stdout, dynamic_ncols=True,
                    bar_format='Processing: {percentage:3.0f}% |{bar:100}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')  # Progressbar.
        for image in img_list:
            current_img = cv.imread(f'{path}/{image}')
            class_images.append(current_img)
            name = os.path.splitext(image)[0]
            known_face_names.append(name)
            current_img = cv.cvtColor(current_img, cv.COLOR_BGR2RGB)
            # print('image:', count, name)
            try:
                encode = fr.face_encodings(current_img)[0]
            except IndexError:
                print()
                print_red(
                    f' ERROR: Image {path}/{image} wasn\'t recognize! It needs to be replaced. ')
                print()

            known_face_encodings.append(encode)
            bad_image_flag = False
            pbar.update()
        pbar.close()
        print()
        # print('known_face_encodings:', known_face_encodings)
        print('known_face_names:', len(known_face_names))
        print('known_face_names:', known_face_names)
        print('known_face_encodings:', len(known_face_encodings))
        print_green('Encodings Complete')
        # Save recognized data to npy-files in target directory
        np.save(f'{path}/names.npy', known_face_names)
        print('File names.npy saved')
        np.save(f'{path}/face_encodings.npy', known_face_encodings)
        print('File face_encodings.npy saved')

        #Create new attendance xlsx-file
        xlsx_file_create_new(path, known_face_names)
    return known_face_names, known_face_encodings


if __name__ == '__main__':
    setup_class('class_beetroot')
    # setup_class('class_got')
    # setup_class('class_trofim')

