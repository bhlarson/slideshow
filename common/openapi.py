from tenacity import retry, wait_random_exponential, stop_after_attempt
import numpy as np
import pprint
import openai
import time
import hashlib
import json

@retry(wait=wait_random_exponential(max=5), stop=stop_after_attempt(6))
def compute_embedding(text, engine="text-embedding-ada-002"):
    # replace newlines, which can negatively affect performance.
    results = openai.Embedding.create(input=[text], engine=engine)
    return results

@retry(wait=wait_random_exponential(max=5), stop=stop_after_attempt(6))
def compute_completion(prompt, engine="text-davinci-003", temperature=1.0, max_tokens=512 ):
    response = openai.Completion.create(
            engine=engine,
            prompt= prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
    return response

class openapi(object):
    def __init__(self, creds, text_engine="text-embedding-ada-002", match_engine="text-embedding-ada-002", completions_engine="text-davinci-003"):

        openai.api_key = creds['key']
        if creds['api_type'] == 'azure':
            openai.api_type = creds['api_type']
            openai.api_base = creds['url']
            openai.api_version = "2022-12-01"

        self.text_engine = text_engine
        self.match_engine = match_engine
        self.completions_engine = completions_engine

    def embedding(self, text, text_model = True):
        text = text.replace("\n", " ")
        tic = time.perf_counter()
        if text_model:
            text_embedding = compute_embedding(text, engine = self.text_engine)
        else:
            text_embedding = compute_embedding(text, engine = self.match_engine)
        toc = time.perf_counter()

        return text_embedding["data"][0]["embedding"], toc - tic

    def match(self, text, embeddings):
        text = text.replace("\n", " ")
        tic = time.perf_counter()
        embedding = compute_embedding(text, engine = self.match_engine)
        toc = time.perf_counter()

        match_dot = []
        for text_embedding in enumerate(embeddings):
            dot_product = np.dot(text_embedding, embedding)
            match_dot.append(dot_product.item())

        iMax = match_dot.index(max(match_dot))

        return iMax, match_dot, toc - tic
    
    def completion(self, prompt, text, max_tokens=512, temperature=1.0):
   
        # replace newlines, which can negatively affect performance.
        scriptText = '{}:\n\n {}'.format(prompt, text.replace('\r', ' ').replace('\n', ' '))

        tic = time.perf_counter()
        response = compute_completion(scriptText, engine=self.completions_engine, max_tokens=max_tokens, temperature=temperature )
        response = openai.Completion.create(
            engine=self.completions_engine,
            prompt= scriptText,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        toc = time.perf_counter()
