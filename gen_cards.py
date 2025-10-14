#!/bin/env python3

import csv
import shutil
import os
from PIL import Image, ImageFont, ImageDraw
import textwrap
import utm
import inquirer
from os import listdir

# wrap and replace code like
# card_img.text((660,92), nome_pop, color, font=font)
def wrap_text(card_img, text, font, offset, width=53):
    lines = textwrap.wrap(text, width=width)
    x_text, y_text = offset
    for line in lines:
        #width, height = font.getsize(line)
        bbox = font.getbbox(line)
        width, height = bbox[2], bbox[3]
        card_img.text((x_text, y_text), line, (0, 0, 0), font=font)
        y_text += height

def convert_coord_to_utm(lat, long):
    coord_y_utm, coord_x_utm, _, _ = utm.from_latlon(
        float(lat.replace(",", ".")), float(long.replace(",", "."))) if lat and long else ("", "", "", "")
    return coord_y_utm, coord_x_utm

def generate_card(template_file, pictures_folder, nome, nome_pop, nome_cien, lat, long, foto, convert_to_utm, output_folder):
    if not foto:
        return

    template = Image.open(template_file)
    card_img = ImageDraw.Draw(template)
    font = ImageFont.truetype("liberation2/LiberationMono-Regular.ttf", 10)
    font_header = ImageFont.truetype("liberation2/LiberationMono-Regular.ttf", 8)
    foto_path = os.path.join(pictures_folder, foto)
    if (not os.path.isfile(foto_path)):
        print(f"ERROR: foto {foto_path} doesn't exist")
        return

    right_margin = 27
    foto_img = Image.open(foto_path).resize((330-right_margin, 445-50))
    template.paste(foto_img, (right_margin, 50))

    line_height = 46/2
    inicial_line = 468-18

    wrap_text(card_img, "Nome popular:", font_header, (right_margin, 3+inicial_line))
    wrap_text(card_img, "    " + nome_pop, font, (right_margin, inicial_line + line_height))
    wrap_text(card_img, "Nome científico:", font_header, (right_margin, 3+inicial_line + 2*line_height))
    wrap_text(card_img, "    " + nome_cien, font, (right_margin, inicial_line + 3*line_height))
    wrap_text(card_img, "Coordenadas:", font_header, (right_margin, 3+inicial_line + 4*line_height))
    if (convert_to_utm):
        lat, long = convert_coord_to_utm(lat, long)
        lat = round(lat, 2)
        long = round(long, 2)
    coord = f"Long {lat}; Lat {long}"
    wrap_text(card_img, "    " + coord, font, (right_margin, inicial_line + 5*line_height))

    output = os.path.join(output_folder, nome + ".png")
    template.save(output)
    print(output)

def main():
    files = listdir('.')
    csv_files = [f for f in files if f.endswith('.csv')]
    image_files = [f for f in files if f.endswith('.png') or f.endswith('.jpg') or f.endswith('.jpeg')]
    folders = [f for f in files if os.path.isdir(f)]
    folders.insert(0, ".")

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
    inquirer.List('template',
                    message="Selecione o arquivo template",
                    choices=image_files,
                    default="template.png"
                ),
    inquirer.List('pictures_folder',
                    message="Selecione a pasta das imagens",
                    choices=folders,
                    default="."
                ),
    ]
    q_files = inquirer.prompt(questions)

    f = open(q_files["csvfile"])
    reader = csv.reader(f, delimiter=q_files["delimiter"], quotechar=q_files["quotechar"])
    header = next(reader)

    questions = [
    inquirer.List('parcela',
                    message="Selecione a coluna da parcela",
                    choices=header,
                    default="Parcela"
                ),
    inquirer.List('nome_pop',
                    message="Selecione a coluna do nome popular",
                    choices=header,
                    default="Nome popular"
                ),
    inquirer.List('nome_cien',
                    message="Selecione a coluna do nome científico",
                    choices=header,
                    default="Nome cientifico"
                ),
    inquirer.Checkbox('fotos',
                    message="Selecione a(s) coluna(s) da(s) foto(s)",
                    choices=header,
                    default=["Foto 1", "Foto 2", "Foto 3", "Foto 4", "Foto 5", "Foto 6"]
                ),
    inquirer.List('lat',
                    message="Selecione a coluna do latitute",
                    choices=header,
                    default="Latitude"
                ),
    inquirer.List('long',
                    message="Selecione a coluna do longitude (NOTA: selecione a mesma coluna na latitude se eles estão no mesmo campo)",
                    choices=header,
                    default="Longitude"
                ),
    inquirer.Confirm('convert_to_utm',
                     message="Converter coordenadas para UTM?" ,
                     default=False),
    ]

    q_fields = inquirer.prompt(questions)
    field_indexes = {
        "parcela": header.index(q_fields["parcela"]),
        "nome_pop": header.index(q_fields["nome_pop"]),
        "nome_cien": header.index(q_fields["nome_cien"]),
        "lat": header.index(q_fields["lat"]),
        "long": header.index(q_fields["long"]),
        "fotos": [header.index(foto) for foto in q_fields["fotos"]]
    }

    # TODO: maybe ask if we should remove existing folder?
    #if (args.rm):
    #    shutil.rmtree(args.output_folder, ignore_errors=True)

    #if (os.path.isdir(args.output_folder)):
    #    raise Exception(f"Folder {args.output_folder} already exist")

    output_folder="results"
    shutil.rmtree(output_folder, ignore_errors=True)
    os.mkdir(output_folder)

    generate_cards(reader, q_files["pictures_folder"],
                   q_files["template"], field_indexes, q_fields['convert_to_utm'], output_folder)

    f.close()


def generate_cards(reader, pictures_folder, template, field_indexes, convert_to_utm, output_folder):
    i = 0
    for row in reader:
        i += 1

        parcela = row[field_indexes["parcela"]]
        nome_pop = row[field_indexes["nome_pop"]]
        nome_cien = row[field_indexes["nome_cien"]]
        fotos = [row[foto_idx] for foto_idx in field_indexes["fotos"]]

        # TODO if they have the same index
        # coord_y, coord_x = coord.split(", ") if coord else ("", "")
        if field_indexes["lat"] == field_indexes["long"]:
            coord = row[field_indexes["lat"]]
            lat, long = coord.split(", ") if coord else ("", "")
        else:
            lat = row[field_indexes["lat"]]
            long = row[field_indexes["long"]]

        for j in range(len(fotos)):
            nome = f'{i}_{parcela}_foto{j+1}'
            generate_card(template, pictures_folder, nome, nome_pop, nome_cien, lat, long, fotos[j], convert_to_utm, output_folder)


if __name__ == "__main__":
    main()
