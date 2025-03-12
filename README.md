# Audio Downloader

A self-hosted web application for downloading songs, albums, or playlists from Spotify and YouTube as MP3 files. The application provides a web interface for users to input links, which are then downloaded as audio files using `spotdl` (for Spotify) or `yt-dlp` (for YouTube).

This is a fork, please read carefully the modifications

----

## 👮🏼 CAREFUL Security issues (thbo)

As for my mommy issues, I also have security issues. If you plan on using this version, it is made without the login. Be sure to use this only in local environnement.

## 👩🏼‍💻 API Usage (thbo)

This API is basic, I just removed the need of the cookie, so you can just fetch the url
`http://yourip:5005/download?spotify_link={thelink}`
and the download will start. Easier to prevent cookie expiration, without cookies. 🤡

## 🛜 Web (thbo)

The web panel doesn't need any login. So be careful when opening public access.

## 🗃️ Download Folder (thbo)

As asked for a friend, I removed the folders, it just downloads the file like this: `{Artist} - {Title}.mp3`

---

# Original repo informations

## Features

- **Download Spotify and YouTube playlists**: Automatically detects and processes playlists based on the URL.
- **Session-based download directories**: Isolates each user session to a unique download directory.
- **Admin Mode**: Enables admin users to download directly to a specified folder on the server.
- **Progress bar and download logs**: View download progress and logs in real-time via the web interface.
- **Auto-cleanup**: Deletes temporary session download folders after a specified time.
- **Organized Downloads**: Downloads are structured by artist and album folders, maintaining organization across downloads.
<!--- **Admin mode**: Allows the admin to specify a custom directory for downloads.
-->
## Prerequisites

- **Docker** and **Docker Compose** installed on your system.

## Installation

**Run with Docker Compose**:
   Use the provided `docker-compose.yaml` configuration to start the container.
```yaml
services:
  playlistdl:
    image: tanner23456/playlistdl:v2
    container_name: playlistdl
    ports:
      - "4827:5000"
    environment:
      #Direct Server Download
      - ADMIN_USERNAME= #Insert unique username here!
      - ADMIN_PASSWORD= #Insert unique password here!

      - AUDIO_DOWNLOAD_PATH=${AUDIO_DOWNLOAD_PATH}  # Use the env variable
      - CLEANUP_INTERVAL=300  # Optional
    volumes:
      - ${AUDIO_DOWNLOAD_PATH}:${AUDIO_DOWNLOAD_PATH}  # Reference env variable here as well


```

## Usage

1. **Access the Web Interface**:
   Open a browser and navigate to `http://localhost:5000` (replace `localhost` with your server IP if remote).

2. **Download a Playlist**:
   - Enter a Spotify or YouTube playlist URL.
   - Click **Download** to start the process.
   - Monitor download progress and logs via the interface.
3. **Admin Mode**:
   - Click the **Admin** button to log in with your credentials.
   - Once logged in, a message will appear in red indicating, "Now downloading directly to your server!"
   - Enter the playlist or album link as usual, and files will be saved to the designated admin folder on your server.
<!--
3. **Admin Mode**:
   - Click the **Admin** button to log in with your credentials.
   - Once logged in, specify a custom folder name where the files will be downloaded.
-->
## Configuration

### Environment Variables

- `CLEANUP_INTERVAL`: (Optional) Sets the cleanup interval for session-based download folders. Defaults to `300` seconds (5 minutes) if not specified.
- `ADMIN_USERNAME` and `ADMIN_PASSWORD`:(Optional) Sets the login credentials for admin access.
- `AUDIO_DOWNLOAD_PATH`: Sets the folder for admin-mode downloads. Files downloaded as an admin are stored here. This is set in your .env file.

## Technical Overview

- **Backend**: Flask application that handles download requests and manages session-based directories.
- **Frontend**: Simple HTML/JavaScript interface for input, progress display, and log viewing.
- **Tools**:
  - `spotdl` for downloading Spotify playlists.
  - `yt-dlp` for downloading YouTube playlists as MP3s.

## Notes

- This application is intended for personal use. Make sure to follow copyright laws and only download media you’re authorized to use.
- Ensure that the `downloads` directory has appropriate permissions if running on a remote server.

## Troubleshooting

- **Permissions**: Ensure the `downloads` directory has the correct permissions for Docker to write files.
- **Port Conflicts**: If port 5000 is in use, adjust the port mapping in the `docker-compose.yaml` file.

## Support This Project

If you like this project, consider supporting it with a donation!

[![Donate via Stripe](https://img.shields.io/badge/Donate-Stripe-blue?style=flat&logo=stripe)](https://buy.stripe.com/6oEdU3dWS19C556dQQ)

