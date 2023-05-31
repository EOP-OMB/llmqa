apt update

# Needed for me/dev
apt install -y vim

#Create my linux user, so I can use mounted volumes nicely, also dockerfile has UID in it.
useradd --uid 2001 llm
chown -R 2001 /work
chown -R 2001 /db
chown -R 2001 /models

# dev bashrc
echo "# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval \"$(dircolors -b ~/.dircolors)\" || eval \"$(dircolors -b)\"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# colored GCC warnings and errors
#export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

# some more ls aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
" > /root/.bashrc

# All this was moved to dockerfile

# Needed for python gpt
#build requirements file
#echo "pygpt4all==v1.0.1
#langchain
#pyllamacpp
#gradio
#pymupdf
#" > /work/requirements.txt

#pip3 install --no-cache-dir -r /work/requirements.txt
