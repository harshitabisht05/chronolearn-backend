# yt-study-planner

## Overview
The yt-study-planner is a FastAPI application designed to help users manage their study schedules by integrating YouTube playlists. It allows users to create, update, and track their study progress while leveraging the YouTube API to fetch relevant educational content.

## Project Structure
```
yt-study-planner/
├── app/
│   ├── __init__.py          # Initializes the app package
│   ├── main.py              # FastAPI entrypoint
│   ├── models.py            # Pydantic + DB models
│   ├── schemas.py           # Request/response models
│   ├── database.py          # DB config
│   ├── youtube_api.py       # YouTube playlist fetch logic
│   ├── calendar_logic.py    # Schedule distribution logic
│   ├── auth.py              # JWT auth
│   └── routes/
│       ├── users.py         # User login/signup
│       ├── playlists.py     # Playlist endpoints
│       └── calendar.py      # Calendar & progress endpoints
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/yt-study-planner.git
   cd yt-study-planner
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Start the FastAPI application:
   ```
   uvicorn app.main:app --reload
   ```

2. Access the API documentation at `http://127.0.0.1:8000/docs`.

## Features
- User authentication with JWT
- Fetch and manage YouTube playlists
- Create and manage study schedules
- Track study progress

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.