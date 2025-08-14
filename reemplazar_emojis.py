#!/usr/bin/env python3
"""
Script para reemplazar automáticamente todos los emojis en archivos Python
"""

import os
import re
import glob

def reemplazar_emojis():
    """Reemplazar todos los emojis con texto simple"""
    
    # Mapeo de emojis a texto
    emoji_mapping = {
        '[OK]': '[OK]',
        '[WARN]': '[WARN]',
        '[ERROR]': '[ERROR]',
        '[INIT]': '[INIT]',
        '[DEPS]': '[DEPS]',
        '[DB]': '[DB]',
        '[ZKT]': '[ZKT]',
        '[STATUS]': '[STATUS]',
        '[BUILD]': '[BUILD]',
        '[PATH]': '[PATH]',
        '[TARGET]': '[TARGET]',
        '[FAST]': '[FAST]',
        '[SEARCH]': '[SEARCH]',
        '[SAVE]': '[SAVE]',
        '[REFRESH]': '[REFRESH]',
        '[LOCK]': '[LOCK]',
        '[UNLOCK]': '[UNLOCK]',
        '[USER]': '[USER]',
        '[USERS]': '[USERS]',
        '[SECURE]': '[SECURE]',
        '[CLIPBOARD]': '[CLIPBOARD]',
        '[UI]': '[UI]',
        '[CONFIG]': '[CONFIG]',
        '[LINK]': '[LINK]',
        '[EDIT]': '[EDIT]',
        '[DELETE]': '[DELETE]',
        '[ADD]': '[ADD]',
        '[REMOVE]': '[REMOVE]',
        '[HELP]': '[HELP]',
        '[INFO]': '[INFO]',
        '[TIP]': '[TIP]',
        '[SUCCESS]': '[SUCCESS]',
        '[HOT]': '[HOT]',
        '[COLD]': '[COLD]',
        '[NIGHT]': '[NIGHT]',
        '[DAY]': '[DAY]',
        '[STAR]': '[STAR]',
        '[PREMIUM]': '[PREMIUM]',
        '[WINNER]': '[WINNER]',
        '[MEDAL]': '[MEDAL]',
        '[UP]': '[UP]',
        '[DOWN]': '[DOWN]',
        '[STATUS]': '[CHART]',
        '[TARGET]': '[TARGET]',
        '[CIRCUS]': '[CIRCUS]',
        '[THEATER]': '[THEATER]',
        '[UI]': '[ART]',
        '[MOVIE]': '[MOVIE]',
        '[MUSIC]': '[MUSIC]',
        '[PIANO]': '[PIANO]',
        '[GUITAR]': '[GUITAR]',
        '[TRUMPET]': '[TRUMPET]',
        '[VIOLIN]': '[VIOLIN]',
        '[DRUM]': '[DRUM]',
        '[MIC]': '[MIC]',
        '[HEADPHONES]': '[HEADPHONES]',
        '[RADIO]': '[RADIO]',
        '[TV]': '[TV]',
        '[CAMERA]': '[CAMERA]',
        '[VIDEO]': '[VIDEO]',
        '[TAPE]': '[TAPE]',
        '[CD]': '[CD]',
        '[SAVE]': '[FLOPPY]',
        '[MINIDISC]': '[MINIDISC]',
        '[LAPTOP]': '[LAPTOP]',
        '[DESKTOP]': '[DESKTOP]',
        '[PRINTER]': '[PRINTER]',
        '[KEYBOARD]': '[KEYBOARD]',
        '[MOUSE]': '[MOUSE]',
        '[TRACKBALL]': '[TRACKBALL]',
        '[MINIDISC]': '[MINIDISC]',
        '[SAVE]': '[FLOPPY]',
        '[CD]': '[CD]',
        '[DVD]': '[DVD]',
        '[TAPE]': '[TAPE]',
        '[VIDEO]': '[VIDEO]',
        '[CAMERA]': '[CAMERA]',
        '[TV]': '[TV]',
        '[RADIO]': '[RADIO]',
        '[HEADPHONES]': '[HEADPHONES]',
        '[MIC]': '[MIC]',
        '[DRUM]': '[DRUM]',
        '[VIOLIN]': '[VIOLIN]',
        '[TRUMPET]': '[TRUMPET]',
        '[GUITAR]': '[GUITAR]',
        '[PIANO]': '[PIANO]',
        '[MUSIC]': '[MUSIC]',
        '[MOVIE]': '[MOVIE]',
        '[UI]': '[ART]',
        '[THEATER]': '[THEATER]',
        '[CIRCUS]': '[CIRCUS]',
        '[TARGET]': '[TARGET]',
        '[DOWN]': '[DOWN]',
        '[UP]': '[UP]',
        '[WINNER]': '[WINNER]',
        '[PREMIUM]': '[PREMIUM]',
        '[STAR]': '[STAR]',
        '[DAY]': '[DAY]',
        '[NIGHT]': '[NIGHT]',
        '[COLD]': '[COLD]',
        '[HOT]': '[HOT]',
        '[SUCCESS]': '[SUCCESS]',
        '[TIP]': '[TIP]',
        '[INFO]': '[INFO]',
        '[HELP]': '[HELP]',
        '[REMOVE]': '[REMOVE]',
        '[ADD]': '[ADD]',
        '[DELETE]': '[DELETE]',
        '[EDIT]': '[EDIT]',
        '[LINK]': '[LINK]',
        '[CONFIG]': '[CONFIG]',
        '[UI]': '[UI]',
        '[CLIPBOARD]': '[CLIPBOARD]',
        '[SECURE]': '[SECURE]',
        '[USERS]': '[USERS]',
        '[USER]': '[USER]',
        '[UNLOCK]': '[UNLOCK]',
        '[LOCK]': '[LOCK]',
        '[REFRESH]': '[REFRESH]',
        '[SAVE]': '[SAVE]',
        '[SEARCH]': '[SEARCH]',
        '[FAST]': '[FAST]',
        '[TARGET]': '[TARGET]',
        '[PATH]': '[PATH]',
        '[BUILD]': '[BUILD]',
        '[STATUS]': '[STATUS]',
        '[ZKT]': '[ZKT]',
        '[DB]': '[DB]',
        '[DEPS]': '[DEPS]',
        '[INIT]': '[INIT]',
        '[ERROR]': '[ERROR]',
        '[WARN]': '[WARN]',
        '[OK]': '[OK]'
    }
    
    # Buscar todos los archivos Python
    python_files = glob.glob("*.py")
    
    total_replaced = 0
    files_modified = 0
    
    print("[INFO] Buscando archivos Python con emojis...")
    
    for file_path in python_files:
        try:
            # Leer el archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            replaced_count = 0
            
            # Reemplazar cada emoji
            for emoji, replacement in emoji_mapping.items():
                if emoji in content:
                    content = content.replace(emoji, replacement)
                    replaced_count += content.count(replacement) - original_content.count(replacement)
            
            # Si se hicieron cambios, escribir el archivo
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                files_modified += 1
                total_replaced += replaced_count
                print(f"[OK] {file_path}: {replaced_count} emojis reemplazados")
                
        except Exception as e:
            print(f"[ERROR] Error procesando {file_path}: {e}")
    
    print(f"\n[SUMMARY] Proceso completado:")
    print(f"[INFO] Archivos modificados: {files_modified}")
    print(f"[INFO] Total de emojis reemplazados: {total_replaced}")

if __name__ == "__main__":
    reemplazar_emojis()
