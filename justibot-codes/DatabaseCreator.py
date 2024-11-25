import os
import openai
import pypdf
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone as pinecone
from langchain_community.vectorstores import Pinecone
from pinecone import ServerlessSpec, PodSpec
import time
from llm import pc, embeddings

spec = ServerlessSpec(cloud='aws', region='us-west-2')
def Delete_index(index_name):
  if index_name in pc.list_indexes().names():
      pc.delete_index(index_name)

def CreateIndex(index_name):
  pc.create_index(
          index_name,
          dimension=1536,
          metric='cosine',
          spec=spec
      )

  while not pc.describe_index(index_name).status['ready']:
      time.sleep(1)
  return True


def CreateDatabase(index_name, url):
    if (index_name not in pc.list_indexes().names()):
        CreateIndex(index_name)
        CreateDatabase(index_name, url)
        print("done")
    else:
        index = pc.Index(index_name)
        docname = url
        loader = PyPDFLoader(docname)
        documents = loader.load()
        documents = documents[0:]
        # split documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=30)
        docs = text_splitter.split_documents(documents)
        print(len(docs))

        vectordb = Pinecone.from_documents(docs, embeddings, index_name=index_name)

        while len(docs) >= index.describe_index_stats().total_vector_count:
            time.sleep(1)

        return True
