# Project description

The project implements self-learning image classification system.
It allows to post an image and get the category of the image.
If the image is not recognized then the category will be inferenced after processing all non-recognized images.

# Technology stack

1. Pytorch (Inference engine, should be Triton)
2. Milvus (Zilliz Cloud)
3. sklearn
4. FastAPI

# Data example

https://www.kaggle.com/datasets/alessiocorrado99/animals10
https://github.com/yashenkoxciv/animals_10_uploader

# Run

```
docker run -d -p 27017:27017 mongo:6.0.5
```

```
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.11-management
```


# Tests

```
bash send_n_images.sh /Users/artemyashenko/filestack-uploader/gatto_100.txt
```
