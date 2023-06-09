# llmqa
A local QA LLM for asking questions over documents

Currently the LLM uses ctranformers to utilize the MPT local models.  Take your pick and replace the env variable.
Utilizes Gradio to provide a web interface
Designed for deployment into K8s

# Dockerbuild
The container is built assuming no volumes, so large datastores have to be brought in at build time.  This includes the models and the embeddings database.
If you have access to volumes, it is a much better way to do this.

# Ingesting
Building a new vectorstore to help with the prompts is important.
The ingest script is used for this, load the container with a volume mounted to /sources and the vectorstore in /db.  /sources should be the collection of files you want to ingest.
Once the script is finished, exit and tar up the local db directory.  This will get installed with the build later.
