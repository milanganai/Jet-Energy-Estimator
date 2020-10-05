#!/usr/bin/python
# ***************************************************************************
# * @File:       train_eval.py
# *
# * @Brief:      builds training model and eval on given datasets
# *              train_eval.py --outdir <dir> --datasets <dataset>
# *
# * @Author:     Milan Ganai
# * 
# * @Creation:   Dec 2017
# ***************************************************************************

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf
import timeit
import importsJE
import os
import sys

#modify these parameters: Start
STEPS = 2000
PRICE_NORM_FACTOR = 1
regress = ['Linear','DNN','DNNs']
estimators = ["Ftrl","Adagrad", "Adam", "Momentum", "RMSProp"]
targets = ["jpt_hard","jpt_hard_m"]
outdir="outdir"
#modify these parameters: End
if '--try' in sys.argv:
    STEPS = 200
    PRICE_NORM_FACTOR = 1
    regress = ['DNN']
    estimators = ["Adam"]
    targets = ["jpt_hard","jpt_hard_m"]
    outdir="outdir"
if '--datasets' in sys.argv and sys.argv.index('--datasets') < len(sys.argv):
    i = sys.argv.index('--datasets')
    dpath = sys.argv[i+1]
    importsJE.set_dpath(dpath)
if '--outdir' in sys.argv and sys.argv.index('--outdir') < len(sys.argv):
    i = sys.argv.index('--outdir')
    outdir = sys.argv[i+1]
if '--help' in sys.argv:
    print('train_evay.py [options]')
    print('--try           :try with smaller')
    print('--outdir  <dir> :specify output <dir>')
    print('--datsets <dir> :specify datasets <dir>/{eval, data}')
    print('--help          :print this')
    sys.exit(1)
   

    
if os.path.exists(outdir):
    print(outdir+" exists!")
    sys.exit(1)

os.mkdir(outdir)


def run(opt,r,tgt):
  """Builds, trains, and evaluates the model."""

  out = outdir +"/" + r + "_" + opt + "_" + tgt + ".csv" 

  #print(out)

  fp = open(out,'w')
  fp.write('%15s, %15s, %15s\n' % ('predicted','hard_jpt','sub_jpt'))
  input_dict, output_dict = importsJE.predict_data()

  #input_dict, output_dict = importsJE.predict_data()
  (train, test) = importsJE.dataset(tgt,0.8)

  # Switch the labels to units of thousands for better convergence.
  def to_thousands(features, labels):
    return features, labels / PRICE_NORM_FACTOR


  # Build the training input_fn.
  def input_train():
    return (
        # Shuffling with a buffer larger than the data set ensures
        # that the examples are well mixed.
        train.shuffle(1000).batch(128)
        # Repeat forever
        .repeat().make_one_shot_iterator().get_next())

  # Build the validation input_fn.
  def input_test():
    return (test.shuffle(1000).batch(128)
            .make_one_shot_iterator().get_next())

  feature_columns = [
      tf.feature_column.numeric_column(key="jpt_full"),
      tf.feature_column.numeric_column(key="jpt_full_m"),
      tf.feature_column.numeric_column(key="sum_pv"),
      tf.feature_column.numeric_column(key="sum_pu"),
      tf.feature_column.numeric_column(key="eta"),
      tf.feature_column.numeric_column(key="phi"),
      tf.feature_column.numeric_column(key="area"),
      tf.feature_column.numeric_column(key="rho"),
      tf.feature_column.numeric_column(key="sigma"),
      tf.feature_column.numeric_column(key="rho_m"),
      tf.feature_column.numeric_column(key="sigma_m"),
      tf.feature_column.numeric_column(key="R"),
      tf.feature_column.numeric_column(key="n_pv"),
      tf.feature_column.numeric_column(key="n_pu"),
  ]
  
  linear_feature_columns = [
      tf.feature_column.numeric_column(key="jpt_full"),
      tf.feature_column.numeric_column(key="rho"),
      tf.feature_column.numeric_column(key="phi"),
      tf.feature_column.numeric_column(key="n_pu"),
      tf.feature_column.numeric_column(key="sum_pu"),
      tf.feature_column.numeric_column(key="sigma"),
      tf.feature_column.numeric_column(key="jpt_full_m"),
      tf.feature_column.numeric_column(key="rho_m"),
      tf.feature_column.numeric_column(key="sigma_m"),
      tf.feature_column.numeric_column(key="R"),
  ]
  dnn_feature_columns = [
      tf.feature_column.numeric_column(key="n_pv"),
      tf.feature_column.numeric_column(key="area"),
  ]

  # Build the Estimator.
  if (r == 0):
    model = tf.estimator.LinearRegressor(feature_columns=feature_columns, optimizer=opt)
  elif (r == 1):
    model = tf.estimator.DNNRegressor(hidden_units=[20, 40, 40, 20], feature_columns=feature_columns, optimizer=opt)
  else:
    model = tf.estimator.DNNRegressor(hidden_units=[20, 40, 40, 20], feature_columns=linear_feature_columns+dnn_feature_columns)


  start_time = timeit.default_timer()
  # Train the model.
  # By default, the Estimators log output every 100 steps.
  model.train(input_fn=input_train, steps=STEPS)
  elapsed1 = timeit.default_timer() - start_time

  #print(opt,r,"Train Elapsed Time =",elapsed1)



  # Evaluate how the model performs on data it has not yet seen.
  eval_result = model.evaluate(input_fn=input_test)

  for key in sorted(eval_result):
    print("%s: %s" % (key, eval_result[key]))
  

  # The evaluation returns a Python dictionary. The "average_loss" key holds the
  # Mean Squared Error (MSE).
  average_loss = eval_result["average_loss"]

  #print eval_result.keys()

  # Convert MSE to Root Mean Square Error (RMSE).
  print("\n" + 80 * "*")
  print("\nRMS error for the test set: ${:.0f}"
        .format(PRICE_NORM_FACTOR * average_loss**0.5))

  elapsed2 = timeit.default_timer() - start_time
  print(opt,r,"Train Elapsed Time =",elapsed2-elapsed1)

  # Run the model in prediction mode.
  input_dict, output_dict = importsJE.predict_data()
  predict_input_fn = tf.estimator.inputs.pandas_input_fn(
      input_dict, shuffle=False)
  predict_results = model.predict(input_fn=predict_input_fn)

  elapsed3 = timeit.default_timer() - start_time
  print(opt,r,"Predict Elapsed Time =",elapsed3-elapsed2)

  # Print the prediction results.
  for i, prediction in enumerate(predict_results):
    fp.write('%15.8f, %15.8f, %15.8f\n'% (prediction["predictions"][0], output_dict[tgt][i],output_dict[tgt.replace('jpt','sub')][i]))

  fp.close()

def main(argv):
  for e in estimators:
	for r in regress:
		for tgt in targets:
                        print("\n" + 80 * "=")
			print(e,r,tgt)
  			start_time = timeit.default_timer()
			try:
				run(e,r,tgt)
			except:
				print("Aborted")
			elapsed = timeit.default_timer() - start_time
  			print(e,r,"Total Elapsed Time =",elapsed)


if __name__ == "__main__":
  # The Estimator periodically generates "INFO" logs; make these logs visible.
  tf.logging.set_verbosity(tf.logging.INFO)
  tf.app.run(main=main)

