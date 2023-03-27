ARG IMAGE

FROM ${IMAGE}

LABEL maintainer="Brad Larson"

#USER root
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update -y && apt-get install -y --no-install-recommends \
    wget \
    git \
    python3-pip \
    libsecret-tools \
    mupdf-tools \
    poppler-utils 

#RUN useradd -D user
#USER user
#WORKDIR /home/user

COPY requirements.txt .
RUN --mount=type=cache,target=/var/cache/apt \
    pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

RUN echo 'alias py=python3' >> ~/.bashrc

WORKDIR /app
ENV LANG C.UTF-8
# ENV PYTHONUNBUFFERED=1 smooths the logfile updates in Kubernetes
ENV PYTHONUNBUFFERED=1 

# ports
# 80
# 443
# 3000: debugger
# 5000: flask
# 6006-6009: tensorboard
# 8080: vscode server
# 8888: jupyter 
EXPOSE 80 443 3000 5000 8888

COPY server server
COPY public public

COPY config config
COPY common common
COPY cert.pem cert.pem
COPY privkey.pem privkey.pem

# Launch server
CMD ["python3","-u", "server/server.py"]
#CMD ["/usr/sbin/sshd", "-D"]