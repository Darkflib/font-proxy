from flask import Flask, request, Response
import requests
from cachelib import FileSystemCache
import logging
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
# Configure FileSystemCache with a directory for storing cache files
cache = FileSystemCache(cache_dir='./cache', default_timeout=5 * 60)

GOOGLE_FONTS_BASE_URL = "https://fonts.googleapis.com"
GOOGLE_FONTS_STATIC_BASE_URL = "https://fonts.gstatic.com"

def is_safe_url(base_url, target_url):
    """Ensure the target URL is within the allowed base URL."""
    base = urlparse(base_url)
    target = urlparse(target_url)
    return base.netloc == target.netloc and target.path.startswith(base.path)

@app.before_request
def log_request_info():
    logging.info(f"Request: {request.method} {request.url}")

@app.route('/<path:font_path>', methods=['GET'])
def proxy_fonts(font_path):
    # Log the request and args for debugging
    logging.info(f"Received request for font path: {font_path}")
    logging.info(f"Request args: {request.args}")

    ourhost = request.host # Get the host from the request to use in the proxied css file

    # is it a font request or a CSS2 API request?
    reqtype = None
    # Is it a request for the CSS2 API?
    if font_path.startswith('css2'):
        reqtype = 'css2'
        logging.info("Request for CSS2 API")
        # Handle the CSS2 API request
        # Check for the presence of the 'family' parameter in the request
        if 'family' not in request.args:
            return Response("Missing 'family' parameter", status=400)

        # Validate the font path
        if not font_path.startswith('css2'):
            logging.warning(f"Invalid font css path: {font_path}")
            return Response("Invalid font path", status=400)
    else:
        reqtype = 'static'
        logging.info("Request for static font file")
        # Handle the static font file request
        # Validate the font path
        if not font_path.endswith('.ttf') and not font_path.endswith('.woff2') and not font_path.endswith('.woff') and not font_path.endswith('.eot') and not font_path.endswith('.otf'):
            logging.warning(f"Invalid font file path: {font_path}")
            return Response("Invalid font path", status=400)

    if reqtype == None:
        logging.warning(f"Invalid request type: {reqtype}")
        return Response("Invalid request type", status=400) # We should never reach here, but just in case

    # Determine the base URL
    base_url = GOOGLE_FONTS_BASE_URL if reqtype == 'css2' else GOOGLE_FONTS_STATIC_BASE_URL
    url = urljoin(base_url, font_path)

    # Append query parameters to the URL
    query_string = request.query_string.decode('utf-8')
    if query_string:
        url = f"{url}?{query_string}"

    # Ensure the URL is safe
    if not is_safe_url(base_url, url):
        logging.warning(f"Unsafe URL detected: {url}")
        return Response("Unsafe URL", status=400)

    # Check the cache
    cached_response = cache.get(url)
    if cached_response:
        logging.info(f"Cache hit for URL: {url}")
        content, content_type = cached_response
        return Response(content, content_type=content_type)

    # Fetch the resource
    logging.info(f"Cache miss for URL: {url}")
    headers = {key: value for key, value in request.headers.items() if key.lower() != 'host'}
    # Override the User-Agent header to avoid blocking by Google Fonts
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) WWFF Font Proxy/1.0 (github.com/darkflib/wwff-font-proxy)'
    response = requests.get(url, headers=headers)

    # Cache the response if successful
    if response.status_code == 200:
        # Replace the URL in the response with the proxied URL if it is a CSS2 API request
        if reqtype == 'css2':
            css_content = response.text  # Use response.text to get the content as a string
            css_content = css_content.replace(GOOGLE_FONTS_BASE_URL, f"https://{ourhost}")
            css_content = css_content.replace(GOOGLE_FONTS_STATIC_BASE_URL, f"https://{ourhost}")
            response_content = css_content.encode('utf-8')  # Encode back to bytes for caching
        else:
            response_content = response.content  # Use the original content for static font files

        logging.info(f"Caching response for URL: {url}")
        cache.set(url, (response_content, response.headers.get('Content-Type')), timeout=24 * 60 * 60)  # Cache for 5 hours

        # Return the response with the correct content type, and expiration headers
        response_headers = {
            'Cache-Control': 'public, max-age=86400',  # Cache for 24 hours
            'Expires': response.headers.get('Expires'),
            'Content-Type': response.headers.get('Content-Type')
        }
        return Response(response_content, status=response.status_code, content_type=response.headers.get('Content-Type'), headers=response_headers)

    return Response(response.content, status=response.status_code, content_type=response.headers.get('Content-Type'))

if __name__ == '__main__':
    # Run the Flask app in debug mode with SSL enabled
    # Note: You need to have a valid SSL certificate and key for this to work
    # For testing purposes, you can generate a self-signed certificate using OpenSSL
    # openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))

