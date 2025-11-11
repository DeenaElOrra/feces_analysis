#!/usr/bin/env python3
import re

# Ler README
with open('README.md', 'r') as f:
    readme = f.read()

# Extrair imagens do README
pattern = r'img:\s*dataset/(.+?)\s+tipo:(\d+)'
new_images = re.findall(pattern, readme)

# Ler CSV atual
with open('labels.csv', 'r') as f:
    existing_lines = f.readlines()

# Criar set de filenames existentes
existing_files = set()
for line in existing_lines[1:]:  # Skip header
    if line.strip():
        existing_files.add(line.split(',')[0])

# Preparar novas linhas
new_lines = []
for filename, tipo in new_images:
    if filename not in existing_files:
        new_lines.append(f"{filename},{tipo}\n")
        print(f"✓ Nova: {filename} (Tipo {tipo})")

# Escrever novo CSV
with open('labels.csv', 'w') as f:
    f.writelines(existing_lines)  # Escrever dados existentes
    f.writelines(new_lines)        # Adicionar novas linhas

print(f"\n✅ Total adicionado: {len(new_lines)} imagens")
print(f"   CSV total agora: {len(existing_lines) + len(new_lines) - 1} imagens")
