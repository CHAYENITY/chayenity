FROM jenkins/jenkins:lts-jdk17

USER root

# Install Docker CLI and dependencies
RUN apt-get update && \
    apt-get install -y curl gnupg lsb-release && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y docker-ce-cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python 3.11, venv, and pip
RUN apt-get update && \
    apt-get install -y python3.11 python3.11-venv python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Make python3.11 the default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Install Poetry
RUN python3 -m pip install --no-cache-dir --break-system-packages poetry

# Install SonarScanner CLI
ENV SONAR_SCANNER_VERSION=5.0.1.3006
ENV SONAR_SCANNER_HOME=/opt/sonar-scanner
RUN cd /tmp && \
    curl -L "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${SONAR_SCANNER_VERSION}-linux.zip" -o sonar-scanner-cli.zip && \
    unzip sonar-scanner-cli.zip && \
    mv sonar-scanner-${SONAR_SCANNER_VERSION}-linux ${SONAR_SCANNER_HOME} && \
    rm sonar-scanner-cli.zip && \
    chown -R jenkins:jenkins ${SONAR_SCANNER_HOME}
ENV PATH=${SONAR_SCANNER_HOME}/bin:${PATH}

# Create the docker group manually and add jenkins user to it
RUN groupadd -f docker && \
    usermod -aG docker jenkins

USER jenkins

# Verify installations
RUN python3 --version && \
    pip3 --version && \
    poetry --version && \
    sonar-scanner -v