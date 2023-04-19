# National New Releases Playlist
This smalls script finds the newest releases of a nation by scraping [Every Noise at Once](https://everynoise.com/new_releases_by_genre) and putting into a specified Spotify playlist using the Spotify Web API.

## Setup
* Install the Python Spotify Web API wrapper [Spotipy](https://github.com/spotipy-dev/spotipy), YAML and the lxml package.
* Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and add a new app with an arbitrary name, description and redirict URI.
* Copy `config.yaml.default` to `config.yaml` and edit it.
* Insert the client ID of the app and secret. Insert the playlist ID and country of interest. (You can find ID using the Web API)
* Set the redirict URI to **exactly** the same which you set in the dashboard.
* Run `new-releases-playlist.py`

## Some information
### Why Every Noie at Once?
I scrape Every Noise at Once, since the new releases in Spotify does not differentiate between music released in a country and country *available* in a country.
The new_releases endpoint of the API therefore provides popular albums from around the world, which was ideal 
as the purpose of this script is making a playlist of obscure music from my country.

### Why does the playlist not always get cleared?
The Spotify Web API has trouble getting the correct URI of some tracks, especially those who has an alternative (or bonus) version.
This makes for some inconsistencies when clearing the playlist, as the script retrieves the URI of every track within and deletes it with the remove_items endpoint.

### Why *National* New Releases?
Try searching *country new releases* on google. Country music has ruined every search query for solutions to the problem of discovering completely new releases from a country.