A service to serve and manipulate a set of release build metadata for Path of Exile.

Required environment variables:

 * ``STATE_DIR``: directory for persistent database state;
 * ``MOLLYGUARD``: secret key needed for mutable updates from clients.

This FastAPI application is best run via something like hypercorn behind a nginx proxy.

Hypercorn config would be something like::

    bind = "[::1]:8000"
    root_path = "/poe-meta"
