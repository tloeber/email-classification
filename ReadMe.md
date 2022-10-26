In this project, I analyze my emails and predict which emails I will reply to. I download all emails since 2017 using Gmail's API, and reserve the newest 10% as test data. 
To perform the actual classification, I use Amazon's Blazing Text algorithm, which is an implementation of Word2Vec optimized for the AWS machine learning infrastructure. It is based on representing words in a lower-dimensional space (trained from a large book corpus), which can then be used to cluster documents based on their words. Features used are the words in the email body. Unfortunately, this algorithm does not support using additional features such as sender. In the future, I plan to add analyses using different algorithms which can use different features.

See the Jupyter notebooks for the analysis.

# Next steps:
## Data pipeline
- Fully refractor to object-oriented design (Make client a class that lists threads). This should make it easier to understand the main logic of the data flow.
- Oversample using SMOTE etc, rather than w/ replacement.
- Add description and explanation to ReadMe.
- Persist raw data, so we can re-run transformation steps more easily. (Try delta lake + Databricks medallion architecture?)
- Persist dead letter queue to Parque for later analysis. In particular, find other locations were email body can be stored, since we're currently losing a good bit of emails due to an empty body.
- Write logs to disk.

## Data preprocessing
- More sophisticated preprocessing: Switch to Spacy for tokenization, since it seems to better handle the many URLs in email body. Add lemmatization. Remove stop words.


## ML
- Leverage Explainable AI to analyze model behavior. In particular, identify which words are associated with distinguishing replies from no-replies.
- Use Sagemaker Model Projects, Registry and Experiments to track model performance of different model and data versions.
- Add incremental training of final model using validation data.
- Try different algorithms and compare performance.