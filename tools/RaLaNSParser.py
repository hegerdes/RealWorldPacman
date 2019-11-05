import datetime
import os
import sys

import h5py
import h5py_cache
import io
import progress
from pathlib import Path
import numpy as np
import scipy
import zipfile

from enum import Enum
from progress.bar import IncrementalBar
from scipy import spatial


class TransmitterTypes(Enum):
    POINT = 0
    LINE = 1
    AREA = 2
    CUBIC = 3
    LIST = 4


TTypes = TransmitterTypes


def read_header_config(zip_path):
    with zipfile.ZipFile(zip_path) as zip_file:
        config_file = zip_file.open("config.cfg")
        result_file = zip_file.open("result.txt")

        header = parse_header(result_file)
        config = parse_config(config_file)

    return header, config


def parse_header(result_file):
    header = {}
    for i, line in enumerate(result_file):
        line_str = str(line, 'utf-8')
        line_parts = line_str.split(' ')
        line_parts = map(lambda l: int(l), line_parts)
        if i == 0:
            (header["t_type"], *remainder) = line_parts
            if header["t_type"] == TTypes.AREA:
                continue  # TODO: Extra parsing?
            elif header["t_type"] == TTypes.LIST:
                (header["t_num"], *transmitters) = remainder
                header["transmitters"] = np.array_split(transmitters, header["t_num"])
        elif i == 1:
            (_, *header["bounds"], header["layers"], header["step_x"], header["step_y"]) = line_parts
            header["size_x"] = int((header["bounds"][2] - header["bounds"][0]) / header["step_x"]) + 1
            header["size_y"] = int((header["bounds"][3] - header["bounds"][1]) / header["step_y"]) + 1
            header["t_num"] = int(header["size_x"] * header["size_y"])
        else:
            break
    # header["header_size"] = result_file.tell()
    # result_file.seek(0, 0)
    return header


def parse_for_list_data(result_file, header):
    raise NotImplementedError


def parse_config(config_file):
    config = {}
    for line in config_file:
        line_str = str(line, 'utf-8')
        name, value = line_str.partition("=")[::2]
        config[name.strip()] = value.strip('\n')
    return config


def to_hdf5(zip_path, cache_path, header, config):
    hdf_file = "{}.hdf5".format(config["mapName"].strip())
    hdf_path = Path(cache_path, hdf_file)

    if hdf_path.exists() and hdf_path.is_file():
        print("WARNING: Cache file {} already exists, skipping generation...".format(str(hdf_file)))
        return hdf_path

    os.makedirs(hdf_path.parent, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        h5_file = h5py_cache.File(str(hdf_path), "a", libver='latest', chunk_cache_mem_size=512*1024**2)
        result_file = zip_file.open("result.txt", force_zip64=True)

        size_x, size_y, t_num = header["size_x"], header["size_y"], header["t_num"]
        num_transmitters = header["t_num"]
        start = 2
        tr_idx = 0

        res = []
        data_set = h5_file.create_dataset("coverage".format(tr_idx), compression="lzf",
                                          dtype=np.float32, shape=(size_x * size_y, size_x, size_y),
                                          chunks=(1, size_x, size_y))

        bar = IncrementalBar('Processing HDF5', max=num_transmitters)
        bar.file = sys.stdout
        bar.check_tty = False
        for l_idx, line in enumerate(result_file):
            if l_idx < start:
                continue
            elif l_idx <= start + size_y - 1:
                if len(line) > 0:
                    line_str = str(line, "utf-8")
                    res.append(np.genfromtxt(io.StringIO(line_str), delimiter=" ").tolist())
                if l_idx == start + size_y - 1:
                    if tr_idx < num_transmitters:
                        data_set[tr_idx] = res
                        res = []
                        tr_idx += 1
                        start += size_y
                        bar.next()
                    else:
                        print("WARNING: Dataset contains more data than expected")

    bar.finish()
    h5_file.close()
    return hdf_path
