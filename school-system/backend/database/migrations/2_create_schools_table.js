const { query } = require('../db');

module.exports = {
  up: async () => {
    await query(`
      CREATE TABLE IF NOT EXISTS schools (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        address TEXT NOT NULL,
        director_id INTEGER REFERENCES users(id),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      );
    `);
    console.log('Tabela schools criada com sucesso');
  },
  down: async () => {
    await query('DROP TABLE IF EXISTS schools CASCADE');
    console.log('Tabela schools removida');
  }
};