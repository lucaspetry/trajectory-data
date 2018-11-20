from core.logger import Logger
import argparse
import numpy as np


logger = Logger()
arg_parser = argparse.ArgumentParser(description='Print dataset stats.')
arg_parser.add_argument('file', help='The dataset file', type=str)
arg_parser.add_argument('--label', default='class', help='The class column (default: class)', type=str)
arg_parser.add_argument('--tid', default='tid', help='The trajectory ID column (default: tid)', type=str)
arg_parser.add_argument('--plot', action='store_true', help='Pass this argument to show the trajectory length and class size distributions.')
args = arg_parser.parse_args()

import pandas as pd
import matplotlib.pyplot as plt
import statistics as st

data = pd.read_csv(args.file)

labels = data[args.label].unique()
num_attributes = len(data.columns) - 1
num_points = len(data)
num_trajectories = len(data[args.tid].unique())
num_classes = len(labels)

traj_lengths = data[args.tid].value_counts()
class_counts = [len(data[data[args.label] == lb][args.tid].unique()) for lb in labels]

avg_traj_length = str(st.mean(traj_lengths)) + \
                    ' +- ' + str(st.stdev(traj_lengths))
avg_traj_class = str(st.mean(class_counts)) + \
                    ' +- ' + str(st.stdev(class_counts))

logger.log(Logger.INFO, "Number of attributes (incl. class):  " + str(num_attributes))
logger.log(Logger.INFO, "Number of points:                    " + str(num_points))
logger.log(Logger.INFO, "Number of trajectories:              " + str(num_trajectories))
logger.log(Logger.INFO, "Number of classes:                   " + str(num_classes))
logger.log(Logger.INFO, "Avg. trajectory length:              " + avg_traj_length)
logger.log(Logger.INFO, "Avg. # of trajectories per class:    " + avg_traj_class)
logger.log(Logger.INFO, "Max. trajectory length:              " + str(max(traj_lengths)))
logger.log(Logger.INFO, "Min. trajectory length:              " + str(min(traj_lengths)))
logger.log(Logger.INFO, "Largest class size:                  " + str(max(class_counts)) + " (class: " + str(labels[np.argmax(class_counts)]) + ")")
logger.log(Logger.INFO, "Smallest class size:                 " + str(min(class_counts)) + " (class: " + str(labels[np.argmin(class_counts)]) + ")")

if args.plot:
    f = plt.figure(1)
    plt.hist(traj_lengths)
    plt.title("Trajectory length distribution")
    plt.xlabel("Trajectory length")
    plt.ylabel("Frequency")
    f.show()

    f2 = plt.figure(2)
    plt.hist(class_counts)
    plt.title("Class size distribution")
    plt.xlabel("Class size")
    plt.ylabel("Frequency")
    f2.show()

    logger.get_answer('\nPress ENTER (RETURN) to exit...')
