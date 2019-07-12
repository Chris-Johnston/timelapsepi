# timelapse pi

A service for capturing timelapse photos on a raspberry pi.

## `config.yaml`

```yaml
# capture every 5 minutes
interval: 300

# capture from the webcam
capture_method: webcam
# into the images dir relative to working dir
capture_directory: images

# upload the file and delete it, if all steps pass
# if one step fails, actions will be repeated
post_capture_methods:
  - azure_upload
  - remove

# azure blob container settings
azure_upload:
  account_name: <name>
  account_key: <account_key>
  blob_container: <container>
  timeout: 1

# image settings
pi_camera:
  x: 1920
  y: 1080
  iso: 200
  delay: 5 # wait 5 seconds before capturing after setting iso, allows for auto adjustment

# log settings
logs: timelapse.log
log_level: DEBUG
```

This file can be ignored using `git update-index --assume-unchanged config.yaml`