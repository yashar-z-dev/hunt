# build images
```
docker build -t hunt:1.0 .
```

---
# run
```
docker run -d \
  --name hunt \
  --restart unless-stopped \
  -v ~/hunt:/app \
  hunt:1.0
```

---
# bash
```
docker run -it --rm \
  --name hunt-debug \
  -v ~/hunt:/app \
  hunt:1.0 bash
```