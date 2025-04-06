const { query } = require('../db');

module.exports = {
  up: async () => {
    await query(`
      CREATE TABLE IF NOT EXISTS students (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(100) NOT NULL,
        birth_date DATE NOT NULL,
        guardians JSONB NOT NULL,
        address TEXT NOT NULL,
        school_id INTEGER NOT NULL REFERENCES schools(id),
        class VARCHAR(50) NOT NULL,
        academic_year VARCHAR(9) NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'active' 
          CHECK (status IN ('active', 'transferred', 'waiting')),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      );
    `);
    console.log('Tabela students criada com sucesso');
  },
  down: async () => {
    await query('DROP TABLE IF EXISTS students CASCADE');
    console.log('Tabela students removida');
  }
};