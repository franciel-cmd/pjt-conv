from utils.file_line_reader import FileLineReader
import json

lines = FileLineReader.read_lines('input_files/SMH05975 (3).035')
result = {}
if len(lines) > 0:
    result['header'] = FileLineReader.parse_header_line(lines[0])
if len(lines) > 1:
    result['Designativo'] = FileLineReader.parse_second_line(lines[1])
if len(lines) > 2:
    detalhes = [FileLineReader.parse_third_line(l) for l in lines[2:] if l.strip()]
    result['lançamento'] = detalhes
# Salva JSON
with open('input_files/SMH05975 (3)_atualizado.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
# Gera novo TXT corrigido
lines_corrigidas = []
# Header
h = result['header']
lines_corrigidas.append(f"SM{h['codigo']}{h['qtd_notas']}{h['qtd_lancamento']}{h['nro']}{h['nome']:<45}{h['filler']}\n")
# Designativo
d = result['Designativo']
lines_corrigidas.append(f"00{d['tipo_nota_35']}{d['qtd_lancamento']}{d['codigo_prest']:<14}{d['valor_total_nota']:<13}{d['valor_total_contraste']:<9}{d['tipo_prest']}{d['periodo']}{d['nro_nota']}{d['filler']}\n")
# Lançamentos
for l in result['lançamento']:
    matricula = l.get('matricula', '')
    nro_contrato = l.get('nro_contrato', '')
    dia = l.get('dia', '')
    cod_honorario = l.get('cod_honorario', '')
    qtde = l.get('qtde', '')
    nome = l.get('nome', '')
    arquivo_pdf = l.get('arquivo_pdf', '') if l.get('arquivo_pdf', '') != 'campo Não encontrado' else ''
    numero_linha = l.get('numero_linha', '')
    lines_corrigidas.append(f"{numero_linha}{matricula}{nro_contrato}{dia}{cod_honorario}{qtde}{nome:<43}{arquivo_pdf}\n")
with open('input_files/SMH05975 (3)_corrigido.txt', 'w', encoding='utf-8') as f:
    f.writelines(lines_corrigidas)
print('JSON e TXT corrigido gerados com sucesso!')
