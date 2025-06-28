# Docker Setup
Various ways
One way is manually create a .devcontainer folder and devcontainer.json and Dockerfile in it. For content, search Google or ask AI.

Download "Containers" extension for VSCode, then go to VSCode Command Prompt (or Ctrl + Shift + P) and search for something like "Dev Container: Build...", then select the folder that contains .devcontainer.

# GitHub Setup
Use .gitignore to ignore environment file (if you use), large files such as images, etc.

# OCR Setup
Typically includes those steps:
1.  Go to a host website.
2.  Signup an account.
3.  Generate a API key (keep the key private, never share or commit in Git).
4.  If you are not familiar with their API, find their cookbook for an example API call.
5.  Select a model.
6.  Check their limit on API calls and prices.
