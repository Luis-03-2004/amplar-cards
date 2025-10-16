import json

texto_do_usuario = """
-46.5658 -21.7892
-43.2096 -22.9035

    -46.6333 -23.5505
-38.5015 -12.9777

-47.8825 -15.7939
-51.2287      -30.0346
-45.123 12.456 99.0
abcde abc
"""

def processar_coordenadas_com_validacao(texto_bruto):
    linhas_brutas = texto_bruto.splitlines()
    coordenadas_validas = []
    
    for linha in linhas_brutas:
        linha_tratada = linha.strip()

        if not linha_tratada:
            continue

        partes = linha_tratada.split()

        if len(partes) == 2:
            try:
                float(partes[0])
                float(partes[1])
                
                linha_padronizada = f"{partes[0]} {partes[1]}"
                coordenadas_validas.append(linha_padronizada)
            except ValueError:
                continue
    
    dados_finais = {
        "coordinates": coordenadas_validas
    }
    
    return dados_finais

dados_processados = processar_coordenadas_com_validacao(texto_do_usuario)

with open('dados_processados.json', 'w') as f:
    json.dump(dados_processados, f, indent=2)
