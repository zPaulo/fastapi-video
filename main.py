from pathlib import Path
from fastapi import FastAPI, Request, Response, Header, HTTPException
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Configuração de templates e vídeo
templates = Jinja2Templates(directory="static")
CHUNK_SIZE = 1024 * 1024  # Tamanho do chunk (1MB)
video_path = Path("data/video/video.mp4")

@app.get("/")
async def read_root(request: Request):
    """
    Renderiza a página inicial (HTML com o player de vídeo).
    """
    return templates.TemplateResponse("teste.html", {"request": request})

@app.get("/video")
async def video_endpoint(range: str = Header(None)):
    """
    Endpoint para streaming do vídeo.
    """
    try:
        # Verifica se o arquivo de vídeo existe
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="Video file not found")

        # Configuração do range (bytes para leitura)
        file_size = video_path.stat().st_size
        start = 0
        end = CHUNK_SIZE

        if range:
            start, end = range.replace("bytes=", "").split("-")
            start = int(start)
            end = int(end) if end else start + CHUNK_SIZE

        # Ajusta o tamanho máximo do range
        end = min(end, file_size - 1)

        # Lê o arquivo de vídeo
        with open(video_path, "rb") as video:
            video.seek(start)
            data = video.read(end - start + 1)

        # Configura os cabeçalhos de resposta
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(end - start + 1),
            "Content-Type": "video/mp4",
        }

        return Response(data, status_code=206, headers=headers)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid range header")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
