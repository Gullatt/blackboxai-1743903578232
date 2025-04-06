const { query } = require('../db');

module.exports = {
  up: async () => {
    await query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(20) NOT NULL CHECK (role IN ('secretary', 'director', 'teacher')),
        school_id INTEGER,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      );
    `);
    console.log('Tabela users criada com sucesso');
  },
  down: async () => {
    await query('DROP TABLE IF EXISTS users CASCADE');
    console.log('Tabela users removida');
  }
};