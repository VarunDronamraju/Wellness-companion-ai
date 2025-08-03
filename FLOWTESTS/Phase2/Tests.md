
varun@VarunDronamraju MINGW64 ~/Desktop/JObSearch/Application/WellnessAtWorkAI/wellness-companion-ai (main)
$ docker exec -it wellness_data_layer python -c "
import sys; sys.path.append('/app/src');
from vector_db.qdrant_client import DataLayerQdrantClient;
print('✅ Import successful')
"
✅ Import successful

varun@VarunDronamraju MINGW64 ~/Desktop/JObSearch/Application/WellnessAtWorkAI/wellness-companion-ai (main)
$ 

