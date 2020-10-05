#!/usr/bin/python
# ***************************************************************************
# * @File:       importsJE.py
# *
# * @Brief:      imports JetEnergy datasets in panda dataframe for tensor flow
# *
# * @Author:     Milan Ganai
# * 
# * @Creation:   Dec 2017
# ***************************************************************************

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import numpy as np
import tensorflow as tf
import glob
import os

sess = tf.InteractiveSession()

datasetPath = os.getcwd() + '/../datasets.gold'
trainData = datasetPath+'/data/jet*.csv'
predictData = datasetPath+'/eval/jet*.csv'

try:
  import pandas as pd  # pylint: disable=g-import-not-at-top
except ImportError:
  pass

# Order is important for the csv-readers, so we use an OrderedDict here.
defaults = collections.OrderedDict([
    ("jpt_hard", [0.0]),
    ("jpt_hard_m", [0.0]),
    ("sub_hard", [0.0]),
    ("sub_hard_m", [0.0]),
    ("jpt_full", [0.0]),
    ("jpt_full_m", [0.0]),
    ("sum_pv", [0.0]),
    ("sum_pu", [0.0]),
    ("eta", [0.0]),
    ("phi", [0.0]),
    ("area", [0.0]),
    ("rho", [0.0]),
    ("sigma", [0.0]),
    ("rho_m", [0.0]),
    ("sigma_m", [0.0]),
    ("R", [0.0]),
    ("n_pv", [0.0]),
    ("n_pu", [0.0])
])  # pyformat: disable


types = collections.OrderedDict((key, type(value[0]))
                                for key, value in defaults.items())


def set_dpath(dpath):
    global datasetPath, trainData, predictData
    datasetPath = dpath
    trainData = datasetPath+'/data/jet*.csv'
    predictData = datasetPath+'/eval/jet*.csv'

def _get_importsJE():
  paths = glob.glob(trainData)
  if len(paths) == 0:
        print('No data found in ' + trainData)
        sys.exit(1)
  return paths


def dataset(y_name="jpt_hard", train_fraction=0.7):
  """Load the importsJE data as a (train,test) pair of `Dataset`.

  Each dataset generates (features_dict, label) pairs.

  Args:
    y_name: The name of the column to use as the label.
    train_fraction: A float, the fraction of data to use for training. The
        remainder will be used for evaluation.
  Returns:
    A (train,test) pair of `Datasets`
  """
  # Download and cache the data
  path = _get_importsJE()

  # Define how the lines of the file should be parsed
  def decode_line(line):
    """Convert a csv line into a (features_dict,label) pair."""


    # Decode the line to a tuple of items based on the types of
    # csv_header.values().
    items = tf.decode_csv(line, list(defaults.values()))



    # Convert the keys and items to a dict.
    pairs = zip(defaults.keys(), items)
    features_dict = dict(pairs)

    # Remove the label from the features_dict
    label = features_dict.pop(y_name)

    return features_dict, label

  def has_no_question_marks(line):
    """Returns True if the line of text has no question marks."""
    # split the line into an array of characters
    chars = tf.string_split(line[tf.newaxis], "").values
    # for each character check if it is a question mark
    is_question = tf.equal(chars, "j") #hack to remove the header
    any_question = tf.reduce_any(is_question)
    no_question = ~any_question

    return no_question

  def in_training_set(line):
    """Returns a boolean tensor, true if the line is in the training set."""
    # If you randomly split the dataset you won't get the same split in both
    # sessions if you stop and restart training later. Also a simple
    # random split won't work with a dataset that's too big to `.cache()` as
    # we are doing here.
    num_buckets = 1000000
    bucket_id = tf.string_to_hash_bucket_fast(line, num_buckets)
    # Use the hash bucket id as a random number that's deterministic per example
    return bucket_id < int(train_fraction * num_buckets)

  def in_test_set(line):
    """Returns a boolean tensor, true if the line is in the training set."""
    # Items not in the training set are in the test set.
    # This line must use `~` instead of `not` beacuse `not` only works on python
    # booleans but we are dealing with symbolic tensors.
    return ~in_training_set(line)

  base_dataset = (tf.contrib.data
                  # Get the lines from the file.
                  .TextLineDataset(path)
                  # drop lines with question marks.
                  .filter(has_no_question_marks))



  train = (base_dataset
           # Take only the training-set lines.
           .filter(in_training_set)
           # Cache data so you only read the file once.
           .cache()
           # Decode each line into a (features_dict, label) pair.
           .map(decode_line))

  # Do the same for the test-set.
  test = (base_dataset.filter(in_test_set).cache().map(decode_line))

  return train, test


def predict_data():
  """Load the importsJE data as a pd.DataFrame."""
  # Download and cache the data
  datapath = predictData

  allFiles = glob.glob(datapath)
  if len(allFiles) == 0:
        print('No eval data found in ' + predictData)
        sys.exit(1)
  list_ = []
  for file_ in allFiles:
    df_ = pd.read_csv(file_, header=0, names=types.keys(), dtype=types, na_values="?")
    list_.append(df_)
  df = pd.concat(list_,ignore_index=True)


  # Load it into a pandas dataframe

  outs = ['jpt_hard','jpt_hard_m','sub_hard','sub_hard_m']
  nodrops = ['jpt_full','jpt_full_m']
  out_df = pd.DataFrame()
  for k in outs+nodrops:
    out_df[k] = df[k]
    if k not in nodrops:
	    df = df.drop(k,1)
  
  # print out
  '''
  for k in out_df.keys():
    print(k,out_df[k],"\n")
  for i in range(10):
    print(out_df['jpt_hard'][i],out_df['sub_hard'][i])
  '''
  return df,out_df


