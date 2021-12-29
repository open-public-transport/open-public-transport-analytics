import glob
import os
from pathlib import Path

from google.cloud import storage
from tracking_decorator import TrackingDecorator


#
# Main
#

class GoogleCloudPlatformBucketUploader:

    @TrackingDecorator.track_time
    def upload_data(self, logger, data_path, city_id, project_id, bucket_name, quiet=False):
        """
        See https://cloud.google.com/storage/docs/creating-buckets#storage-create-bucket-python
        """

        # Set script path
        file_path = os.path.realpath(__file__)
        script_path = os.path.dirname(file_path)
        config_file_path = os.path.join(script_path, "open-public-transport-2e54e67b8c92.json")

        # Check for config file
        if not Path(config_file_path).exists():
            logger.log_line("✗️ Google Cloud config not found " + config_file_path)
            return

        # Define storage client
        client = storage.Client.from_service_account_json(
            config_file_path, project=project_id
        )

        bucket = client.bucket(bucket_name=bucket_name)
        bucket.storage_class = "STANDARD"

        for file_path in glob.iglob(data_path + "/geojson/*.geojson"):
            blob = bucket.blob(os.path.join(city_id, "geojson", os.path.basename(file_path)))
            blob.upload_from_filename(file_path)

            if not quiet:
                logger.log_line("✓️ Uploading " + os.path.basename(file_path))

        for file_path in glob.iglob(data_path + "/sample-points/*"):
            blob = bucket.blob(os.path.join(city_id, "sample-points", os.path.basename(file_path)))
            blob.upload_from_filename(file_path)

            if not quiet:
                logger.log_line("✓️ Uploading " + os.path.basename(file_path))

        for file_path in glob.iglob(data_path + "/styles/*.json"):
            blob = bucket.blob(os.path.join(city_id, "styles", os.path.basename(file_path)))
            blob.upload_from_filename(file_path)

            if not quiet:
                logger.log_line("✓️ Uploading " + os.path.basename(file_path))
