#!/usr/bin/env python

import re
import json
import asyncio
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union # Added Union

# Make sure to install the required libraries:
# pip install google-fastmcp youtube-transcript-api httpx
from mcp.server.fastmcp import FastMCP
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from youtube_transcript_api._transcripts import Transcript # Import Transcript for type hinting

# Initialize FastMCP server
# Using the name and version from the original Node.js code
mcp = FastMCP("yttranscrpter", version="0.1.0")

class McpToolError(Exception):
    """Custom exception to mimic McpError structure if needed, though FastMCP might handle standard exceptions."""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)

def extract_youtube_id(url_or_id: str) -> str:
    """
    Extracts YouTube video ID from various URL formats or direct ID input.
    Raises ValueError if the input is invalid.
    """
    if not url_or_id:
        raise ValueError('YouTube URL or ID is required')

    # Try parsing as a URL
    try:
        parsed_url = urlparse(url_or_id)
        hostname = parsed_url.hostname

        if hostname:
            # Standard youtube.com URLs (www, no subdomain, music)
            if 'youtube.com' in hostname:
                if parsed_url.path == '/watch':
                    query_params = parse_qs(parsed_url.query)
                    if 'v' in query_params and query_params['v']:
                        video_id = query_params['v'][0]
                        if re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                            return video_id
                elif parsed_url.path.startswith('/embed/'):
                    video_id = parsed_url.path.split('/')[2]
                    if re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                         return video_id
                elif parsed_url.path.startswith('/shorts/'):
                    video_id = parsed_url.path.split('/')[2]
                    if re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                         return video_id
            # Short youtu.be URLs
            elif hostname == 'youtu.be':
                video_id = parsed_url.path[1:] # Remove leading '/'
                if re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                    return video_id
            # youtube-nocookie.com URLs
            elif 'youtube-nocookie.com' in hostname:
                 if parsed_url.path.startswith('/embed/'):
                    video_id = parsed_url.path.split('/')[2]
                    if re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                         return video_id

    except Exception:
        # If URL parsing fails, it might be a direct ID or invalid string
        pass

    # Check if the input itself is a valid 11-character ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id

    # If none of the above worked
    raise ValueError(f'Invalid or unsupported YouTube URL/ID format: {url_or_id}')


def format_transcript(transcript_list: List[Any]) -> str: # Changed hint slightly as it's objects now
    """Formats transcript lines (list of FetchedTranscriptSnippet objects)
       into a single space-separated string."""
    # Access the 'text' attribute using dot notation (line.text)
    return ' '.join(
        line.text.strip() for line in transcript_list if line.text and line.text.strip()
    )

@mcp.tool()
async def get_transcript(url: str, lang: str = "auto") -> str:
    """
    Extract transcript from a YouTube video URL or ID.
    Prioritizes manually created transcripts over auto-generated ones.

    Args:
        url: YouTube video URL or ID.
        lang: Language code for transcript (e.g., 'ko', 'en').
              Defaults to "auto", which tries to find the best available transcript,
              preferring manual ones.
    """
    print(f"Received request to get transcript for: url='{url}', lang='{lang}'")

    if not isinstance(url, str):
         raise ValueError('URL parameter is required and must be a string')
    if not isinstance(lang, str):
         raise ValueError('Language code must be a string')

    try:
        video_id = extract_youtube_id(url)
        print(f"Processing transcript for video: {video_id} (requested lang: {lang})")

        # --- Transcript Selection Logic ---
        target_transcript: Optional[Transcript] = None
        list_transcripts = await asyncio.to_thread(YouTubeTranscriptApi.list_transcripts, video_id)

        if lang != "auto":
            # User specified a language, try to find it exactly
            try:
                target_transcript = await asyncio.to_thread(list_transcripts.find_transcript, [lang])
                print(f"Found transcript specifically requested by user: {target_transcript.language} ({'manual' if not target_transcript.is_generated else 'generated'})")
            except NoTranscriptFound:
                print(f"Transcript for requested language '{lang}' not found.")
                # Proceed to auto-detection ONLY if the specific request failed?
                # Or should we fail here? Let's fail here to respect the user's specific request.
                raise NoTranscriptFound(f"Could not find transcript for the specifically requested language: '{lang}'")
        else:
            # Auto-detection: Prioritize manual, then generated
            manual_langs = [t.language_code for t in list_transcripts if not t.is_generated]
            generated_langs = [t.language_code for t in list_transcripts if t.is_generated]
            print(f"Available manual languages: {manual_langs}")
            print(f"Available generated languages: {generated_langs}")

            if manual_langs:
                try:
                    target_transcript = await asyncio.to_thread(list_transcripts.find_manually_created_transcript, manual_langs)
                    print(f"Found best manual transcript: {target_transcript.language}")
                except NoTranscriptFound:
                    print("No suitable manual transcript found.") # Should not happen if manual_langs is not empty, but good practice

            if target_transcript is None and generated_langs:
                try:
                    target_transcript = await asyncio.to_thread(list_transcripts.find_generated_transcript, generated_langs)
                    print(f"Found best generated transcript: {target_transcript.language}")
                except NoTranscriptFound:
                    print("No suitable generated transcript found.") # Should not happen if generated_langs is not empty

        # --- Fetch and Format ---
        if target_transcript is None:
             print(f"No suitable transcript found for video {video_id}.")
             raise NoTranscriptFound(f"No transcript found for video {video_id}" + (f" matching language '{lang}'" if lang != "auto" else " with auto-detection."))

        actual_lang = target_transcript.language_code
        print(f"Fetching transcript for language: {actual_lang}...")
        transcript_data = await asyncio.to_thread(target_transcript.fetch)

        # Format the transcript
        transcript_text = format_transcript(transcript_data)
        print(f"Successfully extracted transcript in '{actual_lang}' ({len(transcript_text)} chars)")

        return transcript_text

    except (NoTranscriptFound, TranscriptsDisabled) as e:
        # Catch errors specifically raised during the process or from the library directly
        error_message = str(e)
        print(f"Transcript processing failed: {error_message}")
        # Return the error message or raise an exception mapped by FastMCP
        return f"Transcript Error: {error_message}" # Return user-friendly message
        # raise McpToolError(code="TRANSCRIPT_ERROR", message=error_message) # Alternative: raise custom error

    except ValueError as e: # Catch errors from extract_youtube_id or type checks
        print(f"Invalid input error: {e}")
        raise # Re-raise ValueError, FastMCP should map it to InvalidParams

    except Exception as e:
        print(f"Failed to retrieve or process transcript for {url}: {e}")
        # Raise a generic exception, FastMCP should map it to InternalError
        raise Exception(f"An unexpected error occurred: {e}")

# async def test_function():
#     # This function is just for testing purposes
#     result = await get_transcript("https://www.youtube.com/watch?v=3_BXIQIdZ54")
#     print(result)
    

if __name__ == "__main__":
    # Initialize and run the server using stdio transport
    mcp.run(transport='stdio')
    # asyncio.run(test_function())