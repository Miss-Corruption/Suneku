import json
import re
import socket
import ssl
from typing import Optional, List, Any, Tuple

import aiohttp
from loguru import logger

__all__ = ["Client"]


class Client:
    """
    A simple client for VNDB

    Parameters
    ----------
    username : string
        Username used to log in
    password : string
        Password used to log in
    client : string
        The client name. Must be between 3-50 characters and must only contain hyphens, underscores,
        spaces and alphanumeric ASCII characters. Defaults to ``username`` if not given
    client_version : string
        The version of the client software, can be any valid string.
        Defaults to 1.0
    session_token : string
        A token created when create_session is set to True. Can be used to log-in without a password.
        Defaults to an empty string
    create_session : bool
        Indicates if a "sessiontoken" should be created. The token can be used to log-in without a password.
        Must log in with a password to generate a session token.
        Defaults to False
    debug : bool
        Indicates if debug logs should be printed.
        Defaults to False
    """

    _session: Optional[aiohttp.ClientSession] = None,
    _client: Optional[str] = None

    def __init__(
            self,
            username: str,
            password: str,
            client: Optional[str] = None,
            client_version: Optional[str] = "1.0",
            session_token: Optional[str] = "",
            create_session: bool = False,
            debug: bool = False,
    ) -> None:

        self.logged_in = False
        self.client = username if client is None else client
        self.client_version = client_version
        self.username: str = username
        self.password: str = password
        self.session_token: str = session_token
        self.create_session: bool = create_session
        self.debug: bool = debug

        self._base_url = "api.vndb.org"
        self._port = 19535
        self._sslContext = aiohttp.client.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self._sslContext.verify_mode = ssl.CERT_REQUIRED
        self._sslContext.check_hostname = True
        self._sslContext.load_default_certs()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sslWrap = self._sslContext.wrap_socket(
            self._socket,
            server_hostname=self._base_url,
        )
        self.sslWrap.connect((self._base_url, self._port))

    def __repr__(self) -> str:
        return f"<{type(self).__name__} client={self.client}>"

    @property
    def session(self) -> aiohttp.ClientSession:
        """The current client session, created when needed"""
        if self._session is None:
            self._session = aiohttp.ClientSession()

        return self._session

    @property
    def client(self) -> Optional[str]:

        return self._client

    @client.setter
    def client(self, client: str) -> None:
        reg = re.compile("^.{3,50}[a-zA-Z0-9]+(?:[w -]*[a-zA-Z0-9]+)*$")
        if reg.match(client, re.IGNORECASE):
            print("Raise BadArg Error")
            # raise errors.InvalidClient({"id": "badarg"})

        self._client = str(client)

    async def login(
            self,
    ):
        login_vars = {
            'protocol': 1,
            'clientver': self.client_version,
            'client': self.client,
            'username': self.username,
            'password': self.password,
            'sessiontoken': self.session_token,
            'createsession': self.create_session
        }

        login_command = 'login' + json.dumps(login_vars) + '\x04'
        status, data = await self._send_request(query=login_command)
        if not status == "ok":
            print("Raise Login Error")
            # raise FailedLogin()
        self.logged_in = True

    async def close(self):
        self.sslWrap.close()

    async def get_vn(
            self,
            search: str,
            flags=None,
            page: int = 1,
            results: int = 10,
            sort_by: str = "id",
            reverse: bool = False,
            humanize: bool = False
    ) -> Tuple[Any, Any]:
        """
        Fetch data from the database searching for visual novels

        Parameters
        ----------
        search : string
            The name or the ID of the visual novel you want to search
        flags : set
            A comma separated set indicating what info to fetch.
            Available params: `basic`, `details`, `anime`, `relations`, `tags`, `stats`, `screens`, `staff`
            Defaults to `basic`.
        page : int
            Used for pagination. 1 would return page 1-10, 2 would return 11-20.
            The number of results can be changed with ``results``.
            Defaults to 1.
        results : int
            Maximum amount of results per page.
            Defaults to 10.
        sort_by : string
            Field to sort the results by.
            Defaults to ID.
        reverse : bool
            Set to true to reverse the order of results.
            Defaults to False.
        humanize : bool
            Indicates if the output should be humanized in a readable, more sorted format.
            If no database is present, or if it is outdated, a request will be made to download the database.
            Defaults to False.
        Returns
        -------
            None
        """

        if not self.logged_in:
            await self.login()

        if flags is None:
            flags = {"basic"}
        allowed_flags = {"basic", "details", "anime", "relations", "tags", "stats", "screens", "staff"}
        invalid_flags = flags.difference(allowed_flags)
        if invalid_flags:
            raise ValueError(
                f"Invalid Flag: {' '.join(invalid_flags)}\n"
                f"Only the following flags are available: {', '.join(allowed_flags)}"
            )

        fuzzy_or_strict = f'(id={search})' if search.isdigit() else f'(search~"{search}")'
        filters = {
            "page": page,
            "results": results,
            "sort": sort_by,
            "reverse": reverse
        }
        args = ' vn %s %s %s' % (
            ",".join(flags), fuzzy_or_strict, json.dumps(filters))
        search_command = 'get' + args + '\x04'
        data = await self._send_request(query=search_command)
        if humanize:
            print("humanize")
            # await human.hmn_vn(data)
        return data

    async def _send_request(self, query: str):
        self.sslWrap.sendall(query.encode('utf-8'))
        response, data = await self._recv_data()
        return response, data

    async def _recv_data(self):
        transmission = ""
        while '\x04' not in transmission:
            self._data_buffer = self.sslWrap.recv(buflen=1024)
            transmission += self._data_buffer.decode('utf-8', 'ignore')
        transmission = transmission[:-1]
        status, data = transmission.split(" ", 1) if " " in transmission else (transmission, None)
        if status == 'error':
            print("An error occurred")
            print(data)
            # raise errors.VNDBException(json.loads(data))
        if data:
            data = json.loads(data)
        return status, data
