[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/goatwang-yttransciptermultilingualmcp-badge.png)](https://mseep.ai/app/goatwang-yttransciptermultilingualmcp)

# YTTranscipterMultilingualMCP
[![smithery badge](https://smithery.ai/badge/@GoatWang/yttransciptermultilingualmcp)](https://smithery.ai/server/@GoatWang/yttransciptermultilingualmcp)

## Description

This repository contains the code for YTTranscipterMultilingualMCP, a service for transcribing YouTube videos in multiple languages.

## Usage
Notice: command should come with `<full-path-of-uvx>` e.g. `/Library/Frameworks/Python.framework/Versions/3.10/bin/uvx`
```
{
  "mcpServers": {
    "yt-transcipter-multilingual": {
      "command": "/Library/Frameworks/Python.framework/Versions/3.10/bin/uvx", 
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

## Other Info

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
