# YTTranscipterMultilingualMCP
[![smithery badge](https://smithery.ai/badge/@GoatWang/yttransciptermultilingualmcp)](https://smithery.ai/server/@GoatWang/yttransciptermultilingualmcp)

## Description

This repository contains the code for YTTranscipterMultilingualMCP, a service for transcribing YouTube videos in multiple languages.

## Usage
```
{
  "mcpServers": {
    "yt-transcipter-multilingual": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/GoatWang/YTTranscipterMultilingualMCP",
        "yt-transcipter-multilingual"
      ]
    }    
  }
}
```

## Prerequisites

* Python 3.10+
* Docker

## Getting Started

1. Clone the repository:

   ```bash
   git clone https://github.com/GoatWang/YTTranscipterMultilingualMCP
   ```

2. Build the Docker image:

   ```bash
   docker build -t yt-transcipter-multilingual .
   ```

3. Run the Docker container:

   ```bash
   docker run -d -p 5000:5000 yt-transcipter-multilingual
   ```
