PS C:\Users\varun\Desktop\JObSearch\Application\WellnessAtWorkAI\wellness-companion-ai> docker-compose build aiml-orchestration
time="2025-08-03T12:11:13+05:30" level=warning msg="C:\\Users\\varun\\Desktop\\JObSearch\\Application\\WellnessAtWorkAI\\wellness-companion-ai\\docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion"
[+] Building 128.5s (14/14) FINISHED
 => [internal] load local bake definitions                                                                                       0.0s
 => => reading from stdin 1.04kB                                                                                                 0.0s
 => [internal] load build definition from Dockerfile                                                                             0.0s
 => => transferring dockerfile: 754B                                                                                             0.0s
 => [internal] load metadata for docker.io/library/python:3.11-slim                                                              2.3s
 => [auth] library/python:pull token for registry-1.docker.io                                                                    0.0s
 => [internal] load .dockerignore                                                                                                0.1s
 => => transferring context: 2B                                                                                                  0.0s
 => [1/6] FROM docker.io/library/python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee        0.1s
 => => resolve docker.io/library/python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee        0.1s
 => [internal] load build context                                                                                                0.2s
 => => transferring context: 2.99kB                                                                                              0.2s
 => CACHED [2/6] WORKDIR /app                                                                                                    0.0s 
 => [3/6] RUN apt-get update && apt-get install -y     curl     build-essential     && rm -rf /var/lib/apt/lists/*              51.8s
 => [4/6] COPY requirements.txt .                                                                                                0.2s
 => [5/6] RUN pip install --no-cache-dir -r requirements.txt                                                                    33.3s 
 => [6/6] COPY src/ ./src/                                                                                                       0.3s 
 => exporting to image                                                                                                          39.0s 
 => => exporting layers                                                                                                         23.4s 
 => => exporting manifest sha256:3a0d5ba85c2f5ea25a9616ec32a0a9caca576857fb50b36262ef0c341d45db6b                                0.0s 
 => => exporting config sha256:cece3eff1893e69f518bbf38bc98c1f9adcc00a541271271a5c05b3b7a0d988f                                  0.0s 
 => => exporting attestation manifest sha256:f22baf9f56b49962be88abac97d3ab797f0886c3d44d52e1535d69cea7962e79                    0.1s 
 => => exporting manifest list sha256:603e8a9dd4c3198a2f6e0656afc634e50778aa7553e75522f17101c997bd585a                           0.0s 
 => => naming to docker.io/library/wellness-companion-ai-aiml-orchestration:latest                                               0.0s 
 => => unpacking to docker.io/library/wellness-companion-ai-aiml-orchestration:latest                                           15.3s 
 => resolving provenance for metadata file                                                                                       0.1s 
[+] Building 1/1
 ✔ aiml-orchestration  Built                                                                                                     0.0s 
PS C:\Users\varun\Desktop\JObSearch\Application\WellnessAtWorkAI\wellness-companion-ai> docker-compose build core-backend
time="2025-08-03T12:17:49+05:30" level=warning msg="C:\\Users\\varun\\Desktop\\JObSearch\\Application\\WellnessAtWorkAI\\wellness-companion-ai\\docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion" 
[+] Building 32.6s (14/14) FINISHED
 => [internal] load local bake definitions                                                                                       0.0s 
 => => reading from stdin 1.49kB                                                                                                 0.0s
 => [internal] load build definition from Dockerfile                                                                             0.0s
 => => transferring dockerfile: 736B                                                                                             0.0s 
 => [internal] load metadata for docker.io/library/python:3.11-slim                                                              2.1s 
 => [auth] library/python:pull token for registry-1.docker.io                                                                    0.0s 
 => [internal] load .dockerignore                                                                                                0.1s
 => => transferring context: 2B                                                                                                  0.0s 
 => [1/6] FROM docker.io/library/python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee        0.1s 
 => => resolve docker.io/library/python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee        0.1s 
 => [internal] load build context                                                                                                0.2s 
 => => transferring context: 3.62kB                                                                                              0.1s 
 => CACHED [2/6] WORKDIR /app                                                                                                    0.0s
 => CACHED [3/6] RUN apt-get update && apt-get install -y     curl     build-essential     && rm -rf /var/lib/apt/lists/*        0.0s 
 => [4/6] COPY requirements.txt .                                                                                                0.1s
 => [5/6] RUN pip install --no-cache-dir -r requirements.txt                                                                    19.6s 
 => [6/6] COPY src/ ./src/                                                                                                       0.2s 
 => exporting to image                                                                                                           9.4s 
 => => exporting layers                                                                                                          6.3s 
 => => exporting manifest sha256:b513d3d665d9415fac4aea14b67e6f6732710488b615b4ab32324ebbcb5a3dbe                                0.0s 
 => => exporting config sha256:e031842ae8fd900b400f599466809f904ffb70850ceb9d194c784290159a72a6                                  0.0s 
 => => exporting attestation manifest sha256:488e4c656ad39e34cab0c90b4ec36590bf220808636e0179b3d0222b384510a3                    0.0s 
 => => exporting manifest list sha256:19b2c24e05055e2a7fbc226f209f9237b65acf880749c5934279b8f7f93a78d8                           0.0s 
 => => naming to docker.io/library/wellness-companion-ai-core-backend:latest                                                     0.0s 
 => => unpacking to docker.io/library/wellness-companion-ai-core-backend:latest                                                  2.8s 
 => resolving provenance for metadata file                                                                                       0.0s 
[+] Building 1/1
 ✔ core-backend  Built                                                                                                           0.0s 
PS C:\Users\varun\Desktop\JObSearch\Application\WellnessAtWorkAI\wellness-companion-ai> docker-compose build data-layer
time="2025-08-03T12:19:28+05:30" level=warning msg="C:\\Users\\varun\\Desktop\\JObSearch\\Application\\WellnessAtWorkAI\\wellness-companion-ai\\docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion" 
[+] Building 74.8s (10/13)
 => [internal] load local bake definitions                                                                                       0.0s 
 => => reading from stdin 554B                                                                                                   0.0s
 => [internal] load build definition from Dockerfile                                                                             0.1s
 => => transferring dockerfile: 891B                                                                                             0.0s 
 => [internal] load metadata for docker.io/library/python:3.11-slim                                                              1.0s 
 => [internal] load .dockerignore                                                                                                0.1s
 => => transferring context: 2B                                                                                                  0.0s 
 => [1/8] FROM docker.io/library/python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee        0.1s 
 => => resolve docker.io/library/python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee        0.1s 
 => [internal] load build context                                                                                                0.2s 
 => => transferring context: 9.81kB                                                                                              0.1s
 => CACHED [2/8] WORKDIR /app                                                                                                    0.0s 
 => [3/8] RUN apt-get update && apt-get install -y     curl     build-essential     postgresql-client     && rm -rf /var/lib/a  63.9s 
 => [4/8] COPY requirements.txt .                                                                                                0.2s
 => ERROR [5/8] RUN pip install --no-cache-dir -r requirements.txt                                                               8.4s
------
 > [5/8] RUN pip install --no-cache-dir -r requirements.txt:
4.282 Collecting fastapi==0.104.1 (from -r requirements.txt (line 2))
4.393   Downloading fastapi-0.104.1-py3-none-any.whl.metadata (24 kB)
4.474 Collecting uvicorn==0.24.0 (from uvicorn[standard]==0.24.0->-r requirements.txt (line 3))
4.488   Downloading uvicorn-0.24.0-py3-none-any.whl.metadata (6.4 kB)
4.992 Collecting sqlalchemy==2.0.23 (from -r requirements.txt (line 6))
5.006   Downloading SQLAlchemy-2.0.23-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (9.6 kB)
5.072 Collecting alembic==1.12.1 (from -r requirements.txt (line 7))
5.082   Downloading alembic-1.12.1-py3-none-any.whl.metadata (7.3 kB)
5.213 Collecting psycopg2-binary==2.9.9 (from -r requirements.txt (line 8))
5.225   Downloading psycopg2_binary-2.9.9-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (4.4 kB)
5.305 Collecting asyncpg==0.29.0 (from -r requirements.txt (line 9))
5.316   Downloading asyncpg-0.29.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (4.4 kB)
5.397 Collecting redis==5.0.1 (from -r requirements.txt (line 12))
5.408   Downloading redis-5.0.1-py3-none-any.whl.metadata (8.9 kB)
5.480 Collecting qdrant-client==1.7.0 (from -r requirements.txt (line 13))
5.491   Downloading qdrant_client-1.7.0-py3-none-any.whl.metadata (9.3 kB)
5.539 Collecting PyPDF2==3.0.1 (from -r requirements.txt (line 16))
5.548   Downloading pypdf2-3.0.1-py3-none-any.whl.metadata (6.8 kB)
5.577 Collecting python-docx==1.1.0 (from -r requirements.txt (line 17))
5.587   Downloading python_docx-1.1.0-py3-none-any.whl.metadata (2.0 kB)
5.616 Collecting python-multipart==0.0.6 (from -r requirements.txt (line 18))
5.626   Downloading python_multipart-0.0.6-py3-none-any.whl.metadata (2.5 kB)
5.653 Collecting aiofiles==23.2.1 (from -r requirements.txt (line 19))
5.663   Downloading aiofiles-23.2.1-py3-none-any.whl.metadata (9.7 kB)
6.379 Collecting boto3==1.34.0 (from -r requirements.txt (line 22))
6.388   Downloading boto3-1.34.0-py3-none-any.whl.metadata (6.6 kB)
7.218 Collecting botocore==1.34.0 (from -r requirements.txt (line 23))
7.235   Downloading botocore-1.34.0-py3-none-any.whl.metadata (5.6 kB)
7.636 ERROR: Ignored the following yanked versions: 37.0.3, 38.0.2, 45.0.0
7.636 ERROR: Ignored the following versions that require a different python version: 0.11.10 Requires-Python >=3.7,<=3.11; 1.0.0 Requires-Python >=3.7,<=3.11; 1.0.1 Requires-Python >=3.7,<=3.11; 1.0.2 Requires-Python >=3.7,<=3.11
7.637 ERROR: Could not find a version that satisfies the requirement cryptography==41.0.8 (from versions: 0.1, 0.2, 0.2.1, 0.2.2, 0.3, 0.4, 0.5, 0.5.1, 0.5.2, 0.5.3, 0.5.4, 0.6, 0.6.1, 0.7, 0.7.1, 0.7.2, 0.8, 0.8.1, 0.8.2, 0.9, 0.9.1, 0.9.2, 0.9.3, 1.0, 1.0.1, 1.0.2, 1.1, 1.1.1, 1.1.2, 1.2, 1.2.1, 1.2.2, 1.2.3, 1.3, 1.3.1, 1.3.2, 1.3.3, 1.3.4, 1.4, 1.5, 1.5.1, 1.5.2, 1.5.3, 1.6, 1.7, 1.7.1, 1.7.2, 1.8, 1.8.1, 1.8.2, 1.9, 2.0, 2.0.1, 2.0.2, 2.0.3, 2.1, 2.1.1, 2.1.2, 2.1.3, 2.1.4, 2.2, 2.2.1, 2.2.2, 2.3, 2.3.1, 2.4, 2.4.1, 2.4.2, 2.5, 2.6, 2.6.1, 2.7, 2.8, 2.9, 2.9.1, 2.9.2, 3.0, 3.1, 3.1.1, 3.2, 3.2.1, 3.3, 3.3.1, 3.3.2, 3.4, 3.4.1, 3.4.2, 3.4.3, 3.4.4, 3.4.5, 3.4.6, 3.4.7, 3.4.8, 35.0.0, 36.0.0, 36.0.1, 36.0.2, 37.0.0, 37.0.1, 37.0.2, 37.0.4, 38.0.0, 38.0.1, 38.0.3, 38.0.4, 39.0.0, 39.0.1, 39.0.2, 40.0.0, 40.0.1, 40.0.2, 41.0.0, 41.0.1, 41.0.2, 41.0.3, 41.0.4, 41.0.5, 41.0.6, 41.0.7, 42.0.0, 42.0.1, 42.0.2, 42.0.3, 42.0.4, 42.0.5, 42.0.6, 42.0.7, 42.0.8, 43.0.0, 43.0.1, 43.0.3, 44.0.0, 44.0.1, 44.0.2, 44.0.3, 45.0.1, 45.0.2, 45.0.3, 45.0.4, 45.0.5)        
7.638 ERROR: No matching distribution found for cryptography==41.0.8
7.805
7.805 [notice] A new release of pip is available: 24.0 -> 25.2
7.805 [notice] To update, run: pip install --upgrade pip
------
Dockerfile:14

--------------------

  12 |     # Copy requirements and install Python dependencies

  13 |     COPY requirements.txt .

  14 | >>> RUN pip install --no-cache-dir -r requirements.txt

  15 |

  16 |     # Copy source code (will be empty for now)

--------------------

failed to solve: process "/bin/sh -c pip install --no-cache-dir -r requirements.txt" did not complete successfully: exit code: 1      

130  /usr/local/bin/dockerd --config-file /run/config/docker/daemon.json --containerd /run/containerd/containerd.sock --pidfile /run/desktop/docker.pid --swarm-default-advertise-addr=192.168.65.3 --host-gateway-ip 192.168.65.254

github.com/moby/buildkit/executor/runcexecutor.exitError

        /root/build-deb/engine/vendor/github.com/moby/buildkit/executor/runcexecutor/executor.go:391

github.com/moby/buildkit/executor/runcexecutor.(*runcExecutor).Run

        /root/build-deb/engine/vendor/github.com/moby/buildkit/executor/runcexecutor/executor.go:339

github.com/moby/buildkit/solver/llbsolver/ops.(*ExecOp).Exec

        /root/build-deb/engine/vendor/github.com/moby/buildkit/solver/llbsolver/ops/exec.go:492

github.com/moby/buildkit/solver.(*sharedOp).Exec.func2

        /root/build-deb/engine/vendor/github.com/moby/buildkit/solver/jobs.go:1120

github.com/moby/buildkit/util/flightcontrol.(*call[...]).run

        /root/build-deb/engine/vendor/github.com/moby/buildkit/util/flightcontrol/flightcontrol.go:122

sync.(*Once).doSlow

        /usr/local/go/src/sync/once.go:78

sync.(*Once).Do

        /usr/local/go/src/sync/once.go:69

runtime.goexit

        /usr/local/go/src/runtime/asm_amd64.s:1700



21896 v0.25.0-desktop.1 C:\Program Files\Docker\cli-plugins\docker-buildx.exe bake --file - --progress rawjson --metadata-file C:\Users\varun\AppData\Local\Temp\compose-build-metadataFile-1202365362.json --allow fs.read=C:\Users\varun\Desktop\JObSearch\Application\WellnessAtWorkAI\wellness-companion-ai\services\data-layer

google.golang.org/grpc.(*ClientConn).Invoke

        google.golang.org/grpc@v1.72.2/call.go:35

github.com/moby/buildkit/api/services/control.(*controlClient).Solve

        github.com/moby/buildkit@v0.23.0/api/services/control/control_grpc.pb.go:88

github.com/moby/buildkit/client.(*Client).solve.func2

        github.com/moby/buildkit@v0.23.0/client/solve.go:268

golang.org/x/sync/errgroup.(*Group).add.func1

        golang.org/x/sync@v0.14.0/errgroup/errgroup.go:130

runtime.goexit

        runtime/asm_amd64.s:1700



130  /usr/local/bin/dockerd --config-file /run/config/docker/daemon.json --containerd /run/containerd/containerd.sock --pidfile /run/desktop/docker.pid --swarm-default-advertise-addr=192.168.65.3 --host-gateway-ip 192.168.65.254

github.com/moby/buildkit/solver.(*edge).execOp

        /root/build-deb/engine/vendor/github.com/moby/buildkit/solver/edge.go:963

github.com/moby/buildkit/solver/internal/pipe.NewWithFunction[...].func2

        /root/build-deb/engine/vendor/github.com/moby/buildkit/solver/internal/pipe/pipe.go:78

runtime.goexit

        /usr/local/go/src/runtime/asm_amd64.s:1700



21896 v0.25.0-desktop.1 C:\Program Files\Docker\cli-plugins\docker-buildx.exe bake --file - --progress rawjson --metadata-file C:\Users\varun\AppData\Local\Temp\compose-build-metadataFile-1202365362.json --allow fs.read=C:\Users\varun\Desktop\JObSearch\Application\WellnessAtWorkAI\wellness-companion-ai\services\data-layer

github.com/moby/buildkit/client.(*Client).solve.func2

        github.com/moby/buildkit@v0.23.0/client/solve.go:285

golang.org/x/sync/errgroup.(*Group).add.func1

        golang.org/x/sync@v0.14.0/errgroup/errgroup.go:130



130  /usr/local/bin/dockerd --config-file /run/config/docker/daemon.json --containerd /run/containerd/containerd.sock --pidfile /run/desktop/docker.pid --swarm-default-advertise-addr=192.168.65.3 --host-gateway-ip 192.168.65.254

github.com/moby/buildkit/solver/llbsolver/ops.(*ExecOp).Exec

        /root/build-deb/engine/vendor/github.com/moby/buildkit/solver/llbsolver/ops/exec.go:513

github.com/moby/buildkit/solver.(*sharedOp).Exec.func2

        /root/build-deb/engine/vendor/github.com/moby/buildkit/solver/jobs.go:1120



PS C:\Users\varun\Desktop\JObSearch\Application\WellnessAtWorkAI\wellness-companion-ai> docker-compose build data-layer
time="2025-08-03T12:22:35+05:30" level=warning msg="C:\\Users\\varun\\Desktop\\JObSearch\\Application\\WellnessAtWorkAI\\wellness-companion-ai\\docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion" 
[+] Building 86.9s (16/16) FINISHED
 => [internal] load local bake definitions                                                                                       0.0s 
 => => reading from stdin 554B                                                                                                   0.0s
 => [internal] load build definition from Dockerfile                                                                             0.0s
 => => transferring dockerfile: 891B                                                                                             0.0s 
 => [internal] load metadata for docker.io/library/python:3.11-slim                                                              2.0s 
 => [auth] library/python:pull token for registry-1.docker.io                                                                    0.0s 
 => [internal] load .dockerignore                                                                                                0.0s
 => => transferring context: 2B                                                                                                  0.0s 
 => [1/8] FROM docker.io/library/python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee        0.1s 
 => => resolve docker.io/library/python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee        0.1s 
 => [internal] load build context                                                                                                0.1s 
 => => transferring context: 3.33kB                                                                                              0.1s
 => CACHED [2/8] WORKDIR /app                                                                                                    0.0s 
 => CACHED [3/8] RUN apt-get update && apt-get install -y     curl     build-essential     postgresql-client     && rm -rf /var  0.0s 
 => [4/8] COPY requirements.txt .                                                                                                0.0s
 => [5/8] RUN pip install --no-cache-dir -r requirements.txt                                                                    44.7s 
 => [6/8] COPY src/ ./src/                                                                                                       0.3s 
 => [7/8] COPY scripts/ ./scripts/                                                                                               0.1s 
 => [8/8] RUN mkdir -p /app/uploads /app/cache                                                                                   0.4s 
 => exporting to image                                                                                                          37.6s 
 => => exporting layers                                                                                                         23.9s 
 => => exporting manifest sha256:637c4c6c3a48c7a3af4c204ade711eb0198b156bac9e31efec907cea5d539638                                0.0s 
 => => exporting config sha256:4f0d3912f877a1d52ddf0ec0e2638b38184af62bc8f65616d9237dddde02ed9d                                  0.0s 
 => => exporting attestation manifest sha256:64e11cf829cf76b034392a6e2c50d0796087ac8b7d40bea87f7001606737a18f                    0.0s 
 => => exporting manifest list sha256:7fce91e67a9ad44a5cef9872e9ac626acf9c362c338b182ce575c9e20982363a                           0.0s 
 => => naming to docker.io/library/wellness-companion-ai-data-layer:latest                                                       0.0s 
 => => unpacking to docker.io/library/wellness-companion-ai-data-layer:latest                                                   13.4s 
 => resolving provenance for metadata file                                                                                       0.0s 
[+] Building 1/1
 ✔ data-layer  Built                                                                                                             0.0s 
PS C:\Users\varun\Desktop\JObSearch\Application\WellnessAtWorkAI\wellness-companion-ai> 








-----------------------------

PS C:\Users\varun\Desktop\JObSearch\Application\WellnessAtWorkAI\wellness-companion-ai> # 1. Build fixed core-backend
PS C:\Users\varun\Desktop\JObSearch\Application\WellnessAtWorkAI\wellness-companion-ai> docker-compose build core-backend
time="2025-08-03T15:25:14+05:30" level=warning msg="C:\\Users\\varun\\Desktop\\JObSearch\\Application\\WellnessAtWorkAI\\wellness-companion-ai\\docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion"
[+] Building 93.7s (16/16) FINISHED
 => [internal] load local bake definitions                                                                                                                                           0.0s
 => => reading from stdin 1.04kB                                                                                                                                                     0.0s
 => [internal] load build definition from Dockerfile                                                                                                                                 0.0s
 => => transferring dockerfile: 1.07kB                                                                                                                                               0.0s
 => [internal] load metadata for docker.io/library/python:3.11-slim                                                                                                                  2.0s
 => [auth] library/python:pull token for registry-1.docker.io                                                                                                                        0.0s
 => [internal] load .dockerignore                                                                                                                                                    0.0s
 => => transferring context: 2B                                                                                                                                                      0.0s
 => [internal] load build context                                                                                                                                                    0.1s
 => => transferring context: 4.22kB                                                                                                                                                  0.1s
 => [1/8] FROM docker.io/library/python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee                                                            0.1s
 => => resolve docker.io/library/python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee                                                            0.1s
 => CACHED [2/8] WORKDIR /app                                                                                                                                                        0.0s
 => CACHED [3/8] RUN apt-get update && apt-get install -y     curl     gcc     g++     && rm -rf /var/lib/apt/lists/*                                                                0.0s 
 => [4/8] COPY requirements.txt .                                                                                                                                                    0.1s
 => [5/8] RUN pip install --no-cache-dir -r requirements.txt                                                                                                                        67.1s 
 => [6/8] COPY src/ ./src/                                                                                                                                                           0.3s 
 => [7/8] RUN mkdir -p /app/logs /app/uploads /app/cache                                                                                                                             0.4s 
 => [8/8] RUN chmod -R 755 /app                                                                                                                                                      0.5s 
 => exporting to image                                                                                                                                                              21.3s 
 => => exporting layers                                                                                                                                                             11.3s 
 => => exporting manifest sha256:0c8308d120f5f70358d1a0ba6e53149d7b1a5eed337d9ba00aa97af39112cc4b                                                                                    0.0s 
 => => exporting config sha256:c476c468b11e1413d02af8ba02f1b6404abfaed2eeb5da6ff3de31dd52abe62f                                                                                      0.0s 
 => => exporting attestation manifest sha256:c58de16629262cec95c3c7768baa45153c7c4f62043208f505eb37bb26f43822                                                                        0.0s 
 => => exporting manifest list sha256:0911b96411af0581c48bddb8c2382e06a348b18068278f1fab25ad5d0ad949c8                                                                               0.0s 
 => => naming to docker.io/library/wellness-companion-ai-core-backend:latest                                                                                                         0.0s
 => => unpacking to docker.io/library/wellness-companion-ai-core-backend:latest                                                                                                      9.6s 
 => resolving provenance for metadata file                                                                                                                                           0.1s 
[+] Building 1/1
 ✔ core-backend  Built                                                                                                                                                               0.0s 
PS C:\Users\varun\Desktop\JObSearch\Application\WellnessAtWorkAI\wellness-companion-ai> 
PS C:\Users\varun\Desktop\JObSearch\Application\WellnessAtWorkAI\wellness-companion-ai> # 2. Start it (should work now)
PS C:\Users\varun\Desktop\JObSearch\Application\WellnessAtWorkAI\wellness-companion-ai> docker-compose up core-backend -d
time="2025-08-03T15:26:49+05:30" level=warning msg="C:\\Users\\varun\\Desktop\\JObSearch\\Application\\WellnessAtWorkAI\\wellness-companion-ai\\docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion"
[+] Running 5/5
 ✔ Container wellness_qdrant   Running                                                                                                                                               0.0s 
 ✔ Container wellness_redis    Running                                                                                                                                               0.0s 
 ✔ Container wellness_backend  Started                                                                                                                                               5.9s 
 ✔ Container wellness_ollama   Started                                                                                                                                               0.1s 
 ✔ Container wellness_aiml     Started                                                                                                                                               0.6s 
PS C:\Users\varun\Desktop\JObSearch\Application\WellnessAtWorkAI\wellness-companion-ai> 
PS C:\Users\varun\Desktop\JObSearch\Application\WellnessAtWorkAI\wellness-companion-ai> # 3. Test it
PS C:\Users\varun\Desktop\JObSearch\Application\WellnessAtWorkAI\wellness-companion-ai>     