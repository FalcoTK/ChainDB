import json
import hmac
import hashlib
import time
from datetime import datetime, timedelta
from collections import defaultdict
import logging

import aiohttp
from aiohttp import web, http
from aiohttp_middlewares import https_middleware

from erorr.erorr import (
    ServerSide,
    ConnectionError,
    AuthenticationError,
    ValidationError,
    JsonError,
    TimeoutError,
)


ReqCounter = defaultdict(list)
with open("config.json", "rb") as Cfg:
    Config = json.load(Cfg)


class Helper:
    """
    The `Helper` class provides an asynchronous method for returning HTTP responses
    in various formats and for handling different HTTP methods such as GET, POST,
    and DELETE. It also includes basic logging functionality to log information and errors.

    Attributes:
    ------------
    - config: Holds configuration settings (assumed from external `Config` class).
    - logger: A logger instance used to log informational messages and errors.

    Methods:
    ---------
    - ReturnBack: Prepares and returns an HTTP response based on the provided status, message,
                  and format (JSON or plain text).
    - LoggingErorr: Logs messages based on the provided log level (info or error).

    Usage:
    ------
    Use the `ReturnBack` method to handle different types of HTTP responses. You can specify
    the response format (JSON or text), the status code, and the HTTP method. The `LoggingErorr`
    method allows you to log custom messages at either the info or error level.

    Example:
    --------
    1. Returning a JSON response for a GET request:

    ```python
    response = await helper().ReturnBack(
        Message={"message": "Hello, world!"},
        status=200,
        isjson=True
    )
    ```

    2. Returning a plain text response:

    ```python
    response = await helper().ReturnBack(
        Message="Simple Text",
        status=200,
        isjson=False
    )
    ```

    3. Logging an error message:

    ``await helper().LoggingErorr(message="This is an error", status="error")``

    """

    def __init__(self):
        self.config = Config
        self.LogActivity = self.config["Config"]["ServerConfig"]["LogActivity"]
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Setting up console logging
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    async def LoggingErorr(self, message: str, status: str = "info"):
        """
        LoggingErorr Method
        -------------------
        Logs messages to the console based on the specified log level.

        Parameters:
        -----------
        - message (str): The message to log.
        - status (str): The log level. Either 'info' for informational messages or 'error'
                        for error messages. Default is 'info'.

        Returns:
        --------
        None

        Example Usage:
        --------------
        1. Logging an informational message:

        ```python
        await helper().LoggingErorr(message="This is an info message")
        ```

        2. Logging an error message:

        ```python
        await helper().LoggingErorr(message="This is an error", status="error")
        ```

        Notes:
        ------
        - By default, the logger is set to log at the INFO level. Error messages will still be
          logged even if the default level is INFO.
        """
        if status.lower() == "error":
            self.logger.error(message)
        else:
            self.logger.info(message)

    async def ReturnBack(
        self, Message: dict = None, status: int = 200, isjson: bool = True
    ):
        """
        ReturnBack Method
        -----------------
        Generates an appropriate HTTP response based on the provided message, status code,
        and content format (JSON or plain text).

        Parameters:
        -----------
        - Message (dict or str): The content to return in the response. Typically a dictionary
                                 for JSON responses, or a string for plain text responses.
        - status (int): The HTTP status code to return. Default is 200 (OK).
        - isjson (bool): Determines whether the response should be in JSON format. Default is True.

        Returns:
        --------
        - `web.json_response`: If `isjson` is True, returns the response in JSON format.
        - `web.Response`: If `isjson` is False, returns a plain text response.

        Notes:
        ------
        - The method primarily supports "GET" requests for now. Future implementations
          may expand this functionality to support other HTTP methods such as POST and DELETE.

        Example Usage:
        --------------
        1. Handling a JSON response for a GET request:

        ```python
        response = await helper().ReturnBack(
            Message={"message": "Hello, world!"},
            status=200,
            isjson=True
        )
        ```

        2. Returning a plain text response:

        ```python
        response = await helper().ReturnBack(
            Message="Simple Text",
            status=200,
            isjson=False
        )
        ```

        Raises:
        -------
        - Catches `ServerSide` exceptions, logs the error, and returns a generic 500 error response
          if a server-side issue occurs.
        """
        try:
            if isjson:
                # Log the status and return a JSON response
                self.logger.info("Sending JSON response")
                return web.json_response(
                    data={"status": status, "Response": Message}, status=status
                )
            else:
                # Return a plain text response
                if self.LogActivity:
                    self.logger.info("Sending plain text response")
                return web.Response(text=Message, status=status)

        except ServerSide as e:
            # Log the error and return a generic server error response
            if self.LogActivity:
                self.logger.error(f"Failed to send response: {str(e)}")
            return web.Response(text="Server-side error occurred", status=500)


class RequestHandler:
    """Recive Request Handler"""

    def __init__(self):
        self.config = Config
        self.LogActivity = self.config["Config"]["ServerConfig"]["LogActivity"]

    # make recive json then process it in other files python
    async def Recive(self, request):
        try:
            data = await request.json()
            return await Helper().ReturnBack(
                Message={"data": data}, status=200, isjson=True
            )
        except Exception as err:
            return await Helper().ReturnBack(
                Message="did you add the payload?",
                status=400,
                isjson=True,
                method="GET",
            )
            return

    async def PingPong(self, request):
        return await Helper().ReturnBack(Message="Pong", status=200, isjson=True)


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

    def __init__(self):
        self.config = Config
        self.LogActivity = self.config["Config"]["ServerConfig"]["LogActivity"]

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

        IpAddr = request.remote
        TimeNow = datetime.now()

        if self.config["Config"]["ServerConfig"]["WhitelistIP"]["UseWhitelist"]:
            if (
                IpAddr
                not in self.config["Config"]["ServerConfig"]["WhitelistIP"][
                    "IpAllowLst"
                ]
            ):
                return await Helper().ReturnBack(
                    Message="who are you?, i dont see in the whitelist",
                    status=400,
                    isjson=False,
                )

        # Remove entries older than 20 seconds
        ReqCounter[IpAddr] = [
            t for t in ReqCounter[IpAddr] if t > TimeNow - timedelta(seconds=20)
        ]

        request_count = len(ReqCounter[IpAddr])

        if request_count >= 20:
            return web.Response(
                text="Your IP has been blocked due to too many requests.",
                status=429,
            )

        # Add current request timestamp
        ReqCounter[IpAddr].append(TimeNow)

        # Process the request
        return await handler(request)

    async def TokenHandler(self, key: str):
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

    async def TokenValidator(self, key: str, ClientToken: str):
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
        timenow = int(time.time() // self.config["Config"]["TokenConfig"]["duration"])
        PalidToken = hmac.new(
            key.encode(), str(timenow).encode(), hashlib.sha256()
        ).hexdigest()
        PerviousToken = hmac.new(
            key.encode(), str(timenow - 1).encode(), hashlib.sha256()
        ).hexdigest()
        return ClientToken == PalidToken or ClientToken == PerviousToken
