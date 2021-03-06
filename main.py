# coding=utf-8
from rawdata import data2vec
from bayesian import MultiNomialNB, BernoulliNB
from randomdata import *
from report import accuracyMetric, showMetric
from features import *
import time



vecs = data2vec('trec06c/full/index', 5000)
groups = randomSplit2(vecs[0]+vecs[1], 0.5)

trainset = groups[0]
testset = groups[1]
featurenum = 10


classifier = BernoulliNB()
classifier.train(trainset, MutualInfo(featurenum))
predicted = classifier.predict([sample[1] for sample in testset])
expected = [sample[0] for sample in testset]
showMetric(accuracyMetric(expected, predicted))


starttime = time.time()

classifier = BernoulliNB()
classifier.train(trainset, MyExtractor(featurenum))
predicted = classifier.predict([sample[1] for sample in testset])
expected = [sample[0] for sample in testset]
showMetric(accuracyMetric(expected, predicted))

middletime1 = time.time()
print middletime1 - starttime
print

classifier = BernoulliNB()
classifier.train(trainset, CombineExtractor(featurenum))
predicted = classifier.predict([sample[1] for sample in testset])
expected = [sample[0] for sample in testset]
showMetric(accuracyMetric(expected, predicted))


middletime2 = time.time()
print middletime2 - middletime1
print

classifier = BernoulliNB()
classifier.train(trainset, SpecialExtractor(featurenum))
predicted = classifier.predict([sample[1] for sample in testset])
expected = [sample[0] for sample in testset]
showMetric(accuracyMetric(expected, predicted))

# classifier = MultiNomialNB()
# classifier.train(trainset, MutualInfo(featurenum))
# predicted = classifier.predict([sample[1] for sample in testset])
# expected = [sample[0] for sample in testset]
# showMetric(accuracyMetric(expected, predicted))

endtime = time.time()
print endtime - middletime2
