In this project, I analyze my emails and predict which emails I will reply to. I download all emails since 2017 using Gmail's API, and reserve the newest 10% as test data. 
To perform the actual classification, I use Amazon's Blazing Text algorithm, which is an implementation of Word2Vec optimized for the AWS machine learning infrastructure. It is based on representing words in a lower-dimensional space (trained from a large book corpus), which can then be used to cluster documents based on their words. Features used are the words in the email body. Unfortunately, this algorithm does not support using additional features such as sender. In the future, I plan to add analyses using different algorithms which can use different features.

See the Jupyter notebook for the analysis.

# Next steps:
## Data pipeline
- Fully refractor to object-oriented design (Make client a class that lists threads). This should make it easier to understand the main logic of the data flow.
- Persist dead letter queue to Parque for later analysis. In particular, find other locations were email body can be stored, since we're currently losing a good bit of emails due to an empty body.
- Write logs to disk.

## Data preprocessing
- Move data cleaning and preprocessing to a dedicated notebook, so we don't have to re-run it every time we restart notebook kernel. Requires defining shared environment variables for S3 locations, as well as pickling training data.
- More sophisticated preprocessing: Switch to Spacy for tokenization, since it seems to better handle the many URLs in email body. Add lemmatization. Remove stop words.


## ML
- Fine-tune hyperparameters.
- Leverage Explainable AI to analyze model behavior. In particular, identify which words are associated with distinguishing replies from no-replies.
- Use Sagemaker's Model Registry to track model performance of different model versions.
- Try different algorithms and compare performance.
