import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export function activate(context: vscode.ExtensionContext) {
    console.log('Logado está ativo!');

    // Verifica se a configuração já foi feita
    const config = context.globalState.get<{ codigoEscola: string; matricula: string; github: string }>('userConfig');
    if (!config) {
        // Mostra a tela inicial se a configuração não foi feita
        showInitialForm(context);
        return;
    }

    // Inicializa o plugin com as configurações salvas
    initializePlugin(context, config.codigoEscola, config.matricula, config.github);
    vscode.window.showInformationMessage(`Plugin configurado para ${config.github}!`);
    console.log(`Plugin inicializado para ${config.matricula} da escola ${config.codigoEscola} e GitHub ${config.github}`);
}


function showInitialForm(context: vscode.ExtensionContext) {
    const panel = vscode.window.createWebviewPanel(
        'initialForm',
        'Configuração do Plugin',
        vscode.ViewColumn.One,
        {
            enableScripts: true,
            retainContextWhenHidden: true // Mantém o estado da Webview quando oculta
        }
    );

    const htmlPath = path.join(context.extensionPath, 'src', 'webview', 'initialForm.html');
    panel.webview.html = fs.readFileSync(htmlPath, 'utf8');

    panel.webview.onDidReceiveMessage(async (message) => {
        switch (message.command) {
            case 'saveConfig':
                // Salva as configurações
                context.globalState.update('userConfig', {
                    codigoEscola: message.codigoEscola,
                    matricula: message.matricula,
                    github: message.github
                });

                vscode.window.showInformationMessage('Configuração salva com sucesso!');
                
                // Fecha a Webview atual
                panel.dispose();
                
                // Inicializa o plugin
                initializePlugin(context, message.codigoEscola, message.matricula, message.github);
                
                // Mostra a nova Webview (tela após login)
                await showPostLoginScreen(context, {
                    codigoEscola: message.codigoEscola,
                    matricula: message.matricula,
                    github: message.github
                });
                break;

            case 'alert':
                vscode.window.showErrorMessage(message.text);
                break;
        }
    }, undefined, context.subscriptions);
}

async function showPostLoginScreen(context: vscode.ExtensionContext, config: { codigoEscola: string; matricula: string; github: string }) {
    // Cria e mostra a nova Webview
    const panel = vscode.window.createWebviewPanel(
        'postLoginScreen',
        'Bem-vindo ao Plugin',
        vscode.ViewColumn.One,
        {
            enableScripts: true
        }
    );

    // Carrega o conteúdo HTML da nova tela
    const htmlPath = path.join(context.extensionPath, 'src', 'webview', 'postLogin.html');
    
    // Se quiser, pode passar dados para o HTML (opcional)
    let htmlContent = fs.readFileSync(htmlPath, 'utf8');
    htmlContent = htmlContent.replace('{{github}}', config.github)
                            .replace('{{matricula}}', config.matricula)
                            .replace('{{codigoEscola}}', config.codigoEscola);
    
    panel.webview.html = htmlContent;

    // Processa mensagens da nova tela, se necessário
    panel.webview.onDidReceiveMessage((message) => {
        switch (message.command) {
            case 'doSomething':
                // Lógica para ações na nova tela
                break;
        }
    }, undefined, context.subscriptions);
}

function initializePlugin(context: vscode.ExtensionContext, codigoEscola: string, matricula: string, github: string) {
    // Cria o caminho do arquivo de log
    const logFilePath = path.join(context.extensionPath, `logs/${codigoEscola}_${matricula}_${github}_log.txt`);

    // Exibe uma mensagem de confirmação
    console.log(`Plugin inicializado para ${matricula} da escola ${codigoEscola} e GitHub ${github}`);
    vscode.window.showInformationMessage(`Plugin configurado para ${github}!`);
}

function KeywordCollector(context: vscode.ExtensionContext) {
    console.log('Extension "Logado" agora está ativo!');

    // Lista de palavras reservadas (JavaScript)
    const reservedWords = [
        'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger', 'default',
        'delete', 'do', 'else', 'export', 'extends', 'finally', 'for', 'function', 'if',
        'import', 'in', 'instanceof', 'new', 'return', 'super', 'switch', 'this', 'throw',
        'try', 'typeof', 'var', 'void', 'while', 'with', 'yield'
    ];

    // Delimitadores que indicam limites de palavras
    const delimiters = [
        ';', ',', '[', ']', '(', ')', '{', '}', ' ', '\n', '\t', '\r', '\v', '\f'
    ];

    // Monitora mudanças no documento
    vscode.workspace.onDidChangeTextDocument((event) => {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            const document = editor.document;
            const changes = event.contentChanges;

            changes.forEach(change => {
                const text = change.text.trim();
                const position = change.range.start;

                // Verifica se o texto é uma palavra reservada E está cercada por delimitadores
                if (reservedWords.includes(text) && isSurroundedByDelimiters(document, position, text, delimiters)) {
                    const timestamp = getTimestamp();
                    console.log(`Palavra reservada "${text}" detectada às ${timestamp}`);

                    // Insere o timestamp ao lado da palavra
                    editor.edit(editBuilder => {
                        const timestampPosition = new vscode.Position(position.line, position.character + text.length);
                        editBuilder.insert(timestampPosition, ` ${timestamp}`);
                    });
                }
            });
        }
    });
}

// Função para verificar se a palavra está cercada por delimitadores
function isSurroundedByDelimiters(document: vscode.TextDocument, position: vscode.Position, word: string, delimiters: string[]): boolean {
    const line = document.lineAt(position.line).text;
    const charBefore = line[position.character - 1] || ' ';
    const charAfter = line[position.character + word.length] || ' ';

    return delimiters.includes(charBefore) && delimiters.includes(charAfter);
}

// Função para gerar timestamp
function getTimestamp(): string {
    return `[${new Date().toLocaleTimeString()}]`;
}

export function deactivate() {}