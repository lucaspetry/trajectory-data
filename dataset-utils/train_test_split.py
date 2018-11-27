import argparse
import pandas as pd
from sklearn.model_selection import train_test_split


# Parse args
arg_parser = argparse.ArgumentParser(description='Print dataset stats.')
arg_parser.add_argument('input_file',
                        help='The input file.',
                        type=str)
arg_parser.add_argument('train_file',
                        help='The output train file.',
                        type=str)
arg_parser.add_argument('test_file',
                        help='The output test file.',
                        type=str)
arg_parser.add_argument('--label',
                        default='class',
                        help='The class column (default: class).',
                        type=str)
arg_parser.add_argument('--tid',
                        default='tid',
                        help='The trajectory ID column (default: tid).',
                        type=str)
arg_parser.add_argument('--train_size',
                        default=0.7,
                        help='The size of the training set. Must range from' +
                        ' 0 and 1 (default: 0.7).',
                        type=float)
arg_parser.add_argument('--random_seed',
                        help='The random seed.',
                        type=int)
arg_parser.add_argument('--stratify',
                        action='store_true',
                        help='Perform stratified train/test split.')
args = arg_parser.parse_args()


# Read file to dataframe
data = pd.read_csv(args.input_file)
tids = data[args.tid].unique()
labels = [data.loc[data[args.tid] == t, args.label].values[0] for t in tids]

train, test = train_test_split(tids,
                               train_size=args.train_size,
                               random_state=args.random_seed,
                               stratify=labels if args.stratify else None)

data.loc[data[args.tid].isin(train), ].to_csv(args.train_file, index=False)
data.loc[data[args.tid].isin(test), ].to_csv(args.test_file, index=False)
