from strava import StravaUploader

if __name__ == "__main__":
    uploader = StravaUploader()
    result = uploader.upload("activity.gpx")
    print(result)
