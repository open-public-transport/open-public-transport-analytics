docker pull ftopal/keplergl

docker run  \
    --name keplergl \
    --rm \
    -p 8080:80 \
    -e MapboxAccessToken="yourMapboxAccessToken" \
    -d \
    ftopal/keplergl