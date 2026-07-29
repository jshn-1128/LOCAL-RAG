# Machine Learning Basics

Machine Learning (ML) is a subset of artificial intelligence that enables systems to learn and improve from experience without explicit programming.

## Types of Machine Learning

### Supervised Learning
Training on labeled data where the correct output is known. Used for:
- **Classification**: Predicting categories (spam/not spam)
- **Regression**: Predicting continuous values (price prediction)

### Unsupervised Learning
Finding patterns in unlabeled data. Used for:
- **Clustering**: Grouping similar data points (customer segmentation)
- **Dimensionality Reduction**: Reducing feature count (PCA)

### Reinforcement Learning
Learning through trial and error using rewards and penalties.

## Evaluation Metrics

### Classification Metrics
- **Accuracy**: (TP + TN) / (TP + TN + FP + FN)
- **Precision**: TP / (TP + FP)
- **Recall**: TP / (TP + FN)
- **F1 Score**: 2 * (Precision * Recall) / (Precision + Recall)

### Regression Metrics
- **Mean Squared Error (MSE)**
- **Mean Absolute Error (MAE)**
- **R-squared (R²)**

## Common Algorithms

### Classical ML
- Linear Regression
- Logistic Regression
- Decision Trees and Random Forests
- Support Vector Machines (SVM)
- K-Nearest Neighbors (KNN)
- K-Means Clustering

### Deep Learning
- Neural Networks
- Convolutional Neural Networks (CNNs) for images
- Recurrent Neural Networks (RNNs) for sequences
- Transformers for NLP tasks

## Feature Engineering

Feature engineering is the process of transforming raw data into features that better represent the underlying problem to predictive models.

## Overfitting and Underfitting

- **Overfitting**: Model memorizes training data, fails on new data
- **Underfitting**: Model is too simple to capture patterns
