const fs = require('fs');
const path = require('path');
const db = require('./db');

async function runMigrations() {
  try {
    // Criar tabela de controle de migrations se não existir
    await db.query(`
      CREATE TABLE IF NOT EXISTS migrations (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE,
        executed_at TIMESTAMP DEFAULT NOW()
      );
    `);

    // Obter migrations já executadas
    const executed = await db.query('SELECT name FROM migrations');
    const executedNames = executed.rows.map(row => row.name);

    // Ler todas as migrations na pasta
    const migrationFiles = fs.readdirSync(__dirname + '/migrations')
      .filter(file => file.endsWith('.js') && file !== 'template.js')
      .sort();

    // Executar cada migration pendente
    for (const file of migrationFiles) {
      if (!executedNames.includes(file)) {
        const migration = require(path.join(__dirname, 'migrations', file));
        console.log(`Executando migration: ${file}`);
        await migration.up();
        await db.query('INSERT INTO migrations (name) VALUES ($1)', [file]);
        console.log(`Migration ${file} concluída`);
      }
    }

    console.log('Todas as migrations foram aplicadas com sucesso!');
  } catch (error) {
    console.error('Erro ao executar migrations:', error);
    process.exit(1);
  }
}

// Executar as migrations
runMigrations();