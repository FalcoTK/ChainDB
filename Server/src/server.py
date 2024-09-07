import datetime
from datetime import datetime, timedelta
import aiohttp
from aiohttp import http, web
from collections import defaultdict
import json
import hmac
import hashlib
import time
from aiohttp_middlewares import https_middleware
from erorr.erorr import (
    ServerSide,
    ConnectionError,
    AuthenticationError,
    ValidationError,
    JsonError,
    TimeoutError,
)


class helper:
    """
    The `helper` class provides an asynchronous method for returning HTTP responses
    in various formats and for different HTTP methods such as GET, POST, and DELETE.

    Methods:
        - ReturnBack: Prepares a response for the given request method, status, and format.

    Usage:
    ------
    Use the `ReturnBack` method to handle different types of HTTP responses by specifying
    whether the response should be in JSON format, the HTTP method, and a custom message.
    """

    async def ReturnBack(
        self,
        Message: dict = None,
        status: int = 200,
        isjson: bool = True,
        method: str = "GET",
    ):
        """
        ReturnBack Method
        -----------------
        Generates an appropriate HTTP response based on the method type, status code,
        and content format.

        Parameters:
        -----------
        - Message (dict): The content to return in the response, typically a dictionary for JSON responses.
        - status (int): The HTTP status code to return. Default is 200 (OK).
        - isjson (bool): Determines whether the response should be in JSON format. Default is True.
        - method (str): The HTTP method to handle. Supports "GET", "POST", and "DELETE". Default is "GET".

        Returns:
        --------
        - `web.json_response`: If `isjson` is True and the method is "GET", returns the response in JSON format.
        - `web.Response`: If `isjson` is False or another method (POST/DELETE) is specified, returns a plain text response.

        Notes:
        ------
        - The method currently supports "GET" requests with fully implemented functionality.
        - Placeholder sections for "POST" and "DELETE" allow for future expansion.

        Examples:
        ---------
        1. Handling a JSON response for a GET request:

        ```python
        response = await helper().ReturnBack(Message={"message": "Hello, world!"}, status=200, isjson=True)
        ```

        2. Returning plain text response:

        ```python
        response = await helper().ReturnBack(Message="Simple Text", status=200, isjson=False)
        ```

        3. Future use of POST/DELETE methods:
        The method includes handling for other methods like "POST" and "DELETE" but isn't fully implemented yet.
        """
        if method == "GET":
            if isjson:
                PayloadBack = {"status": status, "Response": Message}
                return web.json_response(data=PayloadBack, status=status)
            return web.Response(text=Message, status=status)
        if method == "POST":
            pass
        if method == "DELETE":
            pass


class RequestHandler:
    """Recive Request Handler"""

    # make recive json then process it in other files python
    async def Recive(self, request):
        try:
            data = await request.json()
            return web.json_response(data={"status": 200}, status=200)
        except Exception as err:

            raise JsonError("Erorr From JSON, maybe wrong payload?")


class protection:
    """
    The `protection` class provides security mechanisms for a web server, including rate limiting
    and token-based authentication. This helps protect the server from excessive requests (DDoS protection)
    and ensures secure API access using HMAC-based tokens.

    Methods:
    --------
    - RateLimiter: Middleware that limits the number of requests from a single IP address to prevent abuse.
    - TokenHandler: Generates a time-based HMAC token to ensure secure communication.
    - TokenValidator: Validates the token from the client to ensure it is valid and not expired.

    Usage:
    ------
    Use the `RateLimiter` method as a middleware to prevent request spamming, and the `TokenHandler`
    and `TokenValidator` methods for secure API authentication based on a rotating HMAC token.
    """

    @web.middleware
    async def RateLimiter(self, request, handler):
        """
        RateLimiter Method
        ------------------
        A middleware function to implement rate limiting based on the client's IP address.
        Limits the number of requests an IP can make within a given time frame (10 seconds) to 20 requests.

        Parameters:
        -----------
        - request: The incoming request object.
        - handler: The next handler in the middleware chain.

        Returns:
        --------
        - `web.Response`: If the client exceeds the request limit, returns a 429 response indicating
          "Too Many Requests".
        - Calls the next middleware/handler if the limit is not exceeded.

        Notes:
        ------
        - The limit is set to 20 requests per 10 seconds for each client IP address.
        - All requests from an IP are tracked in a dictionary and filtered by the last 10-second window.
        - Can be adjusted to throttle different endpoints or impose stricter limits as needed.

        Example:
        --------
        ```python
        app = web.Application(middlewares=[protection().RateLimiter])
        ```
        """

        CleintIP = request.remote
        CountingReq = defaultdict(list)
        current_time = datetime.now()
        print("Accessed by:", CleintIP)

        # Keep requests only from the last 10 seconds
        CountingReq[CleintIP] = [
            t for t in CountingReq[CleintIP] if t > current_time - timedelta(seconds=10)
        ]

        request_count = len(CountingReq[CleintIP])

        # If the request limit is exceeded
        if request_count >= 20:
            return web.Response(
                text="Your IP has been blocked due to too many requests.",
                status=429,
            )

        CountingReq[CleintIP].append(current_time)
        return await handler(request)

    async def TokenHandler(key: str):
        """
        TokenHandler Method
        -------------------
        Generates a secure time-based HMAC (Hash-based Message Authentication Code) token using
        the given `key`. The token changes every 10 seconds to ensure short-term validity.

        Parameters:
        -----------
        - key (str): The secret key used to generate the token.

        Returns:
        --------
        - str: A secure HMAC token generated using the current time divided by 10 (rotating every 10 seconds).

        Example:
        --------
        ```python
        token = await protection().TokenHandler("my_secret_key")
        ```
        """
        timenow = int(time.time() // 10)
        return hmac.new(
            key.encode(), str(timenow).encode(), hashlib.sha256()
        ).hexdigest()

    async def TokenValidator(key: str, ClientToken: str):
        """
        TokenValidator Method
        ---------------------
        Validates the token provided by the client. The token is considered valid if it matches the
        current token or the previous token, providing a small time window for token validation.

        Parameters:
        -----------
        - key (str): The secret key used to generate the HMAC tokens.
        - ClientToken (str): The token provided by the client that needs validation.

        Returns:
        --------
        - bool: `True` if the client token is valid (matches the current or previous token), `False` otherwise.

        Example:
        --------
        ```python
        is_valid = await protection().TokenValidator("my_secret_key", "client_token")
        if is_valid:
            print("Token is valid!")
        else:
            print("Token is invalid!")
        ```

        Notes:
        ------
        - The validation checks both the current token and the previous one to account for slight delays.
        - This ensures token security while allowing minor time discrepancies between client and server.
        """
        timenow = int(time.time() // 10)
        PalidToken = hmac.new(
            key.encode(), str(timenow).encode(), hashlib.sha256()
        ).hexdigest()
        PerviousToken = hmac.new(
            key.encode(), str(timenow - 1).encode(), hashlib.sha256()
        ).hexdigest()
        return ClientToken == PalidToken or ClientToken == PerviousToken
