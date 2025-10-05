# database.py
import sqlite3
import json
import os
from datetime import datetime

DB_NAME = "mydatabase.db"

def init_db():
    """Inicializa o banco de dados e cria a tabela se não existir."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_sessions (
            session_id TEXT PRIMARY KEY,
            file_name TEXT NOT NULL,
            start_time TEXT NOT NULL,
            last_update TEXT NOT NULL,
            messages_json TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_session(file_name, messages):
    """
    Salva ou atualiza a sessão associada a um arquivo.
    Usa o nome do arquivo como ID da sessão.
    """
    session_id = f"session_{hash(file_name) % (10**8)}"  # ID simples baseado no nome
    now = datetime.now().isoformat()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO analysis_sessions 
            (session_id, file_name, start_time, last_update, messages_json)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, file_name, now, now, json.dumps(messages)))
        conn.commit()
    except Exception as e:
        print(f"[Erro DB] Falha ao salvar sessão: {e}")
    finally:
        conn.close()

def load_session_by_filename(file_name):
    """
    Carrega o histórico de mensagens para um arquivo específico.
    Retorna None se não houver.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT messages_json FROM analysis_sessions
            WHERE file_name = ?
        ''', (file_name,))
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None
    except Exception as e:
        print(f"[Erro DB] Falha ao carregar sessão: {e}")
        return None
    finally:
        conn.close()

def list_all_sessions():
    """
    Retorna uma lista de todas as sessões salvas, ordenadas pela última atualização.
    Cada item é uma tupla: (file_name, start_time, last_update)
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT session_id, file_name, start_time, last_update
            FROM analysis_sessions
            ORDER BY last_update DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"[Erro] Falha em list_all_sessions: {e}")
        return []