FROM python:3
WORKDIR /work
#COPY ggjt-model.bin /work/ggjt-model.bin
COPY startup.sh /work/startup.sh
RUN sh -c /work/startup.sh

# Python packages are HUGE!  Lets build in layers so we can reuse them on other builds
RUN python3 -m pip install --extra-index-url http://localhost:8080 --no-cache-dir pymupdf
RUN python3 -m pip install --extra-index-url http://localhost:8080 --no-cache-dir llama-cpp-python faiss-cpu 
RUN python3 -m pip install --extra-index-url http://localhost:8080 --no-cache-dir transformers sentence_transformers ctransformers 
RUN python3 -m pip install --no-cache-dir chromadb
# Old version
RUN python3 -m pip install --extra-index-url http://localhost:8080 --no-cache-dir pygpt4all==v1.0.1 langchain==v0.0.161 pyllamacpp gradio
# New Version
#RUN python3 -m pip install --no-cache-dir gpt4all==v0.2.3 langchain==v0.0.172 gradio

USER 2001

COPY demo.py /work/demo.py
COPY ingest.py /work/ingest.py
COPY env /work/.env
COPY documents.py /work/documents.py
COPY constants.py /work/constants.py

CMD python3 /work/documents.py
