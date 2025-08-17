import re
import nltk
import numpy as np
from nltk.corpus import wordnet as wn

class ObjectiveTest:

    def __init__(self, data, noOfQues):
        
        self.summary = data
        self.noOfQues = noOfQues

    def get_trivial_sentences(self):
        sentences = nltk.sent_tokenize(self.summary)
        trivial_sentences = list()
        for sent in sentences:
            trivial = self.identify_trivial_sentences(sent)
            if trivial:
                trivial_sentences.append(trivial)
            else:
                continue
        return trivial_sentences

    def identify_trivial_sentences(self, sentence):
        # Tokenize first
        tokens = nltk.word_tokenize(sentence)
    
        # Quick guards
        if len(tokens) < 4:
            return None
    
        # POS tag needs a list of tokens, not a string
        tags = nltk.pos_tag(tokens)
        if tags and tags[0][1] == "RB":  # first token is an adverb
            return None
    
        noun_phrases = []
        grammer = r"""
            CHUNK: {<NN>+<IN|DT>*<NN>+}
                   {<NN>+<IN|DT>*<NNP>+}
                   {<NNP>+<NNS>*}
        """
        chunker = nltk.RegexpParser(grammer)
    
        # We already have POS tags—reuse them
        pos_tokens = tags
        tree = chunker.parse(pos_tokens)
    
        for subtree in tree.subtrees():
            if subtree.label() == "CHUNK":
                temp = " ".join(sub[0] for sub in subtree).strip()
                noun_phrases.append(temp)
    
        replace_nouns = []
        for word, _ in tags:
            for phrase in noun_phrases:
                if phrase and phrase[0] == "'":
                    break
                if word in phrase:
                    for phrase_word in phrase.split()[-2:]:
                        replace_nouns.append(phrase_word)
                    break
            if len(replace_nouns) == 0:
                replace_nouns.append(word)
            break
    
        if len(replace_nouns) == 0:
            return None
    
        val = min(len(i) for i in replace_nouns)
    
        trivial = {
            "Answer": " ".join(replace_nouns),
            "Key": val,
            "Similar": self.answer_options(replace_nouns[0]) if len(replace_nouns) == 1 else []
        }
    
        replace_phrase = " ".join(replace_nouns)
        blanks_phrase = ("__________" * len(replace_nouns)).strip()
        expression = re.compile(re.escape(replace_phrase), re.IGNORECASE)
        sentence = expression.sub(blanks_phrase, str(sentence), count=1)
        trivial["Question"] = sentence
        return trivial


    @staticmethod
    def answer_options(word):
        # Find noun synsets for the word
        synsets = wn.synsets(word, pos="n")
        if not synsets:
            return []
    
        # Use the first synset that actually has a hypernym
        for syn in synsets:
            hypers = syn.hypernyms()
            if not hypers:
                continue
            # Use the first hypernym and get its hyponyms for distractors
            hypos = hypers[0].hyponyms()
            similar = []
            for h in hypos:
                name = h.lemmas()[0].name().replace("_", " ")
                if name.lower() != word.lower():
                    similar.append(name)
                if len(similar) >= 8:
                    break
            return similar
    
        # No hypernyms found for any synset -> no options
        return []


    def generate_test(self):
        trivial_pair = self.get_trivial_sentences()
        question_answer = [d for d in trivial_pair if d and d.get("Key", 0) > int(self.noOfQues)]
    
        if not question_answer:
            return [], []  # let the caller flash a message
    
        target_n = min(int(self.noOfQues), len(question_answer))
        question, answer = [], []
        from random import shuffle
        shuffle(question_answer)
        for qa in question_answer[:target_n]:
            if qa["Question"] not in question:
                question.append(qa["Question"])
                answer.append(qa["Answer"])
        return question, answer
    
