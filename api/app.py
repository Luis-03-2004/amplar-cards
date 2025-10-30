from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS
import csv
import io
import utm
import zipfile
from PIL import Image, ImageOps


app = Flask(__name__)
CORS(app)  # Permite requisições do frontend


def convert_coord_to_utm(lat, long):
    """
    Converte coordenadas geográficas (latitude, longitude) para UTM.
    Retorna as coordenadas Y e X em metros no sistema UTM.
    """
    coord_y_utm, coord_x_utm, _, _ = utm.from_latlon(
        lat, long) if lat and long else ("", "", "", "")
    return coord_y_utm, coord_x_utm


def parse_and_validate_coordinates(raw_text):
    """
    Recebe texto livre de coordenadas (uma por linha).
    Regras:
      - 2 números: considera válido e retorna (lat: float, lon: float)
      - >2 itens numéricos: marca erro explícito retornando ("erro", "erro")
      - outros casos: ignora a linha
    Retorna uma lista com tuplas (lat, lon), podendo conter strings "erro".
    """
    raw_lines = raw_text.splitlines()
    coordinates = []

    for raw_line in raw_lines:
        cleaned = raw_line.strip()
        if not cleaned:
            continue

        parts = cleaned.split()

        # Mais de dois tokens: acusa erro
        if len(parts) > 2:
            coordinates.append(("erro", "erro"))
            continue

        # Diferente de dois tokens: ignora
        if len(parts) != 2:
            continue

        try:
            lat = float(parts[0])
            lon = float(parts[1])
            coordinates.append((lat, lon))
        except ValueError:
            # tokens não numéricos: ignora
            continue

    return coordinates


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/convert")
def convert():
    """
    Body esperado (JSON): { "texto_do_usuario": "-46.5658 -21.7892\n-43.2096 -22.9035" , "format": "json|csv"}
    - Campo "format" é opcional; padrão: "json".
    """
    payload = request.get_json(silent=True) or {}
    raw_text = payload.get("texto_do_usuario", "")
    output_format = (payload.get("format") or "json").lower()

    if not isinstance(raw_text, str) or not raw_text.strip():
        return jsonify({
            "error": "Campo 'texto_do_usuario' é obrigatório e deve ser uma string não vazia"
        }), 400

    coordinates = parse_and_validate_coordinates(raw_text)

    # Converte para UTM
    results = []
    for lat, lon in coordinates:
        if lat == "erro" and lon == "erro":
            results.append({"utm_y": "erro", "utm_x": "erro"})
            continue

        utm_y, utm_x = convert_coord_to_utm(lat, lon)
        results.append({"utm_y": utm_y, "utm_x": utm_x})

    if output_format == "csv":
        # Gera CSV em memória
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["utm_y", "utm_x"])
        writer.writeheader()
        for row in results:
            writer.writerow(row)
        csv_data = output.getvalue()
        output.close()
        return Response(csv_data, mimetype="text/csv")

    # Padrão: JSON
    return jsonify({"items": results, "count": len(results)})


def get_image_orientation(image: Image.Image):
    width, height = image.size
    return 'landscape' if width > height else 'portrait'

def find_closest_template_by_area(photo_width: int, photo_height: int, templates: list[Image.Image]):
    photo_area = photo_width * photo_height
    best_index = None
    min_difference = float('inf')

    for idx, template in enumerate(templates):
        try:
            template_width, template_height = template.size
            template_area = template_width * template_height
            area_difference = abs(template_area - photo_area) / max(photo_area, 1)
            if area_difference < min_difference:
                min_difference = area_difference
                best_index = idx
        except Exception:
            continue
    return best_index


def process_single_photo(src_image_bytes: bytes, landscape_templates: list[Image.Image], portrait_templates: list[Image.Image]):
    """Retorna bytes PNG processados conforme regras do simple_photo_processor."""
    photo = Image.open(io.BytesIO(src_image_bytes))
    photo = ImageOps.exif_transpose(photo)
    photo_width, photo_height = photo.size

    orientation = get_image_orientation(photo)

    # Seleção de template
    template_img = None
    if orientation == 'landscape' and landscape_templates:
        idx = find_closest_template_by_area(photo_width, photo_height, landscape_templates)
        if idx is not None:
            template_img = landscape_templates[idx]
    elif orientation == 'portrait':
        if portrait_templates:
            idx = find_closest_template_by_area(photo_width, photo_height, portrait_templates)
            if idx is not None:
                template_img = portrait_templates[idx]
    if template_img is None:
        raise ValueError('Nenhum template válido fornecido')

    # Trabalhar com cópias para não alterar imagens originais
    template = template_img.copy().convert('RGBA')
    template_width, template_height = template.size

    # Redimensionar foto para ocupar 100% do template
    scale_factor = max(template_width / photo_width, template_height / photo_height)
    new_width = int(photo_width * scale_factor)
    new_height = int(photo_height * scale_factor)
    resized_photo = photo.resize((new_width, new_height), Image.Resampling.LANCZOS).convert('RGBA')

    x_offset = (template_width - new_width) // 2
    y_offset = (template_height - new_height) // 2

    final_image = Image.new('RGBA', (template_width, template_height))
    final_image.paste(resized_photo, (x_offset, y_offset))
    final_image.paste(template, (0, 0), template)

    out_buf = io.BytesIO()
    final_image.convert('RGBA').save(out_buf, format='PNG')
    out_buf.seek(0)
    return out_buf.read()


@app.post('/images/process')
def process_images():
    """
    multipart/form-data esperado:
      - templates_landscape: múltiplos arquivos PNG (opcional, 0..N)
      - templates_portrait: múltiplos arquivos PNG (opcional, 0..N)
      - images_zip: um arquivo ZIP contendo JPG/PNG (opcional)
      - images: múltiplos arquivos (JPG/PNG) (opcional)

    É necessário ao menos um template (portrait ou landscape).
    As imagens podem vir via ZIP ou múltiplos arquivos. Se ambos vierem, são somadas.
    Retorna: application/zip com arquivos processados no padrão <nome>_processed.png
    """
    # Carregar templates landscape
    landscape_files = request.files.getlist('templates_landscape')
    landscape_templates: list[Image.Image] = []
    for f in landscape_files:
        try:
            img = Image.open(f.stream).convert('RGBA')
            landscape_templates.append(img)
        except Exception:
            continue

    # Carregar templates portrait
    portrait_files = request.files.getlist('templates_portrait')
    portrait_templates: list[Image.Image] = []
    for f in portrait_files:
        try:
            img = Image.open(f.stream).convert('RGBA')
            portrait_templates.append(img)
        except Exception:
            continue    

    if not landscape_templates and not portrait_templates:
        return jsonify({"error": "Envie ao menos um template: landscape (templates_landscape) ou retrato (templates_portrait)"}), 400

    # Coletar imagens
    images_bytes: list[tuple[str, bytes]] = []

    # ZIP
    zip_storage = request.files.get('images_zip')
    if zip_storage:
        try:
            zip_buf = io.BytesIO(zip_storage.read())
            with zipfile.ZipFile(zip_buf, 'r') as zf:
                for name in zf.namelist():
                    if name.lower().endswith(('.jpg', '.jpeg', '.png')):
                        with zf.open(name) as f:
                            images_bytes.append((name, f.read()))
        except Exception as e:
            return jsonify({"error": f"Falha ao ler ZIP: {e}"}), 400

    # Arquivos soltos
    for f in request.files.getlist('images'):
        try:
            images_bytes.append((f.filename or 'image.jpg', f.read()))
        except Exception:
            continue

    if not images_bytes:
        return jsonify({"error": "Nenhuma imagem enviada. Use 'images_zip' (ZIP) ou 'images' (arquivos)."}), 400

    # Processar e montar ZIP de saída em memória
    out_zip_buf = io.BytesIO()
    with zipfile.ZipFile(out_zip_buf, 'w', compression=zipfile.ZIP_DEFLATED) as out_zip:
        for name, data in images_bytes:
            base = name.rsplit('/', 1)[-1].rsplit('\\', 1)[-1]
            base_no_ext = base.rsplit('.', 1)[0]
            try:
                processed = process_single_photo(data, landscape_templates, portrait_templates)
                out_zip.writestr(f"{base_no_ext}_processed.png", processed)
            except Exception as e:
                # Em caso de erro por imagem, adiciona um .txt com o erro
                out_zip.writestr(f"{base_no_ext}_ERROR.txt", str(e))

    out_zip_buf.seek(0)
    return send_file(out_zip_buf, mimetype='application/zip', as_attachment=True, download_name='processed_images.zip')


if __name__ == "__main__":
    # Execução local para testes: FLASK_RUN_PORT pode ser configurada externamente
    app.run(host="0.0.0.0", port=5000, debug=True)


