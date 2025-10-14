#!/bin/env python3

import csv
import shutil
import os
from PIL import Image, ImageFont, ImageDraw
import textwrap
import utm
import inquirer
from os import listdir


def convert_coord_to_utm(lat, long):
    coord_y_utm, coord_x_utm, _, _ = utm.from_latlon(
        lat, long) if lat and long else ("", "", "", "")
    return coord_y_utm, coord_x_utm

def main():
    files = listdir('.')
    csv_files = [f for f in files if f.endswith('.csv')]

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

    output_csv="outpuv.csv"

    
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
