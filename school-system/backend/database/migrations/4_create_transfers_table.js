const { query } = require('../db');

module.exports = {
  up: async () => {
    await query(`
      CREATE TABLE IF NOT EXISTS transfers (
        id SERIAL PRIMARY KEY,
        student_id INTEGER NOT NULL REFERENCES students(id),
        old_school_id INTEGER NOT NULL REFERENCES schools(id),
        new_school_id INTEGER NOT NULL REFERENCES schools(id),
        transfer_date DATE NOT NULL DEFAULT CURRENT_DATE,
        reason TEXT NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'pending'
          CHECK (status IN ('pending', 'approved', 'rejected')),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      );
    `);
    console.log('Tabela transfers criada com sucesso');
  },
  down: async () => {
    await query('DROP TABLE IF EXISTS transfers CASCADE');
    console.log('Tabela transfers removida');
  }
};