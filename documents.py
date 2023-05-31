import gradio as gr
from langchain import PromptTemplate, LLMChain
from langchain.llms import GPT4All
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.document_loaders import PyMuPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.embeddings import LlamaCppEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
import os
from dotenv import load_dotenv
from langchain.docstore.document import Document

load_dotenv()

# Need to determine the right number of threads so we run fast, but don't starve the OS
import multiprocessing
use_threads = multiprocessing.cpu_count() - 4

# Grab variables form .env
embeddings_model_name = os.environ.get("EMBEDDINGS_MODEL_NAME")
persist_directory = os.environ.get('PERSIST_DIRECTORY')

model_type = os.environ.get('MODEL_TYPE')
model_path = os.environ.get('MODEL_PATH')
model_n_ctx = os.environ.get('MODEL_N_CTX')
model_verbose = os.environ.get('MODEL_VERBOSE')
model_predict = os.environ.get('N_PREDICT')
retriever_type = os.environ.get('RTR_TYPE')
retriever_k = os.environ.get('RTR_K')
chain_type = os.environ.get('CHAIN_TYPE')

from constants import CHROMA_SETTINGS

# Model declarations moved to enviornment variabled
## NEW! Assume pre-existing document store

# HuggingFace embedding
embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

#prompt = PromptTemplate(template=template, input_variables=["question"])
callbacks = [StreamingStdOutCallbackHandler()]
# trying to switch to mpt
from ctransformers.langchain import CTransformers
llm = CTransformers(model=model_path, model_type=model_type, callbacks=callbacks, verbose=model_verbose, config={"threads":use_threads, "max_new_tokens":int(model_predict), "stream":True})

# CLI testing
#question="What is the best way to conduct a risk assessment?"
#question="What are the requirements for vulnerability scanning?"

# Load persistent Chroma Vector store
db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, client_settings=CHROMA_SETTINGS)

retriever = db.as_retriever(search_type=retriever_type, search_kwargs={'k':int(retriever_k)})

# prompt for the chain to instruct it how to do things
promptq = PromptTemplate(template="""Given the following extracted parts of a long document and a question, create a final answer with references ("SOURCES"). If you don't know the answer, just say that you don't know. Don't try to make up an answer.
ALWAYS return a "SOURCES" part in your answer.

QUESTION: {question}
==
{summaries}
==
Final Answer: """, input_variables=["summaries","question"])

# template to use for each of the contents
promptdoc = PromptTemplate( template="Content: {page_content}\nSource: {source}-p{page_number}", input_variables=["page_content", "source", "page_number"])

# Fetch the list of sources out of the index; for interest, we want to know what the LLM should be looking at
srclist = []
for doc in db.get()['metadatas']:
    if doc['source'] not in srclist:
        srclist.append(doc['source'])
# Prep text blurb for gradio interface
article="The index contains the following documents\n"+", ".join(srclist)

# Production gradio code:
def sample(question):
    # look over the db and find chunks of data related to the question
    rel_docs = retriever.get_relevant_documents(question)
    # PyMuPDF adds a ton of extra metadata which eats tokens.  (why? maybe my promptdoc isn't working)
    # Lets reformat the relevant docs to only have useful metadata
    formatted_docs = []
    for x in rel_docs:
        print("==== rel_doc ====")
        t = Document(page_content=x.page_content, metadata={'source':x.metadata['source'],'page_number':x.metadata['page_number']})
        print(t)
        formatted_docs.append(t)
    # create a new chain "with sources"
    qa_chain = load_qa_with_sources_chain(llm=llm, chain_type=chain_type, prompt=promptq, document_prompt=promptdoc)
    # Run the question against the documents
    result = qa_chain({"input_documents":formatted_docs,"question":question}, return_only_outputs=False)
    # dedup the sources that were used and produce a nice list for output
    auxlist = []
    for doc in result['input_documents']:
        if doc.metadata not in auxlist:
            auxlist.append(str(doc.metadata['source'])+"-p."+str(doc.metadata['page_number']))
    auxprint="\n".join(auxlist)

    return result['output_text'], auxprint

# Build the web interface
demo = gr.Interface(fn=sample, inputs="text", outputs=[gr.components.Textbox(label="LLM answer"),gr.components.Textbox(label="Sources used")], flagging_dir="/tmp/flagging", title="LLMQA", description="Ask questions of an LLM over a number of documents stored in a vector store", article=article)

# Run!
demo.launch(share=True, server_port=7860, server_name="0.0.0.0")

