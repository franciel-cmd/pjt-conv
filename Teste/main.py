import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import argparse
import os
import json
from utils.file_line_reader import FileLineReader

def processar_arquivo_035(input_path, output_json, output_txt):
    lines = FileLineReader.read_lines(input_path)
    result = {}
    if len(lines) > 0:
        header = FileLineReader.parse_header_line(lines[0])
        # Corrige SMH no header
        header['SMH'] = 'SMH'
        result['header'] = header

        # Validação e avisos do header
        erros_header = []
        header_numericos = ['codigo', 'qtd_notas', 'qtd_lancamento', 'nro']
        for campo in header_numericos:
            valor = header.get(campo, '')
            if not valor.isdigit():
                erros_header.append(f"Campo '{campo}' deveria conter apenas números, mas contém: '{valor}'")
        # qtd_notas e qtd_lancamento devem ser > 0
        try:
            qtd_notas_int = int(header.get('qtd_notas', '0'))
        except Exception:
            qtd_notas_int = 0
        try:
            qtd_lancamento_int = int(header.get('qtd_lancamento', '0'))
        except Exception:
            qtd_lancamento_int = 0
        if qtd_notas_int <= 0:
            erros_header.append("A quantidade de notas deve ser maior que 0.")
        if qtd_lancamento_int <= 0:
            erros_header.append("A quantidade de lançamentos deve ser maior que 0.")
        # nro não pode ser '00000000'
        if header.get('nro', '') == '00000000':
            erros_header.append("O campo 'nro' não pode ser '00000000'.")
        if erros_header:
            result['erros_header'] = erros_header

    if len(lines) > 1:
        result['segunda_linha'] = FileLineReader.parse_second_line(lines[1])
    
    # Validação e avisos da segunda linha
    erros_segunda_linha = []
    s = result.get('segunda_linha', {})
    # fixo_00 e tipo_nota_35
    if s.get('fixo_00') != '00':
        erros_segunda_linha.append("Campo 'fixo_00' deveria ser '00'.")
    if s.get('tipo_nota_35') != '35':
        erros_segunda_linha.append("Campo 'tipo_nota_35' deveria ser '35'.")
    # qtd_lancamento > 0 e <= 20
    try:
        qtd_lancamento_int = int(s.get('qtd_lancamento', '0'))
    except Exception:
        qtd_lancamento_int = 0
    if qtd_lancamento_int <= 0 or qtd_lancamento_int > 20:
        erros_segunda_linha.append("Campo 'qtd_lancamento' deve ser maior que 0 e menor ou igual a 20.")
    # cod_prest não pode ser apenas zeros
    if s.get('codigo_prest', '').strip('0') == '':
        erros_segunda_linha.append("Campo 'codigo_prest' não pode ser apenas zeros.")
    # valor_total_nota > 0, 11 inteiros e 2 decimais
    vtn = s.get('valor_total_nota', '')
    try:
        vtn_float = float(vtn)
    except Exception:
        vtn_float = 0.0
    if vtn_float <= 0:
        erros_segunda_linha.append("Campo 'valor_total_nota' deve ser maior que 0.")
    if len(vtn) != 13:
        erros_segunda_linha.append("Campo 'valor_total_nota' deve ter 13 dígitos (11 inteiros e 2 decimais).")
    # valor_total_contraste <= valor_total_nota, 7 inteiros e 2 decimais
    vtc = s.get('valor_total_contraste', '')
    try:
        vtc_float = float(vtc)
    except Exception:
        vtc_float = 0.0
    if len(vtc) != 9:
        erros_segunda_linha.append("Campo 'valor_total_contraste' deve ter 9 dígitos (7 inteiros e 2 decimais).")
    if vtc_float > vtn_float:
        erros_segunda_linha.append("Campo 'valor_total_contraste' não pode ser maior que 'valor_total_nota'.")
    # Período: mês/ano válido
    periodo = s.get('periodo', '')
    if len(periodo) == 4:
        try:
            mes = int(periodo[:2])
            ano = int('20' + periodo[2:])
        except Exception:
            mes = 0
            ano = 0
        from datetime import datetime
        now = datetime.now()
        if mes < 1 or mes > 12:
            erros_segunda_linha.append("Campo 'periodo' possui mês inválido.")
        if ano > now.year:
            erros_segunda_linha.append("Campo 'periodo' possui ano no futuro.")
    else:
        erros_segunda_linha.append("Campo 'periodo' deve ter 4 dígitos (MMYY).")
    # nro_nota > 0
    try:
        nro_nota_int = int(s.get('nro_nota', '0'))
    except Exception:
        nro_nota_int = 0
    if nro_nota_int <= 0:
        erros_segunda_linha.append("Campo 'nro_nota' deve ser maior que 0.")
    if erros_segunda_linha:
        result['erros_segunda_linha'] = erros_segunda_linha

    terceira_linhas = []
    honorario_4100 = None
    cod_32200005 = None
    outros_codigos = []
    for idx, line in enumerate(lines[2:], start=3):
        if not line.strip():
            break
        parsed = FileLineReader.parse_third_line(line)
        if parsed['cod_honorario'].startswith('4100'):
            honorario_4100 = parsed
        elif parsed['cod_honorario'] == '32200005':
            cod_32200005 = parsed
        else:
            outros_codigos.append(parsed)
    if not honorario_4100:
        terceira_linhas.append({'cod_honorario': 'campo Não encontrado'})
    else:
        terceira_linhas.append(honorario_4100)
    if cod_32200005:
        soma_qtde = int(cod_32200005['qtde']) if cod_32200005['qtde'].isdigit() else 0
        for item in outros_codigos:
            if item['qtde'].isdigit():
                soma_qtde += int(item['qtde'])
        cod_32200005['qtde'] = str(soma_qtde)
        terceira_linhas.append(cod_32200005)
    elif outros_codigos:
        soma_qtde = 0
        for item in outros_codigos:
            if item['qtde'].isdigit():
                soma_qtde += int(item['qtde'])
        if outros_codigos:
            outros_codigos[0]['qtde'] = str(soma_qtde)
            outros_codigos[0]['cod_honorario'] = '32200005'
            terceira_linhas.append(outros_codigos[0])
    # Ajusta o campo numero_linha para seguir a ordem sequencial 01, 02, 03...
    for idx, item in enumerate(terceira_linhas):
        item['numero_linha'] = f'{idx+1:02d}'
    if terceira_linhas:
        result['linhas_detalhe'] = terceira_linhas
    # Ajuste especial para QTDE do código 32200005
    if 'linhas_detalhe' in result and 'segunda_linha' in result:
        valor_contraste = result['segunda_linha'].get('valor_total_contraste', '')
        try:
            valor_contraste_float = float(valor_contraste)
        except Exception:
            valor_contraste_float = 0.0
        for item in result['linhas_detalhe']:
            if item.get('cod_honorario') == '32200005':
                qtde_calc = valor_contraste_float / 0.0645 if valor_contraste_float else 0
                if qtde_calc < 1:
                    qtde_str = '00001'
                else:
                    qtde_str_raw = str(qtde_calc).replace('.', '').replace(',', '')
                    qtde_str = qtde_str_raw[:5].ljust(5, '0')
                item['qtde'] = qtde_str
    # Corrige qtd_lancamento da segunda linha para refletir a quantidade de linhas de detalhe no JSON também
    if 'segunda_linha' in result and 'linhas_detalhe' in result:
        result['segunda_linha']['qtd_lancamento'] = f"{len(result['linhas_detalhe']):02d}"
    # Calcula quantidade de notas e lançamentos
    qtd_notas = 1 if honorario_4100 else 0
    qtd_lancamento = len(terceira_linhas) - qtd_notas
    result['header']['qtd_notas'] = f'{qtd_notas:04d}'
    result['header']['qtd_lancamento'] = f'{qtd_lancamento:05d}'
    
    # Validação e avisos das linhas de detalhe
    erros_linhas_detalhe = []
    periodo = s.get('periodo', '')
    periodo_mes = int(periodo[:2]) if len(periodo) == 4 and periodo[:2].isdigit() else None
    periodo_ano = int('20' + periodo[2:]) if len(periodo) == 4 and periodo[2:].isdigit() else None
    for idx, d in enumerate(result.get('linhas_detalhe', [])):
        # referência da linha
        try:
            ref = int(d.get('numero_linha', '0'))
        except Exception:
            ref = -1
        if ref != idx + 1 or ref < 1 or ref > 21:
            erros_linhas_detalhe.append(f"Linha {idx+1}: referência da linha deve ser entre 1 e 21 e em sequência após a segunda linha.")
        # matricula
        try:
            matricula = int(d.get('matricula', '0'))
        except Exception:
            matricula = 0
        if matricula <= 999999999999:
            erros_linhas_detalhe.append(f"Linha {idx+1}: matricula deve ser maior que 999999999999.")
        # dia
        dia = d.get('dia', '')
        if periodo_mes and periodo_ano:
            try:
                dia_int = int(dia)
            except Exception:
                dia_int = 0
            import calendar
            dias_mes = calendar.monthrange(periodo_ano, periodo_mes)[1] if periodo_mes and periodo_ano else 31
            if dia_int < 1 or dia_int > dias_mes:
                erros_linhas_detalhe.append(f"Linha {idx+1}: dia '{dia}' não pertence ao período informado.")
        # qtde
        try:
            qtde = float(d.get('qtde', '0'))
        except Exception:
            qtde = 0
        if qtde <= 0:
            erros_linhas_detalhe.append(f"Linha {idx+1}: qtde deve ser maior que 0.")
        # nome
        nome = d.get('nome', '').strip()
        if not nome:
            erros_linhas_detalhe.append(f"Linha {idx+1}: nome não pode ser vazio ou apenas espaços em branco.")
        # arquivo_pdf
        arquivo_pdf = d.get('arquivo_pdf', '').strip()
        if arquivo_pdf:
            if not arquivo_pdf.lower().endswith('.pdf'):
                erros_linhas_detalhe.append(f"Linha {idx+1}: nome do arquivo PDF deve conter a extensão .pdf.")
            else:
                # Verifica tamanho do arquivo PDF se existir
                import os
                pdf_path = os.path.join(os.path.dirname(input_path), arquivo_pdf)
                if os.path.isfile(pdf_path):
                    tamanho_kb = os.path.getsize(pdf_path) / 1024
                    if tamanho_kb > 500:
                        erros_linhas_detalhe.append(f"Linha {idx+1}: arquivo PDF excede 500kb.")
    if erros_linhas_detalhe:
        result['erros_linhas_detalhe'] = erros_linhas_detalhe

    # Salva resultado em arquivo JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    # Gera arquivo TXT no layout original
    txt_lines = []
    h = result['header']
    txt_lines.append(f"{h['SMH']}{h['codigo']}{h['qtd_notas']}{h['qtd_lancamento']}{h['nro']}{h['nome']:<45}{h['filler']}\n")
    s = result['segunda_linha']
    # Corrige qtd_lancamento da segunda linha para refletir a quantidade de linhas de detalhe
    qtd_lancamento_txt = f"{len(result['linhas_detalhe']):02d}"
    txt_lines.append(f"00{s['tipo_nota_35']}{qtd_lancamento_txt}{s['codigo_prest']:<14}{s['valor_total_nota']:<13}{s['valor_total_contraste']:<9}{s['tipo_prest']}{s['periodo']}{s['nro_nota']}{s['filler']}\n")
    for idx, d in enumerate(result['linhas_detalhe']):
        tipo = 'Nota' if idx == 0 else 'lançamento'
        result['linhas_detalhe'][idx]['tipo'] = tipo
        numero_linha = d.get('numero_linha', '')
        matricula = d.get('matricula', '')
        nro_contrato = d.get('nro_contrato', '')
        dia = d.get('dia', '')
        cod_honorario = d.get('cod_honorario', '')
        qtde = d.get('qtde', '')
        nome = d.get('nome', '')
        arquivo_pdf = d.get('arquivo_pdf', '') if d.get('arquivo_pdf', '') != 'campo Não encontrado' else ''
        txt_lines.append(f"{numero_linha}{matricula}{nro_contrato}{dia}{cod_honorario}{qtde}{nome:<43}{arquivo_pdf}\n")
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.writelines(txt_lines)

def main():
    parser = argparse.ArgumentParser(description='Conversor de arquivos entre layouts (CSV, JSON, etc.)')
    parser.add_argument('--input', required=True, help='Arquivo de entrada')
    parser.add_argument('--from', dest='from_format', required=True, help='Formato de entrada (csv, json, etc.)')
    parser.add_argument('--to', dest='to_format', required=True, help='Formato de saída (csv, json, etc.)')
    parser.add_argument('--output', required=True, help='Arquivo de saída')
    parser.add_argument('--parse', dest='parse', action='store_true', help='Executa apenas o parser das linhas do arquivo de entrada')
    parser.add_argument('--processar_035', dest='processar_035', action='store_true', help='Processa arquivo .035 e gera JSON e TXT atualizados')
    args = parser.parse_args()

    if args.parse:
        lines = FileLineReader.read_lines(args.input)
        result = {}
        if len(lines) > 0:
            result['header'] = FileLineReader.parse_header_line(lines[0])
        if len(lines) > 1:
            result['segunda_linha'] = FileLineReader.parse_second_line(lines[1])
        
        # Validação e avisos da segunda linha
        erros_segunda_linha = []
        s = result.get('segunda_linha', {})
        # fixo_00 e tipo_nota_35
        if s.get('fixo_00') != '00':
            erros_segunda_linha.append("Campo 'fixo_00' deveria ser '00'.")
        if s.get('tipo_nota_35') != '35':
            erros_segunda_linha.append("Campo 'tipo_nota_35' deveria ser '35'.")
        # qtd_lancamento > 0 e <= 20
        try:
            qtd_lancamento_int = int(s.get('qtd_lancamento', '0'))
        except Exception:
            qtd_lancamento_int = 0
        if qtd_lancamento_int <= 0 or qtd_lancamento_int > 20:
            erros_segunda_linha.append("Campo 'qtd_lancamento' deve ser maior que 0 e menor ou igual a 20.")
        # cod_prest não pode ser apenas zeros
        if s.get('codigo_prest', '').strip('0') == '':
            erros_segunda_linha.append("Campo 'codigo_prest' não pode ser apenas zeros.")
        # valor_total_nota > 0, 11 inteiros e 2 decimais
        vtn = s.get('valor_total_nota', '')
        try:
            vtn_float = float(vtn)
        except Exception:
            vtn_float = 0.0
        if vtn_float <= 0:
            erros_segunda_linha.append("Campo 'valor_total_nota' deve ser maior que 0.")
        if len(vtn) != 13:
            erros_segunda_linha.append("Campo 'valor_total_nota' deve ter 13 dígitos (11 inteiros e 2 decimais).")
        # valor_total_contraste <= valor_total_nota, 7 inteiros e 2 decimais
        vtc = s.get('valor_total_contraste', '')
        try:
            vtc_float = float(vtc)
        except Exception:
            vtc_float = 0.0
        if len(vtc) != 9:
            erros_segunda_linha.append("Campo 'valor_total_contraste' deve ter 9 dígitos (7 inteiros e 2 decimais).")
        if vtc_float > vtn_float:
            erros_segunda_linha.append("Campo 'valor_total_contraste' não pode ser maior que 'valor_total_nota'.")
        # Período: mês/ano válido
        periodo = s.get('periodo', '')
        if len(periodo) == 4:
            try:
                mes = int(periodo[:2])
                ano = int('20' + periodo[2:])
            except Exception:
                mes = 0
                ano = 0
            from datetime import datetime
            now = datetime.now()
            if mes < 1 or mes > 12:
                erros_segunda_linha.append("Campo 'periodo' possui mês inválido.")
            if ano > now.year:
                erros_segunda_linha.append("Campo 'periodo' possui ano no futuro.")
        else:
            erros_segunda_linha.append("Campo 'periodo' deve ter 4 dígitos (MMYY).")
        # nro_nota > 0
        try:
            nro_nota_int = int(s.get('nro_nota', '0'))
        except Exception:
            nro_nota_int = 0
        if nro_nota_int <= 0:
            erros_segunda_linha.append("Campo 'nro_nota' deve ser maior que 0.")
        if erros_segunda_linha:
            result['erros_segunda_linha'] = erros_segunda_linha

        terceira_linhas = []
        honorario_4100 = None
        cod_32200005 = None
        outros_codigos = []
        for idx, line in enumerate(lines[2:], start=3):
            if not line.strip():
                break
            parsed = FileLineReader.parse_third_line(line)
            if parsed['cod_honorario'].startswith('4100'):
                honorario_4100 = parsed
            elif parsed['cod_honorario'] == '32200005':
                cod_32200005 = parsed
            else:
                outros_codigos.append(parsed)
        if not honorario_4100:
            terceira_linhas.append({'cod_honorario': 'campo Não encontrado'})
        else:
            terceira_linhas.append(honorario_4100)
        if cod_32200005:
            soma_qtde = int(cod_32200005['qtde']) if cod_32200005['qtde'].isdigit() else 0
            for item in outros_codigos:
                if item['qtde'].isdigit():
                    soma_qtde += int(item['qtde'])
            cod_32200005['qtde'] = str(soma_qtde)
            terceira_linhas.append(cod_32200005)
        elif outros_codigos:
            soma_qtde = 0
            for item in outros_codigos:
                if item['qtde'].isdigit():
                    soma_qtde += int(item['qtde'])
            if outros_codigos:
                outros_codigos[0]['qtde'] = str(soma_qtde)
                outros_codigos[0]['cod_honorario'] = '32200005'
                terceira_linhas.append(outros_codigos[0])
        # Ajusta o campo numero_linha para seguir a ordem sequencial 01, 02, 03...
        for idx, item in enumerate(terceira_linhas):
            item['numero_linha'] = f'{idx+1:02d}'
        if terceira_linhas:
            result['linhas_detalhe'] = terceira_linhas
        # Ajuste especial para QTDE do código 32200005
        if 'linhas_detalhe' in result and 'segunda_linha' in result:
            valor_contraste = result['segunda_linha'].get('valor_total_contraste', '')
            try:
                valor_contraste_float = float(valor_contraste)
            except Exception:
                valor_contraste_float = 0.0
            for item in result['linhas_detalhe']:
                if item.get('cod_honorario') == '32200005':
                    qtde_calc = valor_contraste_float / 0.0645 if valor_contraste_float else 0
                    if qtde_calc < 1:
                        qtde_str = '00001'
                    else:
                        qtde_str_raw = str(qtde_calc).replace('.', '').replace(',', '')
                        qtde_str = qtde_str_raw[:5].ljust(5, '0')
                    item['qtde'] = qtde_str
        # Corrige qtd_lancamento da segunda linha para refletir a quantidade de linhas de detalhe no JSON também
        if 'segunda_linha' in result and 'linhas_detalhe' in result:
            result['segunda_linha']['qtd_lancamento'] = f"{len(result['linhas_detalhe']):02d}"
        # Salva resultado em arquivo JSON
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        import pprint
        pprint.pprint(result)
        return

    if args.processar_035:
        processar_arquivo_035(args.input, args.output + '.json', args.output + '.txt')
        return

    print('Conversão não suportada ainda.')

if __name__ == '__main__':
    main()
