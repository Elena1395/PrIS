import os
import pandas as pd
from collections import defaultdict
from surprise import Dataset, KNNWithMeans, NormalPredictor
from surprise import SVD
from surprise.model_selection import cross_validate, KFold, train_test_split

k = 30

data = Dataset.load_builtin('ml-100k')
trainset, testset = train_test_split(data, test_size=.25)


algo = SVD()
print("SVD")
cross_validate(algo, data, measures=['RMSE'], cv=5, verbose=True)

algo=KNNWithMeans(k,sim_options={'name': 'cosine'})
print("kNN cos")
cross_validate(algo, data, measures=['RMSE'], cv=5, verbose=True)

algo=KNNWithMeans(k,sim_options={'name': 'msd'})
print("kNN msd")
cross_validate(algo, data, measures=['RMSE'], cv=5, verbose=True)

algo=KNNWithMeans(k,sim_options={'name': 'pearson'})
print("kNN pearson")
cross_validate(algo, data, measures=['RMSE'], cv=5, verbose=True)

algo=NormalPredictor()
print("NormalPredictor")
cross_validate(algo, data, measures=['RMSE'], cv=5, verbose=True)


def precision_recall_at_k(predictions, k=10, threshold=3.5):
    """Return precision and recall at k metrics for each user"""

    # First map the predictions to each user.
    user_est_true = defaultdict(list)
    for uid, _, true_r, est, _ in predictions:
        user_est_true[uid].append((est, true_r))

    precisions = dict()
    recalls = dict()
    for uid, user_ratings in user_est_true.items():

        # Sort user ratings by estimated value
        user_ratings.sort(key=lambda x: x[0], reverse=True)

        # Number of relevant items
        n_rel = sum((true_r >= threshold) for (_, true_r) in user_ratings)

        # Number of recommended items in top k
        n_rec_k = sum((est >= threshold) for (est, _) in user_ratings[:k])

        # Number of relevant and recommended items in top k
        n_rel_and_rec_k = sum(((true_r >= threshold) and (est >= threshold))
                              for (est, true_r) in user_ratings[:k])

        # Precision@K: Proportion of recommended items that are relevant
        # When n_rec_k is 0, Precision is undefined. We here set it to 0.

        precisions[uid] = n_rel_and_rec_k / n_rec_k if n_rec_k != 0 else 0

        # Recall@K: Proportion of relevant items that are recommended
        # When n_rel is 0, Recall is undefined. We here set it to 0.

        recalls[uid] = n_rel_and_rec_k / n_rel if n_rel != 0 else 0

    return precisions, recalls


kf = KFold(n_splits=5)
algo = SVD()

for trainset, testset in kf.split(data):
    algo.fit(trainset)
    predictions = algo.test(testset)
    precisions, recalls = precision_recall_at_k(predictions,  k=5, threshold=3.52)

    # Precision and recall can then be averaged over all users
    print(sum(prec for prec in precisions.values()) / len(precisions))
    print(sum(rec for rec in recalls.values()) / len(recalls))


def get_top_n(predictions, n=10):

    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n


# First train an SVD algorithm on the movielens dataset.
trainset = data.build_full_trainset()
algo = SVD()
algo.fit(trainset)

# Than predict ratings for all pairs (u, i) that are NOT in the training set.
testset = trainset.build_anti_testset()
predictions = algo.test(testset)

top_n = get_top_n(predictions, n=5)

# Print the recommended items for user
UserIndex='29'
print(top_n[UserIndex])
#print(top_n[UserIndex][0])
#print(top_n[UserIndex][0][0])

path = os.path.expanduser('~/.surprise_data/ml-100k/ml-100k/u.item')
items = pd.read_csv(path, delimiter="|", encoding='ansi', usecols=[0,1,2], names=['Uid','Fname', 'date'])
#print (items.iloc[0])
res={}
for couple in top_n[UserIndex]:
    index=(int(couple[0])-1)
    line = items.iloc[index]
    res[couple[0]]=(line["Fname"],line["date"])
    #print(res[couple[0]])
print(res)

print('User {}'.format(UserIndex))
for couple in top_n[UserIndex]:
    print('{} {}, {}'.format(couple[0], res[couple[0]], round(couple[1], 3)))
