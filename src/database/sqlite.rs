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
        
        connection.pragma_update(None, "foreign_keys", &true)?;
        
        connection.execute(
            "CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                model TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            )",
            [],
        )?;

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

    pub fn create_session(&self, title: &str, model: &str) -> Result<ChatSession> {
        let id = Uuid::new_v4().to_string();
        let now = Utc::now().timestamp();
        
        self.connection.execute(
            "INSERT INTO chat_sessions (id, title, model, created_at, updated_at) 
             VALUES (?, ?, ?, ?, ?)",
            params![id, title, model, now, now],
        )?;

        Ok(ChatSession {
            id,
            title: title.to_string(),
            model: model.to_string(),
            created_at: Utc::now(),
            updated_at: Utc::now(),
        })
    }

    pub fn get_session(&self, id: &str) -> Result<Option<ChatSession>> {
        match self.connection.query_row(
            "SELECT id, title, model, created_at, updated_at FROM chat_sessions WHERE id = ?",
            [id],
            |row| row_to_session(row),
        ) {
            Ok(session) => Ok(Some(session)),
            Err(rusqlite::Error::QueryReturnedNoRows) => Ok(None),
            Err(e) => Err(e),
        }
    }

    pub fn get_all_sessions(&self) -> Result<Vec<ChatSession>> {
        let mut stmt = self.connection.prepare(
            "SELECT id, title, model, created_at, updated_at FROM chat_sessions ORDER BY updated_at DESC",
        )?;
        
        let sessions = stmt.query_map([], |row| row_to_session(row))?
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
                created_at: DateTime::from_timestamp(timestamp, 0).unwrap_or_default(),
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
    let created_at: i64 = row.get(3)?;
    let updated_at: i64 = row.get(4)?;
    
    Ok(ChatSession {
        id: row.get(0)?,
        title: row.get(1)?,
        model: row.get(2)?,
        created_at: DateTime::from_timestamp(created_at, 0).unwrap_or_default(),
        updated_at: DateTime::from_timestamp(updated_at, 0).unwrap_or_default(),
    })
}
