# Boredom Chat

A chat program I'm making because I'm bored

# How to use

run `src/server.py` with python 3.8 or higher , this script opens a socket 
on localhost that listens to and forwards messages from clients

then run `src/client.py`. this scrip connects to the server and can be used to
send and receive messages 

# design 

this project is really just an eexcuse to mess around with layering different
protocols.

there are 2 layers placed on top of the socket protocol used in python (which 
is TCP/IP I think?). 

1. the "packet" layer, which divides long messages into smaller chunks
2. the  message later, which encodes the actual program logic

## The "I need a better name for it layer"
I added the first layer because there isn't a way to ask a socket if there is 
more data available, short of closing and reopening it when you're done[^idea].

[^idea]: I should try that though, maybe it won't be so bad?
