use rusqlite::{Connection, Result, Row, params};
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use chrono::{DateTime, Utc};
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatSession {
    pub id: String,
    pub title: String,
    pub model: String,
    pub system_prompt: String,
    pub temperature: f32,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatMessage {
    pub id: String,
    pub session_id: String,
    pub role: String,
    pub content: String,
    pub created_at: DateTime<Utc>,
    pub tokens: Option<u32>,
}

pub struct Database {
    connection: Connection,
}

impl Database {
    pub fn new(path: PathBuf) -> Result<Self> {
        let connection = Connection::open(path)?;
        
        connection.pragma_update(None, "foreign_keys", true)?;
        
        connection.execute(
            "CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                model TEXT NOT NULL,
                system_prompt TEXT NOT NULL DEFAULT 'You are a helpful assistant.',
                temperature REAL NOT NULL DEFAULT 0.7,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            )",
            [],
        )?;

        // Check if existing table needs migration
        {
            let mut stmt = connection.prepare("PRAGMA table_info(chat_sessions)")?;
            let columns: Vec<String> = stmt.query_map([], |row| row.get(1))?
                .filter_map(|r| r.ok())
                .collect();
                
            if !columns.contains(&"system_prompt".to_string()) {
                connection.execute("ALTER TABLE chat_sessions ADD COLUMN system_prompt TEXT NOT NULL DEFAULT 'You are a helpful assistant.'", [])?;
            }
            if !columns.contains(&"temperature".to_string()) {
                connection.execute("ALTER TABLE chat_sessions ADD COLUMN temperature REAL NOT NULL DEFAULT 0.7", [])?;
            }
        }

        connection.execute(
            "CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                tokens INTEGER,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
            )",
            [],
        )?;

        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_messages_session ON chat_messages(session_id)",
            [],
        )?;

        Ok(Self { connection })
    }

    pub fn create_session(&self, title: &str, model: &str, system_prompt: &str, temperature: f32) -> Result<ChatSession> {
        let id = Uuid::new_v4().to_string();
        let now = Utc::now().timestamp();
        
        self.connection.execute(
            "INSERT INTO chat_sessions (id, title, model, system_prompt, temperature, created_at, updated_at) 
             VALUES (?, ?, ?, ?, ?, ?, ?)",
            params![id, title, model, system_prompt, temperature, now, now],
        )?;

        Ok(ChatSession {
            id,
            title: title.to_string(),
            model: model.to_string(),
            system_prompt: system_prompt.to_string(),
            temperature,
            created_at: Utc::now(),
            updated_at: Utc::now(),
        })
    }

    pub fn get_session(&self, id: &str) -> Result<Option<ChatSession>> {
        match self.connection.query_row(
            "SELECT id, title, model, system_prompt, temperature, created_at, updated_at FROM chat_sessions WHERE id = ?",
            [id],
            row_to_session,
        ) {
            Ok(session) => Ok(Some(session)),
            Err(rusqlite::Error::QueryReturnedNoRows) => Ok(None),
            Err(e) => Err(e),
        }
    }

    pub fn get_all_sessions(&self) -> Result<Vec<ChatSession>> {
        let mut stmt = self.connection.prepare(
            "SELECT id, title, model, system_prompt, temperature, created_at, updated_at FROM chat_sessions ORDER BY updated_at DESC",
        )?;
        
        let sessions = stmt.query_map([], row_to_session)?
            .filter_map(|r| r.ok())
            .collect();
        
        Ok(sessions)
    }

    pub fn update_session_title(&self, id: &str, title: &str) -> Result<()> {
        let now = Utc::now().timestamp();
        
        self.connection.execute(
            "UPDATE chat_sessions SET title = ?, updated_at = ? WHERE id = ?",
            params![title, now, id],
        )?;
        
        Ok(())
    }

    pub fn update_session_model(&self, id: &str, model: &str) -> Result<()> {
        let now = Utc::now().timestamp();
        
        self.connection.execute(
            "UPDATE chat_sessions SET model = ?, updated_at = ? WHERE id = ?",
            params![model, now, id],
        )?;
        
        Ok(())
    }

    pub fn update_session_params(&self, id: &str, system_prompt: &str, temperature: f32) -> Result<()> {
        let now = Utc::now().timestamp();
        
        self.connection.execute(
            "UPDATE chat_sessions SET system_prompt = ?, temperature = ?, updated_at = ? WHERE id = ?",
            params![system_prompt, temperature, now, id],
        )?;
        
        Ok(())
    }

    pub fn delete_session(&self, id: &str) -> Result<()> {
        self.connection.execute(
            "DELETE FROM chat_sessions WHERE id = ?",
            [id],
        )?;
        
        Ok(())
    }

    pub fn create_message(
        &self,
        session_id: &str,
        role: &str,
        content: &str,
        tokens: Option<u32>,
    ) -> Result<ChatMessage> {
        let id = Uuid::new_v4().to_string();
        let now = Utc::now().timestamp();
        
        self.connection.execute(
            "INSERT INTO chat_messages (id, session_id, role, content, created_at, tokens) 
             VALUES (?, ?, ?, ?, ?, ?)",
            params![id, session_id, role, content, now, tokens],
        )?;
        
        self.connection.execute(
            "UPDATE chat_sessions SET updated_at = ? WHERE id = ?",
            params![now, session_id],
        )?;

        Ok(ChatMessage {
            id,
            session_id: session_id.to_string(),
            role: role.to_string(),
            content: content.to_string(),
            created_at: Utc::now(),
            tokens,
        })
    }

    pub fn get_messages(&self, session_id: &str) -> Result<Vec<ChatMessage>> {
        let mut stmt = self.connection.prepare(
            "SELECT id, session_id, role, content, created_at, tokens 
             FROM chat_messages WHERE session_id = ? ORDER BY created_at ASC",
        )?;
        
        let messages = stmt.query_map(params![session_id], |row| {
            let timestamp: i64 = row.get(4)?;
            Ok(ChatMessage {
                id: row.get(0)?,
                session_id: row.get(1)?,
                role: row.get(2)?,
                content: row.get(3)?,
                created_at: DateTime::from_timestamp(timestamp, 0).unwrap_or_else(Utc::now),
                tokens: row.get(5)?,
            })
        })?
        .filter_map(|r| r.ok())
        .collect();
        
        Ok(messages)
    }

    pub fn delete_messages(&self, session_id: &str) -> Result<()> {
        self.connection.execute(
            "DELETE FROM chat_messages WHERE session_id = ?",
            [session_id],
        )?;
        
        Ok(())
    }
}

fn row_to_session(row: &Row) -> Result<ChatSession> {
    let created_at: i64 = row.get(5)?;
    let updated_at: i64 = row.get(6)?;
    
    Ok(ChatSession {
        id: row.get(0)?,
        title: row.get(1)?,
        model: row.get(2)?,
        system_prompt: row.get(3)?,
        temperature: row.get(4)?,
        created_at: DateTime::from_timestamp(created_at, 0).unwrap_or_else(|| Utc::now()),
        updated_at: DateTime::from_timestamp(updated_at, 0).unwrap_or_else(|| Utc::now()),
    })
}
