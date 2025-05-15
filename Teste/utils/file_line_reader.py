class FileLineReader:
    """
    Classe utilitária para ler um arquivo e separar as linhas em arrays.
    """
    @staticmethod
    def read_lines(filepath):
        """
        Lê um arquivo e retorna uma lista de linhas (strings).
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return [line.rstrip('\n') for line in f]

    @staticmethod
    def read_lines_as_arrays(filepath, separator=None):
        """
        Lê um arquivo e retorna uma lista de arrays, separando cada linha pelo separador informado.
        Se separator=None, retorna cada linha como um array de caracteres.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            if separator is not None:
                return [line.rstrip('\n').split(separator) for line in f]
            else:
                return [list(line.rstrip('\n')) for line in f]

    @staticmethod
    def parse_header_line(line):
        """
        Recebe uma linha e retorna um dicionário com os campos do header extraídos por posição.
        """
        return {
            'SMH': line[0:3],
            'codigo': line[3:17].strip(),
            'qtd_notas': line[17:21].strip(),
            'qtd_lancamento': line[21:26].strip(),
            'nro': line[26:34].strip(),
            'nome': line[34:79].strip(),
            'filler': line[79:].rstrip()
        }

    @staticmethod
    def parse_second_line(line):
        """
        Recebe a segunda linha e retorna um dicionário com os campos extraídos por posição (ajustado conforme especificação).
        """
        return {
            'fixo_00': line[0:2],
            'tipo_nota_35': line[2:4],
            'qtd_lancamento': line[4:6],
            'codigo_prest': line[6:20].strip(),
            'valor_total_nota': line[20:33].strip(),
            'valor_total_contraste': line[33:42].strip(),
            'tipo_prest': line[42:44].strip(),
            'periodo': line[44:48].strip(),
            'nro_nota': line[48:53].strip(),
            'filler': line[53:81].rstrip()
        }

    @staticmethod
    def parse_third_line(line):
        """
        Recebe a terceira linha e retorna um dicionário com os campos extraídos por posição.
        Se algum campo obrigatório estiver vazio, preenche com 'campo Não encontrado'.
        """
        result = {
            'numero_linha': line[0:2].strip(),
            'matricula': line[2:15].strip(),
            'nro_contrato': line[15:23].strip(),
            'dia': line[23:25].strip(),
            'cod_honorario': line[25:33].strip(),
            'qtde': line[33:38].strip(),
            'nome': line[38:81].strip(),
            'arquivo_pdf': line[81:131].strip()
        }
        for campo, valor in result.items():
            if not valor:
                result[campo] = 'campo Não encontrado'
        # Verifica se arquivo_pdf termina com .PDF, se não, também marca como não encontrado
        if result['arquivo_pdf'] != 'campo Não encontrado' and not result['arquivo_pdf'].upper().endswith('.PDF'):
            result['arquivo_pdf'] = 'campo Não encontrado'
        return result

    @staticmethod
    def parse_header_from_file(filepath):
        """
        Lê o primeiro header do arquivo informado e retorna o dicionário extraído.
        """
        lines = FileLineReader.read_lines(filepath)
        if not lines:
            return None
        return FileLineReader.parse_header_line(lines[0])
