from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import csv
import io
import utm


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


if __name__ == "__main__":
    # Execução local para testes: FLASK_RUN_PORT pode ser configurada externamente
    app.run(host="0.0.0.0", port=5000, debug=True)


