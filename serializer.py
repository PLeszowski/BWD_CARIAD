"""
Module manages loading and saving json and pickle files
Patryk Leszowski
APTIV
ADCAM CP60
"""
import pickle
import json
import logging
import re
import lzma
import os

logger = logging.getLogger(__name__)


def save_pkl(obj, path, file):
    """
    :param obj: object to be serialized
    :param path: path to folder
    :param file: file name
    :return:
    Save object to pickle
    """
    ext = file.split('.')[-1]
    logger.info(f'saving pickle: {file}')
    if path[-1] != '\\' or path[-1] != '/':
        path = path + '\\'

    try:
        if ext == 'xz':
            with lzma.open(path + file, 'wb') as f:
                pickle.dump(obj, f)
        else:
            if not re.match(r'.+\.pi?c?kle?', file):
                file += '.pickle'
            with open(path + file, 'wb+') as f:
                pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
    except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
        logger.error(f'failed to save pickle: {file}')
        logger.exception(e)


def load_pkl(path, file=None):
    """
    :param path: path to folder
    :param file: pickle file name
    :return:
    Load object
    """
    if file:
        path = os.path.join(path, file)

    ext = path.split('.')[-1]
    logger.info(f'loading pickle: {path}')

    if ext == 'xz':
        with lzma.open(path, 'rb') as f:
            return pickle.load(f)

    else:
        if not re.match(r'.+\.pi?c?kle?', path):
            file += '.pickle'

        try:
            with open(path, 'rb') as f:
                return pickle.load(f)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            logger.error(f'failed to load pickle: {path}')
            logger.exception(e)
            raise e


def save_json(obj, path, file=None):
    """
    :param obj: object to be serialized
    :param path: path to folder
    :param file: file name
    :return:
    Save object to json
    """
    print(f'saving json: {file}')
    if file:
        if '.json' not in file:
            filename = file + '.json'
        else:
            filename = file
        path = os.path.join(path, filename)
    try:
        with open(path, 'w') as f:
            json.dump(obj, f, indent=2)
    except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
        print(f'failed to save json: {path}')
        print(e)
        raise e


def load_json(path, file=None):
    """
    Load object
    :param path: path to folder
    :param file: json file name
    :return:
    """
    if file:
        logger.info(f'loading json: {file}')
        filename = json_file_name(file)
        if path[-1] != '\\' or path[-1] != '/':
            path = path + '\\'
        try:
            with open(path + filename, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            logger.error(f'failed to load json: {file}')
            logger.exception(e)
            raise e
    else:
        logger.info(f'loading json: {path}')
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            logger.error(f'failed to load json: {path}')
            logger.exception(e)
            raise e


def json_file_name(file):
    """
    :param file: filename
    :return:
    If json extension is not given add it
    """
    if '.json' not in file:
        return file + '.json'
    else:
        return file
