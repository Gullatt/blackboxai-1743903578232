const { Pool } = require('pg');

const pool = new Pool({
  user: process.env.DB_USER || 'postgres',
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'school_management',
  password: process.env.DB_PASSWORD || 'postgres',
  port: process.env.DB_PORT || 5432,
});

const connect = async () => {
  try {
    await pool.query('SELECT NOW()');
    console.log('Conexão com PostgreSQL estabelecida');
    return pool;
  } catch (err) {
    throw err;
  }
};

module.exports = {
  connect,
  query: (text, params) => pool.query(text, params),
};