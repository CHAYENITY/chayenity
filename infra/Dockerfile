FROM jenkins/jenkins:lts-jdk17
USER root

# Update system and install Docker
RUN apt-get update && \
    apt-get upgrade -y && \
    curl -fsSL https://get.docker.com | sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python 3.11 from source (most reliable method)
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        zlib1g-dev \
        libncurses5-dev \
        libgdbm-dev \
        libnss3-dev \
        libssl-dev \
        libreadline-dev \
        libffi-dev \
        libsqlite3-dev \
        libbz2-dev \
        liblzma-dev \
        wget \
        curl \
        unzip && \
    cd /tmp && \
    wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz && \
    tar -xf Python-3.11.9.tgz && \
    cd Python-3.11.9 && \
    ./configure \
        --enable-optimizations \
        --with-ensurepip=install \
        --enable-shared \
        LDFLAGS="-Wl,-rpath /usr/local/lib" && \
    make -j$(nproc) && \
    make altinstall && \
    cd / && \
    rm -rf /tmp/Python-3.11.9* && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create symlinks for python3.11
RUN ln -sf /usr/local/bin/python3.11 /usr/bin/python3.11 && \
    ln -sf /usr/local/bin/pip3.11 /usr/bin/pip3.11 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.11 1 && \
    python3.11 -m pip install --upgrade pip

# Install Poetry
RUN python3.11 -m pip install poetry

# --- Install SonarQube Scanner CLI ---
ENV SONAR_SCANNER_VERSION=5.0.1.3006
ENV SONAR_SCANNER_HOME=/opt/sonar-scanner

RUN cd /tmp && \
    curl -L --output sonar-scanner-cli.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${SONAR_SCANNER_VERSION}-linux.zip && \
    unzip sonar-scanner-cli.zip && \
    mv sonar-scanner-${SONAR_SCANNER_VERSION}-linux ${SONAR_SCANNER_HOME} && \
    rm sonar-scanner-cli.zip

RUN chown -R jenkins:jenkins ${SONAR_SCANNER_HOME}
ENV PATH=${SONAR_SCANNER_HOME}/bin:${PATH}
# --- End SonarQube Scanner CLI Installation ---

# Add jenkins user to the docker group
RUN usermod -aG docker jenkins
USER jenkins

# Verify Python installation
RUN python3.11 --version && pip3.11 --version && poetry --version