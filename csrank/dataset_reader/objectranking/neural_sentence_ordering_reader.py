import logging
import os

import h5py
import numpy as np

from csrank.constants import OBJECT_RANKING
from csrank.dataset_reader.objectranking.util import sub_sampling
from ..dataset_reader import DatasetReader

NAME = 'SentenceOrderingDatasetReader'


class SentenceOrderingDatasetReader(DatasetReader):
    def __init__(self, n_dims=25, train_obj=None, **kwargs):
        super(SentenceOrderingDatasetReader, self).__init__(learning_problem=OBJECT_RANKING,
                                                            dataset_folder='sentence_ordering', **kwargs)
        self.logger = logging.getLogger(name=NAME)
        dimensions = [25, 50, 100, 200]
        d_files = ["test_{}_dim.h5", "train_{}_dim.h5"]
        self.train_obj = train_obj
        if n_dims not in dimensions:
            n_dims = 25
        self.logger.info("Loading the dataset with {} features".format(n_dims))
        self.train_file = os.path.join(self.dirname, d_files[1]).format(n_dims)
        self.test_file = os.path.join(self.dirname, d_files[0]).format(n_dims)

        self.__load_dataset__()

    def __load_dataset__(self):
        file = h5py.File(self.train_file, 'r')
        self.X_train, self.Y_train = self.get_rankings_dict(file)
        if self.train_obj is not None:
            self.X_train, self.Y_train = self.sub_sampling_for_dictionary()
        file = h5py.File(self.test_file, 'r')
        self.X_test, self.Y_test = self.get_rankings_dict(file)
        self.logger.info("Done loading the dataset")

    def get_rankings_dict(self, file):
        lengths = file["lengths"]
        X = dict()
        Y = dict()
        for ranking_length in np.array(lengths):
            features = np.array(file["X_{}".format(ranking_length)])
            rankings = np.array(file["Y_{}".format(ranking_length)])
            X[ranking_length], Y[ranking_length] = self.X, self.rankings = features, rankings
            self.__check_dataset_validity__()
        return X, Y

    def sub_sampling_for_dictionary(self):
        X = []
        Y = []
        for n in self.X_train.keys():
            if n > self.train_obj:
                x, y = sub_sampling(NAME, self.X_train[n], self.Y_train[n], n_objects=self.train_obj)
                if len(X) == 0:
                    X = np.copy(x)
                    Y = np.copy(y)
                else:
                    X = np.concatenate([X, x], axis=0)
                    Y = np.concatenate([Y, y], axis=0)
        if self.train_obj in self.X_train.keys():
            X = np.concatenate([X, np.copy(self.X_train[self.train_obj])], axis=0)
            Y = np.concatenate([Y, np.copy(self.Y_train[self.train_obj])], axis=0)
        self.logger.info("Sampled instances {} objects {}".format(X.shape[0], X.shape[1]))
        return X, Y

    def splitter(self, iter):
        pass

    def get_train_test_datasets(self, n_datasets):
        return self.X_train, self.Y_train, self.X_test, self.Y_test

    def get_complete_dataset(self):
        pass

    def get_single_train_test_split(self):
        return self.X_train, self.Y_train, self.X_test, self.Y_test
