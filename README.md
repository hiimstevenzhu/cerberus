# ceberus

an ai-based pipeline for keyword identification in real-time speech

# dependencies

openai whisper (follow the README under https://github.com/openai/whisper)
real time usage of openai whisper (https://github.com/davabase/whisper_real_time)
NOT USED: faster whisper [pip install -U openai-whisper]

# workflow:

we first implement a simple benchmark:
a speech to text model (faster whisper), which provides the most recent n words, which is used to send to a keyword detection algorithm (Boyer-Moore), of which if there are matches, we then can send an alert

consider:
nlp models for keyword extraction (not targeted) to be used to parse the text block, of which these words can be used to determine threat level

- https://prakhar-mishra.medium.com/10-popular-keyword-extraction-algorithms-in-natural-language-processing-8975ada5750c
- https://monkeylearn.com/keyword-extraction/

gpt? for contextual understanding

an ensemble of models to poll for severity levels

multi-language and language detection and automatic switching

- b) models that are trained and developed for singlish (a mixture of languages)

# Implementation requirements:

Currently, keywords must be in a format such that there are NO spaces at the beginning or the end of the keyword.

For example, valid keywords are:

- "Sir Stop"
- "I"
- "STOP NOW"

Examples of invalid keywords are:

- " hello"
- "hi there "
- " red "

# Progress:

14/05:
Started:

- Started a keyword finding algorithm:

To complete:

- Enhance the keyword finding algorithm to find number of times keywords are matched
- Implement faster-whisper

15/05
Started:

- Implemented openai-whisper (faster-whisper requires gpu to run faster)
- Integrated the keyword finding algorithm to ping when there is recognition of certain keywords

To complete:

- Enhance the keyword finding algorithm to find number of times keywords are matched, also fix it such that it matches strings of more than one word. In this case, we will be using the Boyer-Moore's algorithm.

16/05:
Completed:

- Implementing openai-whisper
- Integrated Boyer-Moore's algorithm to count the number of times a keyword is matched

Started:

- Changed the model to be able to support multiple languages. Issues arise as under "To Complete".

To complete:

- Extending to other languages, Chinese, Malay, Tamil, Hindu perfectly.

1. Boyer-Moore's does not fit well with non-roman alphabet - speaking in chinese creates problems
2. The model has a separate feature which detects some semblance of an accent and transcribes everything into that base accent language. For me, it transcribes into malay.
3. The speed is exceedingly slow, and is unable to support long sentences/conversations.
4. The model needs to be able to identify the main individual - some sort of voice recognition is required..?

To consider:

- Implementing an ensemble of models, one trained to detect each language, to poll for their confidence in terms of the language spoken (?)
- Using GPU to train a model off Singlish using the National Speech Corpus

17/05:
To start:

- Integrating a cloud server for deployment(?), and better GPU resources

23/05:
Started:

- Implemented a simple website dashboard to simulate the command and control centre.
- Effectively, this container script will now simulate the input and the access point cloud servers, which deal with data collection, input, and processing.

To complete:

- Updating of script so that we can collect information and send to the dashboard as we require.

# references

https://github.com/openai/whisper
https://github.com/davabase/whisper_real_time
