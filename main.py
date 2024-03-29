"""
 Module for building the face recognition and facial expression analysis system
"""


import numpy as np
import data_preprocess as dp
import face_detection as fd
import feature_extraction as fe
import model_construction as mc
import model_evaluation as me


def compare_models():
    """
    The main program for building the system. And we support following kinds of model:
        1. Convolutional Neural Network (CNN)
        2. Support Vector Machine (SVM)
        3. Adaboost
        4. Multilayer Perceptron (MLP)

    Args:
        None.

    Returns:
        None.

    Note: we'll construct and evaluate several different models for emotion
          analysis. And also, we combine the Principal Component Analysis (PCA,
          eigenfaces) with the Linear Discriminant Analysis (LDA), and use the
          combination (fisherfaces) to do feature extraction for each image to
          improve our model performances.
    """

    # Give a prompt for user to specify their wanted model
    model_type = input("Please select a kind of model from the following: 'cnn', 'svm', 'adaboost', 'mlp':\n")
    while model_type not in ['cnn', 'svm', 'adaboost', 'mlp']:
        print("Your input is not correct, please try again:\n")
        model_type = input("Please select a kind of model from the following: 'cnn', 'svm', 'adaboost', 'mlp:\n")
    print(f"You entered {model_type}\n")

    # Give a prompt for user to specify their wanted dataset
    dataset = input("Please select a dataset that you want to perform from the following: 'CK+48', 'fer2013'.\n")
    while dataset not in ['CK+48', 'fer2013']:
        print("Your input is not correct, please try again:\n")
        dataset = input("Please select a dataset that you want to perform from the following: 'CK+48', 'fer2013'.\n")
    print(f"You entered {dataset}\n")

    # Give a prompt for user to specify their wanted feature extraction algorithm
    algorithm = input("Please select an feature extraction algorithm that you want to use from the following: 'eigenfaces', 'fisherfaces'.\n")
    while algorithm not in ['eigenfaces', 'fisherfaces']:
        print("Your input is not correct, please try again:\n")
        algorithm = input("Please select an feature extraction algorithm that you want to use from the following: 'eigenfaces', 'fisherfaces'.\n")
    print(f"You entered {algorithm}")

    # Load the dataset into a shuffled list of tuples
    dataset_tuple_list = dp.load_dataset(dataset)

    # # Test to see the loading result
    # for data_tuple in dataset_tuple_list:
    #     print(data_tuple)

    # Split the dataset into train, test, validation and their corresponding labels
    img_train, img_train_label, img_validation, img_validation_label, img_test, img_test_label, le = \
        dp.split_data(dataset_tuple_list)

    if model_type == 'cnn':
        # Do the feature extraction algorithm on the splitted datasets
        if algorithm == 'eigenfaces':
            # Eigenfaces: Get the pca_train and pca_test feature vectors for further training and predicting
            pca_train, pca_test, pca_validation, pca = fe.principalComponentAnalysis(img_train, img_test, img_validation,
                                                                                     img_train_label, le, num_components=625)

            # Construct and train the selected model with the input train and validation datasets
            model_trained = mc.train_model(model_type, pca_train, img_train_label, pca_validation, img_validation_label,
                                           algorithm)

            # Perform me on the trained model with the test dataset
            me.evaluate_model(model_trained, model_type, pca_test, img_test_label, algorithm)

        elif algorithm == 'fisherfaces':
            # Fisherfaces: Get the fisherfaces_train and fisherfaces_test feature vectors for further training and predicting
            fisher_train, fisher_test, fisher_validation, pca, lda = fe.fisherfaces(img_train, img_test, img_validation,
                                                                                    img_train_label, le)

            # Construct and train the selected model with the input train and validation datasets
            model_trained = mc.train_model(model_type, fisher_train, img_train_label, fisher_validation,
                                           img_validation_label, algorithm)

            # Perform me on the trained model with the test dataset
            me.evaluate_model(model_trained, model_type, fisher_test, img_test_label, algorithm)

    elif model_type == 'svm' or model_type == 'adaboost' or model_type == 'mlp':
        # Do the feature extraction algorithm on the splitted datasets
        if algorithm == 'eigenfaces':
            # Eigenfaces: Get the pca_train and pca_test feature vectors for further training and predicting
            pca_train, pca_test, pca_validation, pca = fe.principalComponentAnalysis(img_train, img_test, img_validation,
                                                                                     img_train_label, le, num_components=625)

            # Construct and train the selected model
            model_trained = mc.train_model(model_type, pca_train, img_train_label)
            # Evaluate trained model
            me.evaluate_model(model_trained, model_type, pca_test, img_test_label)

        elif algorithm == 'fisherfaces':
            # Fisherfaces: Get the fisherfaces_train and fisherfaces_test feature vectors for further training and predicting
            fisher_train, fisher_test, fisher_validation, pca, lda = fe.fisherfaces(img_train, img_test, img_validation,
                                                                                    img_train_label, le)

            # Construct and train the selected model
            model_trained = mc.train_model(model_type, fisher_train, img_train_label)
            # Evaluate trained model
            me.evaluate_model(model_trained, model_type, fisher_test, img_test_label)

    else:
        print("ERROR: invalid model type!")
        return None


def recognize_emotion(name, mode, dataset):
    """
        The main program for building the system. And we support following kinds of model:
            1. Convolutional Neural Network (CNN)
            2. Support Vector Machine (SVM)
            3. Adaboost
            4. Multilayer Perceptron (MLP)

        Args:
            name: path of the photo for recognizing
            mode: mode used for face detection, 'auto' or 'manual
            dataset: dataset used for face recognition, 'CK+48' or 'fer2013'

        Returns:
            predicted: emotion prediction (numerical) of detected faces using cnn and fisherfaces
            recognition: emotion recognition (categorical) of detected faces using cnn and fisherfaces

        Note: result will be printed to standard output, accuracy needs to be improved.
    """

    # Load the dataset into a shuffled list of tuples
    dataset_tuple_list = dp.load_dataset(dataset)

    # Split the dataset into train, test, validation and their corresponding labels
    img_train, img_train_label, img_validation, img_validation_label, img_test, img_test_label, le = \
        dp.split_data(dataset_tuple_list)

    # Fisherfaces: Get the fisherfaces_train and fisherfaces_test feature vectors for further training and predicting
    fisher_train, fisher_test, fisher_validation, pca, lda = fe.fisherfaces(img_train, img_test, img_validation,
                                                                       img_train_label, le)

    # Construct and train the selected model with the input train and validation datasets
    model_trained = mc.train_model('cnn', fisher_train, img_train_label, fisher_validation,
                                   img_validation_label, 'fisherfaces')

    # detect faces in photo and get coordinates of them
    face_coordinates, resized_list = fd.detect_face(name, mode)

    # project faces to fisherfaces
    face_column_matrix = fe.constructRowMatrix(np.array(resized_list))
    pca_face = pca.transform(face_column_matrix)
    fisherfaces_face = lda.transform(pca_face)

    # use trained cnn to recognize emotions
    fisherfaces_face = fisherfaces_face.reshape(-1, 1, 6)
    prediction = model_trained.predict(fisherfaces_face)
    recognized = np.argmax(prediction, axis=1)
    print(f'\nprediction:\n{prediction}\nrecognized:\n{recognized}')

    return prediction, recognized


# Main program
if __name__ == '__main__':
    compare_models()
    # recognize_emotion('detect_face/multi1.jpg', 'auto', 'CK+48')
