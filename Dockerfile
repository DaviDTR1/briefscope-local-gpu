FROM python:3.11-slim

WORKDIR /code

# System deps:
#   - libmupdf-dev, gcc/g++: build PyMuPDF and native wheels
#   - pandoc: Markdown -> DOCX (rapid mode)
#   - libpango / libcairo / libgdk-pixbuf / fonts: WeasyPrint runtime (Markdown -> PDF)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmupdf-dev gcc g++ \
    pandoc \
    libpango-1.0-0 libpangocairo-1.0-0 libcairo2 \
    libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info \
    fonts-dejavu-core fonts-liberation fonts-lato \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app           /code/app
COPY prompts       /code/prompts
COPY frontend_dist /code/frontend_dist

RUN mkdir -p /code/data /code/generated

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
