
varun@VarunDronamraju MINGW64 ~/Desktop/JObSearch/Application/WellnessAtWorkAI/wellness-companion-ai (main)
$ docker compose down
docker compose build core-backend
docker compose up -d
[+] Running 8/8
 ✔ Container wellness_backend                      Removed                                                                                                                           0.5s 
 ✔ Container wellness_aiml                         Removed                                                                                                                           2.2s 
 ✔ Container wellness_ollama                       Removed                                                                                                                           0.5s 
 ✔ Container wellness_data_layer                   Removed                                                                                                                           0.7s 
 ✔ Container wellness_redis                        Removed                                                                                                                           1.0s 
 ✔ Container wellness_qdrant                       Removed                                                                                                                           0.9s 
 ✔ Container wellness_postgres                     Removed                                                                                                                           0.5s 
 ✔ Network wellness-companion-ai_wellness_network  Removed                                                                                                                           0.5s 
[+] Building 3.2s (16/16) FINISHED
 => [internal] load local bake definitions                                                                                                                                           0.0s 
 => => reading from stdin 1.49kB                                                                                                                                                     0.0s
 => [internal] load build definition from Dockerfile                                                                                                                                 0.0s
 => => transferring dockerfile: 978B                                                                                                                                                 0.0s 
 => [internal] load metadata for docker.io/library/python:3.11-slim                                                                                                                  1.0s 
 => [internal] load .dockerignore                                                                                                                                                    0.0s
 => => transferring context: 2B                                                                                                                                                      0.0s 
 => [1/9] FROM docker.io/library/python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee                                                            0.0s 
 => => resolve docker.io/library/python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee                                                            0.0s 
 => [internal] load build context                                                                                                                                                    0.0s
 => => transferring context: 27.70kB                                                                                                                                                 0.0s 
 => CACHED [2/9] WORKDIR /app                                                                                                                                                        0.0s 
 => CACHED [3/9] RUN apt-get update && apt-get install -y     curl     gcc     g++     libmagic1     libmagic-dev     file     && rm -rf /var/lib/apt/lists/*                        0.0s 
 => CACHED [4/9] COPY requirements.txt .                                                                                                                                             0.0s 
 => CACHED [5/9] RUN pip install --no-cache-dir -r requirements.txt                                                                                                                  0.0s 
 => [6/9] COPY src/ ./src/                                                                                                                                                           0.1s 
 => [7/9] COPY main.py ./                                                                                                                                                            0.1s 
 => [8/9] RUN mkdir -p /app/logs /app/uploads /app/cache                                                                                                                             0.3s 
 => [9/9] RUN chmod -R 755 /app                                                                                                                                                      0.4s 
 => exporting to image                                                                                                                                                               0.6s 
 => => exporting layers                                                                                                                                                              0.2s 
 => => exporting manifest sha256:e434d6895a0789a94e4a77029e3676471243fd64845ca185c99852731b7da9de                                                                                    0.0s 
 => => exporting config sha256:19ce7b4ac53051a0b95e905673939806951473380e51a6a8711ee0ad63f156c8                                                                                      0.0s 
 => => exporting attestation manifest sha256:1a58cf898a2e85c8b6611ac976fa7f23e639f541592cbdb3c28c394311343e65                                                                        0.0s 
 => => exporting manifest list sha256:7896b64c40f4435b136a656005d2819bc3a124fca95d0594efa24d1275a6ee7f                                                                               0.0s 
 => => naming to docker.io/library/wellness-companion-ai-core-backend:latest                                                                                                         0.0s 
 => => unpacking to docker.io/library/wellness-companion-ai-core-backend:latest                                                                                                      0.2s 
 => resolving provenance for metadata file                                                                                                                                           0.0s 
[+] Building 1/1
 ✔ core-backend  Built                                                                                                                                                               0.0s 
[+] Running 8/8
 ✔ Network wellness-companion-ai_wellness_network  Created                                                                                                                           0.1s 
 ✔ Container wellness_postgres                     Started                                                                                                                           1.8s 
 ✔ Container wellness_redis                        Started                                                                                                                           1.6s 
 ✔ Container wellness_qdrant                       Started                                                                                                                           1.7s 
 ✔ Container wellness_ollama                       Started                                                                                                                           1.5s 
 ✔ Container wellness_data_layer                   Started                                                                                                                           2.0s 
 ✔ Container wellness_aiml                         Started                                                                                                                           2.3s 
 ✔ Container wellness_backend                      Started                                                                                                                           2.5s 

varun@VarunDronamraju MINGW64 ~/Desktop/JObSearch/Application/WellnessAtWorkAI/wellness-companion-ai (main)
$ curl "http://localhost:8001/api/documents/list?user_id=test_user&sort_by=size&sort_order=desc"

curl "http://localhost:8001/api/documents/list?user_id=test_user&search=test&limit=5"

curl "http://localhost:8001/api/documents/stats?user_id=test_user"
{"documents":[],"total":0,"limit":20,"offset":0,"has_more":false,"page":1,"total_pages":1,"user_id":"test_user","filters_applied":{"file_type":null,"status":null,"search":null,"sort_by":"size","sort_order":"desc"}}{"documents":[],"total":0,"limit":5,"offset":0,"has_more":false,"page":1,"total_pages":1,"user_id":"test_user","filters_applied":{"file_type":null,"status":null,"search":"test","sort_by":"created_at","sort_order":"desc"}}{"user_id":"test_user","total_documents":0,"total_size":0,"total_size_mb":0.0,"file_types":{},"status_breakdown":{},"size_distribution":{"small":0,"medium":0,"large":0},"recent_uploads":{"today":0,"this_week":0,"this_month":0},"timestamp":"2025-08-05T18:02:28.535251"}
varun@VarunDronamraju MINGW64 ~/Desktop/JObSearch/Application/WellnessAtWorkAI/wellness-companion-ai (main)
$ # 1. Upload a document first
curl -X POST http://localhost:8001/api/documents/upload \
  -F "file=@test.txt" \
  -F "user_id=test_user" \
  -F "title=My Test Document"

# 2. Now list documents (should show the uploaded file)
curl "http://localhost:8001/api/documents/list?user_id=test_user"

# 3. Get document stats
curl http://localhost:8001/docs/documents/stats?user_id=test_user"
{"success":true,"document_id":"f54f3b40-3008-446f-bb88-df20fe27ebcd","filename":"test.txt","title":"My Test Document","size":22,"status":"uploaded","timestamp":"2025-08-05T18:02:37.241999"}{"documents":[{"document_id":"f54f3b40-3008-446f-bb88-df20fe27ebcd","filename":"test.txt","file_path":"/app/uploads/test_user/f54f3b40-3008-446f-bb88-df20fe27ebcd_test.txt","size":22,"created_at":"2025-08-05T18:02:37.236251","modified_at":"2025-08-05T18:02:37.236251","status":"uploaded","file_type":".txt"}],"total":1,"limit":20,"offset":0,"has_more":false,"page":1,"total_pages":1,"user_id":"test_user","filters_applied":{"file_type":null,"status":null,"search":null,"sort_by":"created_at","sort_order":"desc","date_range":null,"size_range":null},"timestamp":"2025-08-05T18:02:37.758678"}{"detail":"Failed to get document stats: name 'timedelta' is not defined"}
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css">
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
    <title>Wellness Companion AI - Core Backend - Swagger UI</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({
        url: '/openapi.json',
    "dom_id": "#swagger-ui",
"layout": "BaseLayout",
"deepLinking": true,
"showExtensions": true,
"showCommonExtensions": true,
oauth2RedirectUrl: window.location.origin + '/docs/oauth2-redirect',
    presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
    })
    </script>
    </body>
    </html>

varun@VarunDronamraju MINGW64 ~/Desktop/JObSearch/Application/WellnessAtWorkAI/wellness-companion-ai (main)
$ # Update main.py and add list.py
docker compose down
docker compose build core-backend
docker compose up -d

# Test Task 41 endpoints:
curl "http://localhost:8001/api/documents/list?user_id=test_user"
curl "http://localhost:8001/api/documents/stats?user_id=test_user"

# Test with filters:
curl "http://localhost:8001/api/documents/list?user_id=test_user&file_type=.txt&limit=10"
[+] Running 8/8
 ✔ Container wellness_backend                      Removed                                                                                                                           0.7s 
 ✔ Container wellness_aiml                         Removed                                                                                                                           1.6s 
 ✔ Container wellness_ollama                       Removed                                                                                                                           0.5s 
 ✔ Container wellness_data_layer                   Removed                                                                                                                           0.8s 
 ✔ Container wellness_redis                        Removed                                                                                                                           0.9s 
 ✔ Container wellness_postgres                     Removed                                                                                                                           0.8s 
 ✔ Container wellness_qdrant                       Removed                                                                                                                           0.7s 
 ✔ Network wellness-companion-ai_wellness_network  Removed                                                                                                                           0.4s 
[+] Building 2.1s (16/16) FINISHED
 => [internal] load local bake definitions                                                                                                                                           0.0s 
 => => reading from stdin 1.49kB                                                                                                                                                     0.0s
 => [internal] load build definition from Dockerfile                                                                                                                                 0.0s
 => => transferring dockerfile: 978B                                                                                                                                                 0.0s 
 => [internal] load metadata for docker.io/library/python:3.11-slim                                                                                                                  1.1s 
 => [internal] load .dockerignore                                                                                                                                                    0.0s
 => => transferring context: 2B                                                                                                                                                      0.0s 
 => [1/9] FROM docker.io/library/python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee                                                            0.0s 
 => => resolve docker.io/library/python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee                                                            0.0s 
 => [internal] load build context                                                                                                                                                    0.0s
 => => transferring context: 3.64kB                                                                                                                                                  0.0s 
 => CACHED [2/9] WORKDIR /app                                                                                                                                                        0.0s 
 => CACHED [3/9] RUN apt-get update && apt-get install -y     curl     gcc     g++     libmagic1     libmagic-dev     file     && rm -rf /var/lib/apt/lists/*                        0.0s 
 => CACHED [4/9] COPY requirements.txt .                                                                                                                                             0.0s 
 => CACHED [5/9] RUN pip install --no-cache-dir -r requirements.txt                                                                                                                  0.0s 
 => CACHED [6/9] COPY src/ ./src/                                                                                                                                                    0.0s 
 => CACHED [7/9] COPY main.py ./                                                                                                                                                     0.0s 
 => CACHED [8/9] RUN mkdir -p /app/logs /app/uploads /app/cache                                                                                                                      0.0s 
 => CACHED [9/9] RUN chmod -R 755 /app                                                                                                                                               0.0s 
 => exporting to image                                                                                                                                                               0.2s 
 => => exporting layers                                                                                                                                                              0.0s 
 => => exporting manifest sha256:e434d6895a0789a94e4a77029e3676471243fd64845ca185c99852731b7da9de                                                                                    0.0s 
 => => exporting config sha256:19ce7b4ac53051a0b95e905673939806951473380e51a6a8711ee0ad63f156c8                                                                                      0.0s 
 => => exporting attestation manifest sha256:344cd0cfd976ee548da15484ce594ca2258d7d22648fa4a20d0412deae2f8990                                                                        0.0s 
 => => exporting manifest list sha256:94e4e64f11f0381ba0c1ca544bc73cbb5af3149d89e675b69d713db6f2565fb3                                                                               0.0s 
 => => naming to docker.io/library/wellness-companion-ai-core-backend:latest                                                                                                         0.0s 
 => => unpacking to docker.io/library/wellness-companion-ai-core-backend:latest                                                                                                      0.0s 
 => resolving provenance for metadata file                                                                                                                                           0.0s 
[+] Building 1/1
 ✔ core-backend  Built                                                                                                                                                               0.0s 
[+] Running 8/8
 ✔ Network wellness-companion-ai_wellness_network  Created                                                                                                                           0.1s 
 ✔ Container wellness_ollama                       Started                                                                                                                           1.4s 
 ✔ Container wellness_qdrant                       Started                                                                                                                           1.6s 
 ✔ Container wellness_redis                        Started                                                                                                                           1.7s 
 ✔ Container wellness_postgres                     Started                                                                                                                           1.5s 
 ✔ Container wellness_data_layer                   Started                                                                                                                           1.9s 
 ✔ Container wellness_aiml                         Started                                                                                                                           2.1s 
 ✔ Container wellness_backend                      Started                                                                                                                           2.4s 
curl: (52) Empty reply from server
curl: (52) Empty reply from server
{"documents":[],"total":0,"limit":10,"offset":0,"has_more":false,"page":1,"total_pages":1,"user_id":"test_user","filters_applied":{"file_type":".txt","status":null,"search":null,"sort_by":"created_at","sort_order":"desc"}}
varun@VarunDronamraju MINGW64 ~/Desktop/JObSearch/Application/WellnessAtWorkAI/wellness-companion-ai (main)
$ curl "http://localhost:8001/api/documents/list?user_id=test_user"
curl "http://localhost:8001/api/documents/stats?user_id=test_user"
{"documents":[],"total":0,"limit":20,"offset":0,"has_more":false,"page":1,"total_pages":1,"user_id":"test_user","filters_applied":{"file_type":null,"status":null,"search":null,"sort_by":"created_at","sort_order":"desc"}}{"user_id":"test_user","total_documents":0,"total_size":0,"total_size_mb":0.0,"file_types":{},"status_breakdown":{},"size_distribution":{"small":0,"medium":0,"large":0},"recent_uploads":{"today":0,"this_week":0,"this_month":0},"timestamp":"2025-08-05T18:03:07.051004"}
varun@Va







varun@VarunDronamraju MINGW64 ~/Desktop/JObSearch/Application/WellnessAtWorkAI/wellness-companion-ai (main)
$ docker compose down
docker compose build core-backend
docker compose up -d
[+] Running 8/8
 ✔ Container wellness_backend                      Removed                                                                                                                                                              0.7s 
 ✔ Container wellness_aiml                         Removed                                                                                                                                                              1.9s 
 ✔ Container wellness_data_layer                   Removed                                                                                                                                                              0.9s 
 ✔ Container wellness_ollama                       Removed                                                                                                                                                              0.5s 
 ✔ Container wellness_redis                        Removed                                                                                                                                                              1.0s 
 ✔ Container wellness_postgres                     Removed                                                                                                                                                              0.8s 
 ✔ Container wellness_qdrant                       Removed                                                                                                                                                              0.7s 
 ✔ Network wellness-companion-ai_wellness_network  Removed                                                                                                                                                              0.4s 
[+] Building 2.1s (16/16) FINISHED
 => [internal] load local bake definitions                                                                                                                                                                              0.0s
 => => reading from stdin 1.49kB                                                                                                                                                                                        0.0s
 => [internal] load build definition from Dockerfile                                                                                                                                                                    0.0s
 => => transferring dockerfile: 978B                                                                                                                                                                                    0.0s
 => [internal] load metadata for docker.io/library/python:3.11-slim                                                                                                                                                     1.0s
 => [internal] load .dockerignore                                                                                                                                                                                       0.0s
 => => transferring context: 2B                                                                                                                                                                                         0.0s
 => [1/9] FROM docker.io/library/python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee                                                                                               0.1s
 => => resolve docker.io/library/python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee                                                                                               0.0s
 => [internal] load build context                                                                                                                                                                                       0.0s
 => => transferring context: 3.89kB                                                                                                                                                                                     0.0s
 => CACHED [2/9] WORKDIR /app                                                                                                                                                                                           0.0s
 => CACHED [3/9] RUN apt-get update && apt-get install -y     curl     gcc     g++     libmagic1     libmagic-dev     file     && rm -rf /var/lib/apt/lists/*                                                           0.0s
 => CACHED [4/9] COPY requirements.txt .                                                                                                                                                                                0.0s
 => CACHED [5/9] RUN pip install --no-cache-dir -r requirements.txt                                                                                                                                                     0.0s
 => CACHED [6/9] COPY src/ ./src/                                                                                                                                                                                       0.0s
 => CACHED [7/9] COPY main.py ./                                                                                                                                                                                        0.0s
 => CACHED [8/9] RUN mkdir -p /app/logs /app/uploads /app/cache                                                                                                                                                         0.0s
 => CACHED [9/9] RUN chmod -R 755 /app                                                                                                                                                                                  0.0s
 => exporting to image                                                                                                                                                                                                  0.2s
 => => exporting layers                                                                                                                                                                                                 0.0s
 => => exporting manifest sha256:b0a814fa62beaa033e02a7d3272909a21fbc75771324e2cc4ab30fceda5577a9                                                                                                                       0.0s
 => => exporting config sha256:392ed2b77ea4f8e0d1cd5f63522de79dc8303a713f9fe23d0ec0b7ceabd496e2                                                                                                                         0.0s
 => => exporting attestation manifest sha256:14ff17727d76b3b6922dcc0d00c0edb4d81ac376ff2835b13068ea44245a854e                                                                                                           0.0s
 => => exporting manifest list sha256:b1c80a2702434aa3780ce4f756ea2b130213385cd915dc099cdd7279e5e6c1ba                                                                                                                  0.0s
 => => naming to docker.io/library/wellness-companion-ai-core-backend:latest                                                                                                                                            0.0s
 => => unpacking to docker.io/library/wellness-companion-ai-core-backend:latest                                                                                                                                         0.0s
 => resolving provenance for metadata file                                                                                                                                                                              0.0s
[+] Building 1/1
 ✔ core-backend  Built                                                                                                                                                                                                  0.0s 
[+] Running 8/8
 ✔ Network wellness-companion-ai_wellness_network  Created                                                                                                                                                              0.1s 
 ✔ Container wellness_redis                        Started                                                                                                                                                              1.6s 
 ✔ Container wellness_ollama                       Started                                                                                                                                                              1.5s 
 ✔ Container wellness_qdrant                       Started                                                                                                                                                              1.4s 
 ✔ Container wellness_postgres                     Started                                                                                                                                                              1.6s 
 ✔ Container wellness_data_layer                   Started                                                                                                                                                              1.9s 
 ✔ Container wellness_aiml                         Started                                                                                                                                                              2.1s 
 ✔ Container wellness_backend                      Started                                                                                                                                                              2.4s 

varun@VarunDronamraju MINGW64 ~/Desktop/JObSearch/Application/WellnessAtWorkAI/wellness-companion-ai (main)
$ curl -X POST http://localhost:8001/api/documents/upload \
  -F "file=@test.txt" \
  -F "user_id=test_user"

# 2. List documents (get document ID)
curl "http://localhost:8001/api/documents/list?user_id=test_user"

# 3. Test DELETE with actual document ID
curl -X DELETE "http://localhost:8001/api/documents/cde68ae0-0dbb-43e3-b6dc-de3875f6c0f1?user_id=test_user"

# 4. Verify document deleted
curl "http://localhost:8001/api/documents/list?user_id=test_user"
{"success":true,"document_id":"324ac692-a0ea-49c0-9b98-60bf0a2241cf","filename":"test.txt","title":"test.txt","size":22,"status":"uploaded","timestamp":"2025-08-05T18:49:52.467011"}{"documents":[{"document_id":"324ac692-a0ea-49c0-9b98-60bf0a2241cf","filename":"test.txt","file_path":"/app/uploads/test_user/324ac692-a0ea-49c0-9b98-60bf0a2241cf_test.txt","size":22,"created_at":"2025-08-05T18:49:52.463837","modified_at":"2025-08-05T18:49:52.463837","status":"uploaded","file_type":".txt"}],"total":1,"limit":20,"offset":0,"has_more":false,"page":1,"total_pages":1,"user_id":"test_user","filters_applied":{"file_type":null,"status":null,"search":null,"sort_by":"created_at","sort_order":"desc","date_range":null,"size_range":null},"timestamp":"2025-08-05T18:49:53.021989"}{"detail":"Document cde68ae0-0dbb-43e3-b6dc-de3875f6c0f1 not found"}{"documents":[{"document_id":"324ac692-a0ea-49c0-9b98-60bf0a2241cf","filename":"test.txt","file_path":"/app/uploads/test_user/324ac692-a0ea-49c0-9b98-60bf0a2241cf_test.txt","size":22,"created_at":"2025-08-05T18:49:52.463837","modified_at":"2025-08-05T18:49:52.463837","status":"uploaded","file_type":".txt"}],"total":1,"limit":20,"offset":0,"has_more":false,"page":1,"total_pages":1,"user_id":"test_user","filters_applied":{"file_type":null,"status":null,"search":null,"sort_by":"created_at","sort_order":"desc","date_range":null,"size_range":null},"timestamp":"2025-08-05T18:49:54.134546"}
varun@VarunDronamraju MINGW64 ~/Desktop/JObSearch/Application/WellnessAtWorkAI/wellness-companion-ai (main)
$ curl -X POST http://localhost:8001/api/documents/upload \
  -F "file=@test.txt" \
  -F "user_id=test_user"

# 2. Get document ID from upload response, then test details
curl "http://localhost:8001/api/documents/f54f3b40-3008-446f-bb88-df20fe27ebcd?user_id=test_user"

# 3. Test metadata only
curl "http://localhost:8001/api/documents/f54f3b40-3008-446f-bb88-df20fe27ebcd/metadata?user_id=test_user"

# 4. Test content preview
curl "http://localhost:8001/api/documents/f54f3b40-3008-446f-bb88-df20fe27ebcd/content?user_id=test_user&preview_length=200"
{"success":true,"document_id":"cfa4094f-4f75-4a31-92c5-d1d00801e478","filename":"test.txt","title":"test.txt","size":22,"status":"uploaded","timestamp":"2025-08-05T18:50:11.564529"}{"detail":"Document f54f3b40-3008-446f-bb88-df20fe27ebcd not found"}{"detail":"Document not found"}{"detail":"Document not found"}
varun@VarunDronamraju MINGW64 ~/Desktop/JObSearch/Application/WellnessAtWorkAI/wellness-companion-ai (main)
$ curl -X POST http://localhost:8001/api/documents/upload \
  -F "file=@test.txt" \
  -F "user_id=test_user"

# 2. Test document details (use new document ID from upload)
curl "http://localhost:8001/api/documents/{NEW_DOCUMENT_ID}?user_id=test_user"

# 3. Test metadata only
curl "http://localhost:8001/api/documents/{NEW_DOCUMENT_ID}/metadata?user_id=test_user"

# 4. Test content preview
curl "http://localhost:8001/api/documents/{NEW_DOCUMENT_ID}/content?user_id=test_user"

# 5. Test stats (should work now)
curl "http://localhost:8001/api/documents/stats?user_id=test_user"

# 6. Verify all endpoints in docs
curl http://localhost:8001/docs
{"success":true,"document_id":"6b87df54-fc33-46d4-9e02-812b2b7e8b10","filename":"test.txt","title":"test.txt","size":22,"status":"uploaded","timestamp":"2025-08-05T18:50:26.893045"}{"detail":"Document NEW_DOCUMENT_ID not found"}{"detail":"Document not found"}{"detail":"Document not found"}{"user_id":"test_user","total_documents":3,"total_size":66,"total_size_mb":0.0,"total_size_gb":0.0,"file_types":{".txt":3},"status_breakdown":{"uploaded":3},"size_distribution":{"small":3,"medium":0,"large":0},"recent_uploads":{"today":3,"this_week":3,"this_month":3},"average_file_size_mb":0.0,"timestamp":"2025-08-05T18:50:29.203783"}
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css">
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
    <title>Wellness Companion AI - Core Backend - Swagger UI</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({
        url: '/openapi.json',
    "dom_id": "#swagger-ui",
"layout": "BaseLayout",
"deepLinking": true,
"showExtensions": true,
"showCommonExtensions": true,
oauth2RedirectUrl: window.location.origin + '/docs/oauth2-redirect',
    presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
    })
    </script>
    </body>
    </html>

varun@VarunDronamraju MINGW64 ~/Desktop/JObSearch/Application/WellnessAtWorkAI/wellness-companion-ai (main)
$







varun@VarunDronamraju MINGW64 ~/Desktop/JObSearch/Application/WellnessAtWorkAI/wellness-companion-ai (main)
$ docker compose down
docker compose build core-backend
docker compose up -d
[+] Running 8/8
 ✔ Container wellness_backend                      Removed                                    0.7s 
 ✔ Container wellness_aiml                         Removed                                    1.9s 
 ✔ Container wellness_data_layer                   Removed                                    0.9s 
 ✔ Container wellness_ollama                       Removed                                    0.5s 
 ✔ Container wellness_redis                        Removed                                    1.0s 
 ✔ Container wellness_postgres                     Removed                                    0.8s 
 ✔ Container wellness_qdrant                       Removed                                    0.7s 
 ✔ Network wellness-companion-ai_wellness_network  Removed                                    0.4s 
[+] Building 2.1s (16/16) FINISHED
 => [internal] load local bake definitions                                                                                                                                                                              0.0s
 => => reading from stdin 1.49kB                                                                                                                                                                                        0.0s
 => [internal] load build definition from Dockerfile                                                                                                                                                                    0.0s
 => => transferring dockerfile: 978B                                                                                                                                                                                    0.0s
 => [internal] load metadata for docker.io/library/python:3.11-slim                                                                                                                                                     1.0s
 => [internal] load .dockerignore                                                                                                                                                                                       0.0s
 => => transferring context: 2B                                                                                                                                                                                         0.0s
 => [1/9] FROM docker.io/library/python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee                                                                                               0.1s
 => => resolve docker.io/library/python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee                                                                                               0.0s
 => [internal] load build context                                                                                                                                                                                       0.0s
 => => transferring context: 3.89kB                                                                                                                                                                                     0.0s
 => CACHED [2/9] WORKDIR /app                                                                                                                                                                                           0.0s
 => CACHED [3/9] RUN apt-get update && apt-get install -y     curl     gcc     g++     libmagic1     libmagic-dev     file     && rm -rf /var/lib/apt/lists/*                                                           0.0s
 => CACHED [4/9] COPY requirements.txt .                                                                                                                                                                                0.0s
 => CACHED [5/9] RUN pip install --no-cache-dir -r requirements.txt                                                                                                                                                     0.0s
 => CACHED [6/9] COPY src/ ./src/                                                                                                                                                                                       0.0s
 => CACHED [7/9] COPY main.py ./                                                                                                                                                                                        0.0s
 => CACHED [8/9] RUN mkdir -p /app/logs /app/uploads /app/cache                                                                                                                                                         0.0s
 => CACHED [9/9] RUN chmod -R 755 /app                                                                                                                                                                                  0.0s
 => exporting to image                                                                                                                                                                                                  0.2s
 => => exporting layers                                                                                                                                                                                                 0.0s
 => => exporting manifest sha256:b0a814fa62beaa033e02a7d3272909a21fbc75771324e2cc4ab30fceda5577a9                                                                                                                       0.0s
 => => exporting config sha256:392ed2b77ea4f8e0d1cd5f63522de79dc8303a713f9fe23d0ec0b7ceabd496e2                                                                                                                         0.0s
 => => exporting attestation manifest sha256:14ff17727d76b3b6922dcc0d00c0edb4d81ac376ff2835b13068ea44245a854e                                                                                                           0.0s
 => => exporting manifest list sha256:b1c80a2702434aa3780ce4f756ea2b130213385cd915dc099cdd7279e5e6c1ba                                                                                                                  0.0s
 => => naming to docker.io/library/wellness-companion-ai-core-backend:latest                                                                                                                                            0.0s
 => => unpacking to docker.io/library/wellness-companion-ai-core-backend:latest                                                                                                                                         0.0s
 => resolving provenance for metadata file                                                                                                                                                                              0.0s
[+] Building 1/1
 ✔ core-backend  Built                                    0.0s 
[+] Running 8/8
 ✔ Network wellness-companion-ai_wellness_network  Created                                    0.1s 
 ✔ Container wellness_redis                        Started                                    1.6s 
 ✔ Container wellness_ollama                       Started                                    1.5s 
 ✔ Container wellness_qdrant                       Started                                    1.4s 
 ✔ Container wellness_postgres                     Started                                    1.6s 
 ✔ Container wellness_data_layer                   Started                                    1.9s 
 ✔ Container wellness_aiml                         Started                                    2.1s 
 ✔ Container wellness_backend                      Started                                    2.4s 

varun@VarunDronamraju MINGW64 ~/Desktop/JObSearch/Application/WellnessAtWorkAI/wellness-companion-ai (main)
$ curl -X POST http://localhost:8001/api/documents/upload \
  -F "file=@test.txt" \
  -F "user_id=test_user"

# 2. List documents (get document ID)
curl "http://localhost:8001/api/documents/list?user_id=test_user"

# 3. Test DELETE with actual document ID
curl -X DELETE "http://localhost:8001/api/documents/cde68ae0-0dbb-43e3-b6dc-de3875f6c0f1?user_id=test_user"

# 4. Verify document deleted
curl "http://localhost:8001/api/documents/list?user_id=test_user"
{"success":true,"document_id":"324ac692-a0ea-49c0-9b98-60bf0a2241cf","filename":"test.txt","title":"test.txt","size":22,"status":"uploaded","timestamp":"2025-08-05T18:49:52.467011"}{"documents":[{"document_id":"324ac692-a0ea-49c0-9b98-60bf0a2241cf","filename":"test.txt","file_path":"/app/uploads/test_user/324ac692-a0ea-49c0-9b98-60bf0a2241cf_test.txt","size":22,"created_at":"2025-08-05T18:49:52.463837","modified_at":"2025-08-05T18:49:52.463837","status":"uploaded","file_type":".txt"}],"total":1,"limit":20,"offset":0,"has_more":false,"page":1,"total_pages":1,"user_id":"test_user","filters_applied":{"file_type":null,"status":null,"search":null,"sort_by":"created_at","sort_order":"desc","date_range":null,"size_range":null},"timestamp":"2025-08-05T18:49:53.021989"}{"detail":"Document cde68ae0-0dbb-43e3-b6dc-de3875f6c0f1 not found"}{"documents":[{"document_id":"324ac692-a0ea-49c0-9b98-60bf0a2241cf","filename":"test.txt","file_path":"/app/uploads/test_user/324ac692-a0ea-49c0-9b98-60bf0a2241cf_test.txt","size":22,"created_at":"2025-08-05T18:49:52.463837","modified_at":"2025-08-05T18:49:52.463837","status":"uploaded","file_type":".txt"}],"total":1,"limit":20,"offset":0,"has_more":false,"page":1,"total_pages":1,"user_id":"test_user","filters_applied":{"file_type":null,"status":null,"search":null,"sort_by":"created_at","sort_order":"desc","date_range":null,"size_range":null},"timestamp":"2025-08-05T18:49:54.134546"}
varun@VarunDronamraju MINGW64 ~/Desktop/JObSearch/Application/WellnessAtWorkAI/wellness-companion-ai (main)
$ curl -X POST http://localhost:8001/api/documents/upload \
  -F "file=@test.txt" \
  -F "user_id=test_user"

# 2. Get document ID from upload response, then test details
curl "http://localhost:8001/api/documents/f54f3b40-3008-446f-bb88-df20fe27ebcd?user_id=test_user"

# 3. Test metadata only
curl "http://localhost:8001/api/documents/f54f3b40-3008-446f-bb88-df20fe27ebcd/metadata?user_id=test_user"

# 4. Test content preview
curl "http://localhost:8001/api/documents/f54f3b40-3008-446f-bb88-df20fe27ebcd/content?user_id=test_user&preview_length=200"
{"success":true,"document_id":"cfa4094f-4f75-4a31-92c5-d1d00801e478","filename":"test.txt","title":"test.txt","size":22,"status":"uploaded","timestamp":"2025-08-05T18:50:11.564529"}{"detail":"Document f54f3b40-3008-446f-bb88-df20fe27ebcd not found"}{"detail":"Document not found"}{"detail":"Document not found"}
varun@VarunDronamraju MINGW64 ~/Desktop/JObSearch/Application/WellnessAtWorkAI/wellness-companion-ai (main)
$ curl -X POST http://localhost:8001/api/documents/upload \
  -F "file=@test.txt" \
  -F "user_id=test_user"

# 2. Test document details (use new document ID from upload)
curl "http://localhost:8001/api/documents/{NEW_DOCUMENT_ID}?user_id=test_user"

# 3. Test metadata only
curl "http://localhost:8001/api/documents/{NEW_DOCUMENT_ID}/metadata?user_id=test_user"

# 4. Test content preview
curl "http://localhost:8001/api/documents/{NEW_DOCUMENT_ID}/content?user_id=test_user"

# 5. Test stats (should work now)
curl "http://localhost:8001/api/documents/stats?user_id=test_user"

# 6. Verify all endpoints in docs
curl http://localhost:8001/docs
{"success":true,"document_id":"6b87df54-fc33-46d4-9e02-812b2b7e8b10","filename":"test.txt","title":"test.txt","size":22,"status":"uploaded","timestamp":"2025-08-05T18:50:26.893045"}{"detail":"Document NEW_DOCUMENT_ID not found"}{"detail":"Document not found"}{"detail":"Document not found"}{"user_id":"test_user","total_documents":3,"total_size":66,"total_size_mb":0.0,"total_size_gb":0.0,"file_types":{".txt":3},"status_breakdown":{"uploaded":3},"size_distribution":{"small":3,"medium":0,"large":0},"recent_uploads":{"today":3,"this_week":3,"this_month":3},"average_file_size_mb":0.0,"timestamp":"2025-08-05T18:50:29.203783"}
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css">
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
    <title>Wellness Companion AI - Core Backend - Swagger UI</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({
        url: '/openapi.json',
    "dom_id": "#swagger-ui",
"layout": "BaseLayout",
"deepLinking": true,
"showExtensions": true,
"showCommonExtensions": true,
oauth2RedirectUrl: window.location.origin + '/docs/oauth2-redirect',
    presets: [
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css">
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
    <title>Wellness Companion AI - Core Backend - Swagger UI</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({
        url: '/openapi.json',
    "dom_id": "#swagger-ui",
"layout": "BaseLayout",
"deepLinking": true,
"showExtensions": true,
"showCommonExtensions": true,
oauth2RedirectUrl: window.location.origin + '/docs/oauth2-redirect',
    presets: [
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
    <title>Wellness Companion AI - Core Backend - Swagger UI</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({
        url: '/openapi.json',
    "dom_id": "#swagger-ui",
"layout": "BaseLayout",
"deepLinking": true,
"showExtensions": true,
"showCommonExtensions": true,
oauth2RedirectUrl: window.location.origin + '/docs/oauth2-redirect',
    presets: [
    <body>
    <div id="swagger-ui">
    </div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({
        url: '/openapi.json',
    "dom_id": "#swagger-ui",
"layout": "BaseLayout",
"deepLinking": true,
"showExtensions": true,
"showCommonExtensions": true,
oauth2RedirectUrl: window.location.origin + '/docs/oauth2-redirect',
    presets: [
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({
        url: '/openapi.json',
    "dom_id": "#swagger-ui",
"layout": "BaseLayout",
"deepLinking": true,
"showExtensions": true,
"showCommonExtensions": true,
oauth2RedirectUrl: window.location.origin + '/docs/oauth2-redirect',
    presets: [
    "dom_id": "#swagger-ui",
"layout": "BaseLayout",
"deepLinking": true,
"showExtensions": true,
"showCommonExtensions": true,
oauth2RedirectUrl: window.location.origin + '/docs/oauth2-redirect',
    presets: [
"showExtensions": true,
"showCommonExtensions": true,
oauth2RedirectUrl: window.location.origin + '/docs/oauth2-redirect',
    presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
    })
    </script>
    </body>
    </html>

varun@VarunDronamraju MINGW64 ~/Desktop/JObSearch/Application/WellnessAtWorkAI/wellness-companion-ai (main)
$ # Test DELETE with correct document ID from list
curl -X DELETE "http://localhost:8001/api/documents/324ac692-a0ea-49c0-9b98-60bf0a2241cf?user_id=test_user"

# If that works, then Task 43 is complete
# If not, need to debug the delete router registration
{"success":true,"document_id":"324ac692-a0ea-49c0-9b98-60bf0a2241cf","filename":"test.txt","file_size":22,"user_id":"test_user","cleanup_result":{"document_id":"324ac692-a0ea-49c0-9b98-60bf0a2241cf","user_id":"test_user","cleanup_operations":[{"operation":"file_deletion","file_path":"/app/uploads/test_user/324ac692-a0ea-49c0-9b98-60bf0a2241cf_test.txt","success":true,"timestamp":"2025-08-05T18:59:33.129547","file_size":22,"message":"File deleted successfully"},{"operation":"vector_cleanup","document_id":"324ac692-a0ea-49c0-9b98-60bf0a"cleanup_operations":[{"operation":"file_deletion","file_path":"/app/uploads/test_user/324ac692-a0ea-49c0-9b98-60bf0a2241cf_test.txt","success":true,"timestamp":"2025-08-05T18:59:33.129547","file_size":22,"message":"File deleted successfully"},{"operation":"vector_cleanup","document_id":"324ac692-a0ea-49c0-9b98-60bf0a2241cf","user_id":"test_user","success":true,"timestamp":"2025-08-05T18:59:33.129929","message":"Vector cleanup placeholder - will be implemented in Phase 5"},{"operation":"metadata_cleanup","document_id":"324ac692-a0ea-49c0-9b98-60bf0a2241cf","user_id":"test_user","success":true,"timestamp":"2025-08-05T18:59:33.130001","message":"Metadata cleanup placeholder - will be implemented in Phase 5"},{"operation":"cache_cleanup","document_id":"324ac692-a0ea-49c0-9b98-60bf0a2241cf","user_id":"test_user","success":true,"timestamp":"2025-08-05T18:59:33.130099","message":"Cache cleanup completed (file-based cache)","cleaned_cache_files":0}],"overall_success":true,"cleanup_time":"2025-08-05T18:59:33.129536"},"deleted_at":"2025-08-05T18:59:33.130840"}
varun@VarunDronamraju MINGW64 ~/Desktop/JObSearch/Application/WellnessAtWorkAI/wellness-companion-ai (main)
$













