In this project, I analyze my emails and predict which emails I will reply to. To create the data set, I download all emails since 2017 using Gmail's API, and reserve the newest 10% as test data.
To perform the actual classification, I use BlazingText, which is a classification algorithm based on Amazon's optimization of Word2Vec. It is based on representing words in a lower-dimensional space (trained from a large book corpus), which can then be used to cluster documents based on their words. Features used are the words in the email body. Unfortunately, this algorithm does not support using additional features such as sender. In the future, I plan to add analyses using different algorithms which can use different features.

See the Jupyter notebooks for the analysis, and the `data-pipeline` folder for how I create the data set.

# Lessons so far

While Amazon Sagemaker  offers an amazing ecosystem that makes it much easier to productionize machine learning models - compared to piecing together the different components from different vendors, or even reinventing the wheel by building a ML platform yourself - I'm struck by how much undifferentiated heavy lifting is still necessary in order to piece these components together. When I first used Sagemaker Notebooks a few years ago, I was impressed because I did not have the expectation of it providing an entire ML platform, and because I was training a model I was already familiar with.

This time, I expected Sagemaker to make it easy to quickly try out a variety of inbuilt algorithms and out-of-the-box models, so I could focus on higher-level tasks such as leveraging explainable-AI in order to compare how these different algorithms make decisions.
However, it turned out that it still requires a lot of undifferentiated heavy lifting to train an inbuilt model such such as a BlazingText classifier.
I think the reason for this is that **Sagemaker does not follow good object-oriented design that defines standard interfaces between components, which would allow easily swapping out one algorithm for another.**

Of course, the best solution to this would be a greater standardization of interfaces between different ML libraries and frameworks, rather than defining these interfaces at the library level.
 I hope this will happen in the medium-term, but this is clearly not an easy task because it poses a coordination problem (and to some extent even a
[collective-action dilemma](https://en.wikipedia.org/wiki/Collective_action_problem)). Thus, the best solution for the short term may be to create a higher-level library that provides wrappers around particular libraries and implements adapters to allow standardized interfaces.
 I think the lowest-hanging fruit is creating a wrapper class for *datasets*: A common frustration I encountered with Sagemaker BlazingText was that it allowed two different input formats (JSON Lines and plaintext - both with additional specific requirements), and after deciding on one, it frequently turned out down the line that specific features required one or the other of these input formats. One would hope that the documentation would tell you beforehand, so that you are aware of the trade-offs when deciding on which input format to use, but unfortunately it is not. Even worse, for one important feature – Clarify's Explainable AI – required the predictor to output JSON, which turned out to not be possible to achieve for BlazingText at all (which was also not mentioned in the documentation).
At the same time, I've started to look into *declarative machine learning* using [Ludwig](https://ludwig.ai/latest/), which may offer the best starting point for abstracting the undifferentiated heavy lifting from data scientists.

# Current work

Trying out *declarative machine learning* using [Ludwig](https://ludwig.ai/latest/).
If this framework is production-ready, it will be a game-changer!

# Next steps

## Data pipeline

- Fully refractor to object-oriented design (Make client a class that lists threads). This should make it easier to understand the main logic of the data flow.
- Document in separate ReadMe. Explain architectural decisions.
- Persist raw data, so we can re-run transformation steps more easily. (Try delta lake + Databricks medallion architecture?)
- Persist dead letter queue to Parque for later analysis. In particular, find other locations were email body can be stored, since we're currently losing a good bit of emails due to an empty body.
- Write logs to disk.

## Data preprocessing

- Oversample using SMOTE etc, rather than w/ replacement.
- More sophisticated preprocessing: Switch to Spacy for tokenization, since it seems to better handle the many URLs in email body. Add lemmatization. Remove stop words.
- Handle preprocessing through a sagemaker transformer, so we can track data versions through sagemaker experiments.

## ML

- ~~Leverage Explainable AI to analyze model behavior. In particular, identify which words are associated with distinguishing replies from no-replies.~~ Not directly supported for BlazingText, but use once implemented other algorithms.
- Use Sagemaker Experiments/Model Registry to track model performance of different model and data versions.
- Use Sagemaker Projects/Pipelines to run end-to-end once we're past the experimental/interactive phase.
- Add incremental training of final model using validation data.
- Try different algorithms and compare performance.
