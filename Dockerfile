FROM python:3.11

ENV SASS_VERSION 1.32.8

RUN curl -sL https://deb.nodesource.com/setup_20.x | bash -

RUN apt-get update && apt-get install -y \
                                            vim \
                                            make \
                                            rsync \
                                            curl \
                                            redis \
                                            nginx \
                                            nodejs \
                                            firefox-esr

RUN npm install

RUN cd /tmp && \
    curl \
        --silent \
        --location \
        --request GET \
        https://github.com/sass/dart-sass/releases/download/${SASS_VERSION}/dart-sass-${SASS_VERSION}-linux-x64.tar.gz \
        --output sass.tgz && \
        tar xzvf sass.tgz && \
        mv dart-sass/sass /usr/local/bin/

RUN pip install --upgrade pip

ENV PROJECT light-emitting-desk

COPY docker-config/bashrc /root/.bashrc

WORKDIR /opt/${PROJECT}

COPY ./ /opt/${PROJECT}
RUN make dev-install
