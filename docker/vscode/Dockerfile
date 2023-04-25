FROM codercom/code-server:latest

USER root

# Install the extensions
# https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter
# https://marketplace.visualstudio.com/items?itemName=ms-toolsai.vscode-jupyter-powertoys
RUN code-server --install-extension ms-toolsai.jupyter --install-extension ms-toolsai.vscode-jupyter-powertoys

USER coder
