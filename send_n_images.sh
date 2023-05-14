#!/bin/bash

input=$1
while IFS= read -r line
do
    image_url=$(echo "$line" | jq -r '.url')
    
    echo $image_url

    curl -s -X 'POST' \
        'http://127.0.0.1:8000/image' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{"url": "'$image_url'"}'
    #break
done < "$input"

