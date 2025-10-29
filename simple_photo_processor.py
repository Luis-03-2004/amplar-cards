#!/usr/bin/env python3

import os
import glob
from PIL import Image, ImageOps

def get_image_orientation(image):
    """
    Detecta a orientação da imagem baseado nas dimensões de pixel.
    Retorna 'landscape' ou 'portrait'.
    """
    width, height = image.size
    return 'landscape' if width > height else 'portrait'

def find_closest_landscape_template(photo_width, photo_height, landscape_templates):
    """
    Encontra o template landscape mais próximo em tamanho.
    Retorna o caminho do template mais próximo.
    """
    photo_area = photo_width * photo_height
    best_template = None
    min_difference = float('inf')
    
    for template_path in landscape_templates:
        try:
            template = Image.open(template_path)
            template_width, template_height = template.size
            template_area = template_width * template_height
            
            # Calcular diferença percentual de área
            area_difference = abs(template_area - photo_area) / photo_area
            
            if area_difference < min_difference:
                min_difference = area_difference
                best_template = template_path
                
        except Exception as e:
            print(f"  Aviso: Erro ao analisar template {template_path}: {e}")
            continue
    
    return best_template

def process_photos(input_folder, output_folder, landscape_templates, portrait_template):
    """
    Processa todas as fotos .jpg de uma pasta e aplica templates baseado na orientação.
    
    Args:
        input_folder: Pasta com as fotos originais
        output_folder: Pasta onde salvar as fotos processadas
        landscape_templates: Lista de caminhos para templates paisagem
        portrait_template: Caminho para o template retrato
    """
    
    # Criar pasta de saída se não existir
    os.makedirs(output_folder, exist_ok=True)
    
    # Buscar todas as fotos .jpg na pasta
    photo_pattern = os.path.join(input_folder, "*.jpg")
    photos = glob.glob(photo_pattern)
    
    print(f"Encontradas {len(photos)} fotos para processar...")
    
    processed_count = 0
    
    for photo_path in photos:
        try:
            # Obter nome do arquivo sem extensão
            photo_name = os.path.splitext(os.path.basename(photo_path))[0]
            
            # Abrir a foto e normalizar orientação via EXIF
            photo = Image.open(photo_path)
            photo = ImageOps.exif_transpose(photo)
            photo_width, photo_height = photo.size
            
            # Detectar orientação real considerando EXIF
            orientation = get_image_orientation(photo)
            
            print(f"Processando: {photo_name} ({photo_width}x{photo_height}) - Orientação: {orientation}")
            
            # Determinar template baseado na orientação real
            if orientation == 'landscape':
                # Paisagem - encontrar template mais próximo
                template_path = find_closest_landscape_template(photo_width, photo_height, landscape_templates)
                if template_path is None:
                    print(f"  Erro: Nenhum template landscape encontrado!")
                    continue
                template_name = f"paisagem ({os.path.basename(template_path)})"
            else:
                # Retrato - usar template único
                template_path = portrait_template
                template_name = "retrato"
            
            # Abrir template
            template = Image.open(template_path)
            template_width, template_height = template.size
            
            print(f"  Usando template {template_name}: {template_width}x{template_height}")
            
            # Redimensionar foto para ocupar 100% do template (pode cortar partes)
            # Manter proporção mas preencher todo o template
            scale_factor = max(template_width / photo_width, template_height / photo_height)
            new_width = int(photo_width * scale_factor)
            new_height = int(photo_height * scale_factor)

            # Redimensionar foto mantendo proporção
            resized_photo = photo.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Calcular posição para centralizar (pode cortar bordas)
            x_offset = (template_width - new_width) // 2
            y_offset = (template_height - new_height) // 2

            # Criar imagem final com as dimensões do template
            final_image = Image.new('RGB', (template_width, template_height))
            
            # Colar foto como fundo (100% do template)
            final_image.paste(resized_photo, (x_offset, y_offset))
            
            # Colar template por cima da foto (overlay)
            final_image.paste(template, (0, 0), template)
            
            # Salvar resultado
            output_path = os.path.join(output_folder, f"{photo_name}_processed.png")
            final_image.save(output_path)
            
            print(f"  Salvo: {output_path}")
            processed_count += 1
            
        except Exception as e:
            print(f"Erro ao processar {photo_path}: {e}")
            continue
    
    print(f"\nProcessamento concluído! {processed_count} fotos processadas com sucesso.")

def main():
    # Configurações
    input_folder = "Images\Amparo"
    output_folder = "Images\fotos_processadas"
    
    # Lista de templates landscape (adicione quantos quiser)
    landscape_templates = [
        "Refloresta  (3672 x 2066 px).png",
        "Refloresta (1600 x 721 px).png"
        # Adicione mais templates landscape aqui conforme necessário
    ]
    
    portrait_template = "Refloresta (3024 x 4032 px).png"
    
    # Verificar se os arquivos existem
    if not os.path.exists(input_folder):
        print(f"Erro: Pasta '{input_folder}' não encontrada!")
        return
    
    # Verificar templates landscape
    valid_landscape_templates = []
    for template in landscape_templates:
        if os.path.exists(template):
            valid_landscape_templates.append(template)
            print(f"✓ Template landscape encontrado: {template}")
        else:
            print(f"⚠ Template landscape não encontrado: {template}")
    
    if not valid_landscape_templates:
        print("Erro: Nenhum template landscape válido encontrado!")
        return
    
    if not os.path.exists(portrait_template):
        print(f"Erro: Template retrato '{portrait_template}' não encontrado!")
        return
    
    print(f"✓ Template retrato encontrado: {portrait_template}")
    print(f"Total de templates landscape: {len(valid_landscape_templates)}")
    print()
    
    # Processar fotos
    process_photos(input_folder, output_folder, valid_landscape_templates, portrait_template)

if __name__ == "__main__":
    main()
