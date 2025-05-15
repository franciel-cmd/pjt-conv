from utils.file_line_reader import FileLineReader
import pprint

lines = FileLineReader.read_lines('input_files/SMH05975 (3).035')
header = FileLineReader.parse_header_line(lines[0])
second = FileLineReader.parse_second_line(lines[1])
detalhes = [FileLineReader.parse_third_line(l) for l in lines[2:] if l.strip()]

print('HEADER:')
pprint.pprint(header)
print('\nSEGUNDA LINHA:')
pprint.pprint(second)
print('\nDETALHES:')
for d in detalhes:
    pprint.pprint(d)
