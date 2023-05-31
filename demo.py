import gradio as gr
from langchain import PromptTemplate, LLMChain
from langchain.llms import GPT4All
#from langchain.callbacks.base import Callbacks
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Need to determine the right number of threads so we run fast, but don't starve the OS
import multiprocessing
use_threads = multiprocessing.cpu_count() - 4

local_path='/work/ggjt-model.bin'

template = """Question: {question}
Answer: I've thought about that, """

prompt = PromptTemplate(template=template, input_variables=["question"])
callbacks = [StreamingStdOutCallbackHandler()]
llm = GPT4All(model=local_path, callbacks=callbacks, verbose=True, n_threads=use_threads)

def sample(question):
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    return  llm_chain.run(question)

#llm_chain = LLMChain(prompt=prompt, llm=llm)

demo = gr.Interface(fn=sample, inputs="text", outputs="text", flagging_dir="/tmp/flagging")

demo.launch(share=True, server_port=7860, server_name="0.0.0.0")
