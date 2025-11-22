# build images
```
docker build -t <image_name>:<image_tags> .
```

---
# run
```
docker run -d \
  --name <container_name> \
  --restart unless-stopped \
  -v ~/<dirctory>:/app \
  <image_name_or_id>:<image_tags>
```

---
# bash
```
docker run -it --rm \
  --name <container_name> \
  -v ~/<dirctory>:/app \
  <image_name_or_id>:<image_tags> bash
```

```
docker exec -it <container_name_or_id> /bin/bash
```

```
docker exec -it <container_name_or_id> /bin/sh
```

```
docker exec -it --user <username_or_uid> <container_name_or_id> /bin/bash
```