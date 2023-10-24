# -*- coding: utf-8 -*-
"""Chatbot with Conversational Memeory-Ankita Test.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HelZzwPn1w3wx7X9sbj2I3-aJp80OxoU

This notebook makes a question answering chain with a specified website as a context data.

# Setting up

Install dependencies
"""

!pip install langchain==0.0.189
!pip install pinecone-client
!pip install openai
!pip install tiktoken
!pip install nest_asyncio

"""Set up OpenAI API key"""

import os
os.environ["OPENAI_API_KEY"] = "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"

"""Set up Pinecone API keys"""

import pinecone

# initialize pinecone
pinecone.init(
    api_key="96e01bcd-0886-4c2d-8c3b-75e9fab99572",  # find at app.pinecone.io
    environment="us-west4-gcp-free"  # next to api key in console
)

"""# Index

**Load data from Web**

Extends from the WebBaseLoader, this will load a sitemap from a given URL, and then scrape and load all the pages in the sitemap, returning each page as a document.

The scraping is done concurrently, using WebBaseLoader. There are reasonable limits to concurrent requests, defaulting to 2 per second.

Link to the [documentation](https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/sitemap.html)
"""

# fixes a bug with asyncio and jupyter
import nest_asyncio
nest_asyncio.apply()

from langchain.document_loaders.sitemap import SitemapLoader

loader = SitemapLoader(
    "https://ind.nl/sitemap.xml",
    filter_urls=["https://ind.nl/en"]
)
docs = loader.load()

docs

"""**Split the text from docs into smaller chunks**

There are many ways to split the text. We are using the text splitter that is recommended for generic texts. For more ways to slit the text check the [documentation](https://python.langchain.com/en/latest/modules/indexes/text_splitters.html)
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1200,
    chunk_overlap  = 200,
    length_function = len,
)

docs_chunks = text_splitter.split_documents(docs)

"""Create embeddings"""

from langchain.embeddings.openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

"""**Creating a vectorstore**

A vectorstore stores Documents and associated embeddings, and provides fast ways to look up relevant Documents by embeddings.

There are many ways to create a vectorstore. We are going to use Pinecone. For other types of vectorstores visit the [documentation](https://python.langchain.com/en/latest/modules/indexes/vectorstores.html)

First you need to go to [Pinecone](https://www.pinecone.io/) and create an index there. Then type the index name in "index_name"
"""

from langchain.vectorstores import Pinecone

index_name = "chatbot"

# #create a new index
docsearch = Pinecone.from_documents(docs_chunks, embeddings, index_name=index_name)

# if you already have an index, you can load it like this
#docsearch = Pinecone.from_existing_index(index_name, embeddings)

"""If you cannot create a Pinecone account, try to use CromaDB. The following code creates a transient in-memory vectorstore. For further information check the [documentation](https://python.langchain.com/en/latest/modules/indexes/vectorstores/examples/chroma.html).

The following code block uses Croma for creating a vectorstore. Uncomment it if you don't have access to pinecone and use it instead.
"""

# from langchain.vectorstores import Chroma
# docsearch = Chroma.from_documents(docs, embeddings)

"""Vectorstore is ready. Let's try to query our docsearch with similarity search"""

query = "I run a black-owned bookstore in Brookline, MA and I would like to expand my inventory and networking outreach. I am interested in submitting a business proposal to local university in order to fulfil my needs. Approximately how long does the business proposal process take?"
docs = docsearch.similarity_search(query)
print(docs[0])

"""# Making a question answering chain
The question answering chain will enable us to generate the answer based on the relevant context chunks. See the [documentation](https://python.langchain.com/en/latest/modules/chains/index_examples/qa_with_sources.html) for more explanation.

Additionally, we can return the source documents used to answer the question by specifying an optional parameter when constructing the chain. For more information visit the [documentation](https://python.langchain.com/en/latest/modules/chains/index_examples/vector_db_qa.html#return-source-documents)
"""

from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
llm=OpenAI()

qa_with_sources = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=docsearch.as_retriever(), return_source_documents=True)

query = "I run a black-owned bookstore in Brookline, MA and I would like to expand my inventory and networking outreach. I am interested in submitting a business proposal to local university in order to fulfil my needs. Approximately how long does the business proposal process take at MIT?"
result = qa_with_sources({"query": query})
result["result"]

query = "tell me more"
result = qa_with_sources({"query": query})
result["result"]

query = "What are some of the certifications that I can obtain as a black business owner?"
result = qa_with_sources({"query": query})
result["result"]

query = "Who is the POC for business proposal at MIT?"
result = qa_with_sources({"query": query})
result["result"]

while(True):
  query = input()
  result = qa_with_sources({"query": query})
  print(result["result"])

"""Output source documents that were found for the query"""

result["source_documents"]

'''

'''