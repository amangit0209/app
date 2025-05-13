# Use a slim Python base
FROM python:3.10-slim

# 1) Install OS deps: Chrome, ChromeDriver prerequisites, xvfb for headless
RUN apt-get update && \
    apt-get install -y \
      wget \
      unzip \
      xvfb \
      libxi6 \
      libgconf-2-4 && \
    rm -rf /var/lib/apt/lists/*

# 2) Install Chrome
RUN wget -qO /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && \
    apt-get install -y /tmp/chrome.deb && \
    rm /tmp/chrome.deb

# 3) ChromeDriver will be auto-installed by webdriver-manager at runtime,
#    so no need to install it here manually.

# 4) Create app directory
WORKDIR /app
COPY requirements.txt .

# 5) Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# 6) Copy your app code
COPY . .

# 7) Expose the port Streamlit uses
ENV PORT=8080
EXPOSE 8080

# 8) Run via xvfb to enable headless Chrome
CMD ["bash", "-lc", "xvfb-run -a streamlit run Qapp.py --server.port $PORT"]
