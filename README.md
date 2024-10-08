# SnippetDepot Backend

SnippetDepot is a real-time code snippet retrieval system that combines the principles of Google Instant Search, StackOverflow, and Wikipedia into one service. This repository contains the backend server code for the SnippetDepot project.

## Features

- RESTful API for snippet management
- Real-time snippet search and retrieval
- User authentication and session management
- SQLite database for storing snippets and user data
- Automatic backup system
- HTTPS support

## Files

- `server.py`: Main server file containing API endpoints and database operations
- `handleHTTP.py`: HTTP request handler
- `autoBackup.py`: Automatic backup script for the database
- `startServer.sh`: Script to start all server components
- `stopServer.sh`: Script to stop all server processes

## Setup

1. Ensure you have Python 3.x installed on your system.
2. Install the required dependencies:
   ```
   pip install aiohttp aiosqlite jinja2 cryptography
   ```
3. Set up SSL certificates for HTTPS:
   - Place your SSL certificate at `/etc/letsencrypt/live/snippetdepot.com/fullchain.pem`
   - Place your SSL key at `/etc/letsencrypt/live/snippetdepot.com/privkey.pem`

## Running the Server

To start the server, run:

```
bash startServer.sh
```

This will start the main server, HTTP handler, and the automatic backup script.

To stop the server, run:

```
bash stopServer.sh
```

## API Endpoints

- `/search/{lang}/{query}`: Search for snippets
- `/latest/`: Get the latest snippets
- `/getSnippet/{query}`: Retrieve a specific snippet
- `/addSnippet/`: Add a new snippet (POST)
- `/login/`: User login (POST)
- `/delete/`: Delete a snippet (POST, requires authentication)
- `/isAuth/`: Check authentication status
- `/getSnippetCount/`: Get the total number of snippets
- `/getSnippetsBetween/{a}/{b}`: Get a range of snippets

## Database

The server uses two SQLite databases:
- `data.db`: Stores code snippets
- `userdata.db`: Stores user information

## Security

- HTTPS is enabled by default
- Passwords are salted and hashed
- Session management uses encrypted cookies
- Rate limiting is implemented to prevent spam

## Automatic Backups

The `autoBackup.py` script creates backups of the `data.db` file every 6 hours, keeping a maximum of 40 backup files.

## Contributing

Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For more information, visit [snippetdepot.com](https://snippetdepot.com) or join our [subreddit](https://reddit.com/r/snippetdepot).
