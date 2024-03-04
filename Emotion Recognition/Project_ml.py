import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score,\
    f1_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier
import time

sns.set()
sns.color_palette("rocket")

file = "Tweets.csv"
df = pd.read_csv(file)

tv = TfidfVectorizer()
tv.fit(df["Tweets"])
X = tv.transform(df["Tweets"])
Y = df["Feelings"]

x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=1)


def confusion_plot(model_confusion, model_name):
    emotions = ["Anger", "Disgust", "Fear", "Happiness", "Sadness", "Surprise"]
    ax = sns.heatmap(model_confusion, annot=True, fmt="d", cmap="rocket_r")
    ax.set_xlabel("Predicted label", labelpad=20)
    ax.xaxis.set_ticklabels(emotions)
    ax.set_ylabel("True label", labelpad=20)
    ax.yaxis.set_ticklabels(emotions)
    ax.set_title(f"Confusion Matrix for {model_name}", pad=20)
    plt.show()


def best_params(model, param_grid):
    cv = GridSearchCV(model, param_grid, n_jobs=-1, verbose=2)  # verbose=2
    cv.fit(x_train, y_train)

    return cv.best_params_


def model_classification(model):
    model = model
    model.fit(x_train, y_train)
    model_prediction = model.predict(x_test)
    class_report = classification_report(y_test, model_prediction)
    model_confusion = confusion_matrix(y_test, model_prediction)
    accuracy = accuracy_score(y_test, model_prediction)
    precision = precision_score(y_test, model_prediction, average="weighted")
    recall = recall_score(y_test, model_prediction, average="weighted")
    f1 = f1_score(y_test, model_prediction, average="weighted")

    print(f"Report:\n{class_report}")
    print(f"Accuracy: {accuracy}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"F-1: {f1}")

    return model_confusion


# K Nearest Neighbors

kneighbors_time_start = time.time()
print("\n~ K Nearest Neighbors ~")

kneighbors_model = KNeighborsClassifier()
kneighbors_grid = {"n_neighbors": [n for n in range(1, 100)]}
kneighbors_params_neighbors = best_params(kneighbors_model, kneighbors_grid)["n_neighbors"]

print(f"Best value for \"n_neighbors\" parameter: {kneighbors_params_neighbors}")

kneighbors_model = KNeighborsClassifier(n_neighbors=kneighbors_params_neighbors)
kneighbors_confusion = model_classification(kneighbors_model)

kneighbors_time_end = time.time()
kneighbors_time = kneighbors_time_end - kneighbors_time_start

print(f"\nTotal time: {kneighbors_time}")

confusion_plot(kneighbors_confusion, "K Nearest Neighbors")

# Decision Tree Classifier

decision_tree_time_start = time.time()
print("\n~ Decision Tree Classifier ~")

decision_tree_model = DecisionTreeClassifier(random_state=1)
decision_tree_grid = {"max_depth": [2, 4, 8, 16, 32, 64, 128, None], "min_samples_leaf": [n for n in range(2, 65, 2)]}
decision_trees_params_max_depth = best_params(decision_tree_model, decision_tree_grid)["max_depth"]
decision_trees_params_min_leaf = best_params(decision_tree_model, decision_tree_grid)["min_samples_leaf"]

print(f"Best value for \"max_depth\" parameter: {decision_trees_params_max_depth}")
print(f"Best value for \"min_samples_leaf\" parameter: {decision_trees_params_min_leaf}")

decision_tree_model = DecisionTreeClassifier(random_state=1, max_depth=decision_trees_params_max_depth,
                                             min_samples_leaf=decision_trees_params_min_leaf)
decision_tree_confusion = model_classification(decision_tree_model)

decision_tree_time_end = time.time()
decision_tree_time = decision_tree_time_end - decision_tree_time_start

print(f"\nTotal time: {decision_tree_time}")

confusion_plot(decision_tree_confusion, "Decision Tree Classifier")

# Multinomial Naive Bayes

naive_bayes_time_start = time.time()
print("\n~ Multinomial Naive Bayes ~")

naive_bayes_model = MultinomialNB()
naive_bayes_grid = {"alpha": [n / 10 for n in range(1, 11)], "force_alpha": [True, False]}
naive_bayes_alpha = best_params(naive_bayes_model, naive_bayes_grid)["alpha"]
naive_bayes_force_alpha = best_params(naive_bayes_model, naive_bayes_grid)["force_alpha"]

print(f"Best value for \"alpha\" parameter: {naive_bayes_alpha}")
print(f"Best value for \"force_alpha\" parameter: {naive_bayes_force_alpha}")

naive_bayes_model = MultinomialNB(alpha=naive_bayes_alpha, force_alpha=naive_bayes_force_alpha)
naive_bayes_confusion = model_classification(naive_bayes_model)

naive_bayes_time_end = time.time()
naive_bayes_time = naive_bayes_time_end - naive_bayes_time_start

print(f"\nTotal time: {naive_bayes_time}")

confusion_plot(naive_bayes_confusion, "Multinomial Naive Bayes")

# Linear Classifier with Stochastic Gradient Descent

sgd_time_start = time.time()
print("\n~ Linear Classifier with Stochastic Gradient Descent ~")

sgd_model = SGDClassifier(random_state=1)
sgd_grid = {"alpha": [n / 10000 for n in range(1, 50)], "max_iter": [n for n in range(1000, 5000, 25)]}
sgd_alpha = best_params(sgd_model, sgd_grid)["alpha"]
sgd_max_iter = best_params(sgd_model, sgd_grid)["max_iter"]

print(f"Best value for \"alpha\" parameter: {sgd_alpha}")
print(f"Best value for \"max_iter\" parameter: {sgd_max_iter}")

sgd_model = SGDClassifier(random_state=1, alpha=sgd_alpha, max_iter=sgd_max_iter)
sgd_confusion = model_classification(sgd_model)

sgd_time_end = time.time()
sgd_time = sgd_time_end - sgd_time_start

print(f"\nTotal time:{sgd_time}")

confusion_plot(sgd_confusion, "Linear Classifier with Stochastic Gradient Descent")

# Random Forest Classifier

random_forest_time_start = time.time()
print("\n~ Random Forest Classifier ~")

random_forest_model = RandomForestClassifier(random_state=1, oob_score=True)
random_forest_grid = {"n_estimators": [n for n in range(25, 500, 25)], "max_depth": [2, 4, 8, 16, 32, 64, 128, None]}
random_forest_estimators = best_params(random_forest_model, random_forest_grid)["n_estimators"]
random_forest_max_depth = best_params(random_forest_model, random_forest_grid)["max_depth"]

print(f"Best value for \"n_estimators\" parameter: {random_forest_estimators}")
print(f"Best value for \"max_depth\" parameter: {random_forest_max_depth}")

random_forest_model = RandomForestClassifier(random_state=1, oob_score=True, n_estimators=random_forest_estimators,
                                             max_depth=random_forest_max_depth)
random_forest_confusion = model_classification(random_forest_model)

random_forest_time_end = time.time()
random_forest_time = random_forest_time_end - random_forest_time_start

print(f"\nTotal time: {random_forest_time}")

confusion_plot(random_forest_confusion, "Random Forest Classifier")
