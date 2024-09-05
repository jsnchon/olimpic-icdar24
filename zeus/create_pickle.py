#!/usr/bin/env python3
import argparse
import os
import pickle

import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("name", help="Name of the dataset")
parser.add_argument("split", choices=["train", "dev", "test"], help="Which split to use")
parser.add_argument("--image_suffix", default="", type=str, help="Suffix to add to every image name")
args = parser.parse_args()

with open(os.path.join(args.name, f"samples.{args.split}.txt"), mode="r") as split_file:
    samples = [line.rstrip("\r\n") for line in split_file.readlines()]

dataset = []
for basepath in samples:
    image = None
    for extension in ["png", "jpg"]:
        try:
            with open(os.path.join(args.name, f"{basepath}{args.image_suffix}.{extension}"), mode="rb") as image_file:
                image = image_file.read()
        except FileNotFoundError:
            pass
    if image is None:
        raise ValueError(f"Cannot load image for basepath '{basepath}'")
    with open(os.path.join(args.name, f"{basepath}.lmx"), mode="r") as lmx_file:
        lmx = lmx_file.read().rstrip("\r\n")
        assert not "\n" in lmx
    with open(os.path.join(args.name, f"{basepath}.musicxml"), mode="r") as musicxml_file:
        musicxml = musicxml_file.read()
    dataset.append({
        "path": basepath,
        "image": image,
        "lmx": lmx,
        "musicxml": musicxml,
    })
with open(f"{args.name}-{args.split}.pickle", mode="wb") as dataset_file:
    pickle.dump(dataset, dataset_file)
