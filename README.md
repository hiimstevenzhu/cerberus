# ceberus

a ai-based pipeline for keyword identification in real-time speech

# dependencies

openai whisper (follow the README under https://github.com/openai/whisper)
faster whisper [pip install -U openai-whisper]
real time usage of openai whisper (https://github.com/davabase/whisper_real_time)

# workflow:

we first implement a simple benchmark:
a speech to text model (faster whisper), which provides the most recent n words, which is used to send to a keyword detection algorithm (Boyer-Moore), of which if there are matches, we then can send an alert

consider:
nlp models for keyword extraction (not targetted) to be used to parse the text block, of which these words can be used to determine threat level

- https://prakhar-mishra.medium.com/10-popular-keyword-extraction-algorithms-in-natural-language-processing-8975ada5750c
- https://monkeylearn.com/keyword-extraction/

gpt? for contextual understanding

an ensemble of models to poll for severity levels

multi-language and language detection and automatic switching

- b) models that are trained and developed for singlish (a mixture of languages)

# Work progress:

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

# references

https://github.com/openai/whisper
https://github.com/davabase/whisper_real_time
