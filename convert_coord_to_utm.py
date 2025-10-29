#!/bin/env python3

import csv
import shutil
import os
import json
from PIL import Image, ImageFont, ImageDraw
import textwrap
import utm
import inquirer
from os import listdir


def convert_coord_to_utm(lat, long):
    coord_y_utm, coord_x_utm, _, _ = utm.from_latlon(
        lat, long) if lat and long else ("", "", "", "")
    return coord_y_utm, coord_x_utm

def process_json_coordinates(json_file_path):
    """Processa arquivo JSON com coordenadas e converte para UTM"""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    coordinates = data.get('coordinates', [])
    utm_data = []
    
    for coord_string in coordinates:
        # Faz split por espaço e pega latitude e longitude
        parts = coord_string.strip().split()
        if len(parts) >= 2:
            try:
                lat = float(parts[0])
                long = float(parts[1])
                
                # Converte para UTM
                coord_y_utm, coord_x_utm = convert_coord_to_utm(lat, long)
                
                utm_data.append({
                    'original_coordinates': coord_string,
                    'latitude': lat,
                    'longitude': long,
                    'utm_y': coord_y_utm,
                    'utm_x': coord_x_utm
                })
                
                print(f"Convertido: {coord_string} -> UTM Y: {coord_y_utm}, X: {coord_x_utm}")
                
            except ValueError:
                print(f"Erro ao processar coordenada: {coord_string}")
                continue
    
    return utm_data

def save_json_to_csv(utm_data, output_file):
    """Salva os dados UTM em formato CSV"""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['original_coordinates', 'latitude', 'longitude', 'utm_y', 'utm_x']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in utm_data:
            writer.writerow(row)

def main():
    files = listdir('.')
    csv_files = [f for f in files if f.endswith('.csv')]
    json_files = [f for f in files if f.endswith('.json')]

    # Primeiro, escolher o tipo de arquivo
    file_type_questions = [
        inquirer.List('file_type',
                     message="Selecione o tipo de arquivo",
                     choices=["CSV", "JSON"]
                     ),
    ]
    file_type = inquirer.prompt(file_type_questions)["file_type"]

    if file_type == "JSON":
        # Processamento de arquivo JSON
        json_questions = [
            inquirer.List('jsonfile',
                         message="Selecione o arquivo JSON",
                         choices=json_files
                         ),
        ]
        json_file = inquirer.prompt(json_questions)["jsonfile"]
        
        print(f"Processando arquivo JSON: {json_file}")
        utm_data = process_json_coordinates(json_file)
        
        output_csv = "output_utm_from_json.csv"
        save_json_to_csv(utm_data, output_csv)
        print(f"Dados convertidos salvos em: {output_csv}")
        return

    # Processamento de arquivo CSV (código original)
    questions = [
    inquirer.List('csvfile',
                    message="Selecione o arquivo csv",
                    choices=csv_files
                ),
    inquirer.List('delimiter',
                    message="Selecione o caracter delimitador do csv",
                    choices=[",", ";"]
                ),
    inquirer.List('quotechar',
                    message="Selecione o caracter de aspas do csv",
                    choices=['"', "'"]
                ),
    inquirer.List('encoding',
                    message="Selecione o encoding do arquivo (se o csv foi gerado no windows, deve ser ISO-8859-1)",
                    choices=["ISO-8859-1", "utf-8"]
                ),
    ]
    q_files = inquirer.prompt(questions)

    f = open(q_files["csvfile"], encoding=q_files["encoding"])
    reader = csv.reader(f, delimiter=q_files["delimiter"], quotechar=q_files["quotechar"])
    header = next(reader)

    questions = [
    inquirer.List('lat',
                    message="Selecione a coluna da latitude",
                    choices=header,
                    default="Latitude"
                ),
    inquirer.List('long',
                    message="Selecione a coluna da latitude",
                    choices=header,
                    default="Longitude"
                ),
    ]

    q_fields = inquirer.prompt(questions)
    lat_index = header.index(q_fields["lat"])
    long_index = header.index(q_fields["long"])

    output_csv="output_utm_from_csv.csv"

    
    with open(output_csv, 'w', encoding=q_files["encoding"]) as file_csv:
        writer = csv.writer(file_csv, delimiter=q_files["delimiter"], quotechar=q_files["quotechar"])
        writer.writerow(header)
        for row in reader:
            if lat_index == long_index:
                lat, long = row[lat_index].split(",")
            else:
                lat = row[lat_index]
                long = row[long_index]

            if lat and long:
                lat = float(lat.replace(".", ""))/1000000
                long = float(long.replace(".", ""))/1000000
                print(lat, long)
                lat, long = convert_coord_to_utm(lat, long)
                row[lat_index] = lat
                row.append(long)
                #row[long_index+1] = long

            writer.writerow(row)

    f.close()


if __name__ == "__main__":
    main()
