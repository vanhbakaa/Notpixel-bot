const { Telegraf } = require('telegraf');
const fs = require('fs');
const { exec } = require('child_process');
require('dotenv').config();

const BOT_TOKEN = process.env.BOT_TOKEN;

const bot = new Telegraf(BOT_TOKEN);

bot.start((ctx) => {
    ctx.reply('Hello! Please paste your NotPixel Query ID.');
});

bot.on('text', (ctx) => {
    const inputText = ctx.message.text;
    
    fs.writeFileSync('data.txt', inputText, 'utf8');
    ctx.reply('Running Bot...');

    const command = 'source venv/bin/activate && python3 main.py -a 3';
    const pythonProcess = exec(command, { shell: '/bin/bash' });

    pythonProcess.stdin.write('y\n');
    pythonProcess.stdout.on('data', (data) => {
        ctx.reply(`${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        ctx.reply(`Python Error: ${data}`);
    });

    setTimeout(() => {
        pythonProcess.kill('SIGINT');
        ctx.reply('Bot Stopped after 3 Minutes.');
    }, 180000);
});

bot.launch();
