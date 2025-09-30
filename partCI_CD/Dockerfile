FROM jenkins/jenkins:lts-jdk17
USER root

# Update system and install Docker
RUN apt-get update && \
    apt-get upgrade -y && \
    curl -fsSL https://get.docker.com | sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python 3.11 and build tools (Python 3.11 should already be available in Jenkins LTS JDK17)
RUN apt-get update && \
    apt-get install -y \
        python3.11 \
        python3.11-pip \
        python3.11-venv \
        python3.11-dev \
        python3-pip \
        build-essential \
        curl \
        unzip \
        wget \
        ca-certificates \
        gnupg \
        lsb-release && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create symlinks to make python3.11 the default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    python3.11 -m pip install --upgrade pip

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

# (Optional) Set the default SONAR_SCANNER_HOME for the jenkins user
# ENV SONAR_SCANNER_HOME=/opt/sonar-scanner