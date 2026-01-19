"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.LogadoGenerator = void 0;
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
class LogadoGenerator {
    reservedWords = new Set([
        'let', 'const', 'var', 'if', 'else', 'for', 'while', 'function',
        'return', 'parseInt', 'parseFloat', 'prompt', 'alert', 'document',
        'writeln', 'console', 'log', 'typeof', 'instanceof', 'new', 'class'
    ]);
    eventsCache = new Map();
    start(context) {
        console.log('Logado iniciado!');
        // Monitora mudanças em tempo real
        vscode.workspace.onDidChangeTextDocument((event) => {
            if (event.document.languageId === 'javascript') {
                this.handleTextChange(event);
            }
        }, null, context.subscriptions);
        // Salva JSON ao salvar arquivo
        vscode.workspace.onDidSaveTextDocument((document) => {
            if (document.languageId === 'javascript') {
                this.saveJsonFile(document);
            }
        }, null, context.subscriptions);
        vscode.window.showInformationMessage('Logado: Monitorando arquivos .js');
    }
    handleTextChange(event) {
        const document = event.document;
        const fileName = document.fileName;
        event.contentChanges.forEach(change => {
            const changedText = change.text;
            const words = changedText.match(/\b\w+\b/g);
            if (!words)
                return;
            words.forEach(word => {
                if (this.reservedWords.has(word)) {
                    const position = document.positionAt(change.rangeOffset + changedText.indexOf(word));
                    const getFormattedLocalTime = () => {
                        const now = new Date();
                        const pad = (num) => num.toString().padStart(2, '0');
                        return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
                    };
                    const event = {
                        keyword: word,
                        timestamp: getFormattedLocalTime(),
                        file: path.basename(fileName),
                        line: position.line + 1,
                        column: position.character + 1
                    };
                    if (!this.eventsCache.has(fileName)) {
                        this.eventsCache.set(fileName, []);
                    }
                    this.eventsCache.get(fileName).push(event);
                    console.log(`✓ "${word}" em ${event.file}:${event.line}:${event.column}`);
                }
            });
        });
    }
    saveJsonFile(document) {
        console.log('=== SALVANDO JSON ===');
        console.log('Arquivo:', document.fileName);
        try {
            const fileName = document.fileName;
            const jsonFile = fileName.replace(/\.js$/, '.json');
            let events = this.eventsCache.get(fileName) || [];
            if (events.length === 0) {
                console.log('Cache vazio, escaneando arquivo...');
                events = this.scanFullDocument(document);
            }
            console.log(`Total de eventos: ${events.length}`);
            fs.writeFileSync(jsonFile, JSON.stringify(events, null, 2), 'utf-8');
            vscode.window.showInformationMessage(`${events.length} eventos salvos em ${path.basename(jsonFile)}`);
            console.log(`✓ JSON salvo: ${jsonFile}`);
            this.eventsCache.delete(fileName);
        }
        catch (error) {
            console.error('ERRO:', error);
            vscode.window.showErrorMessage(`Erro: ${error}`);
        }
    }
    scanFullDocument(document) {
        const events = [];
        const fileName = path.basename(document.fileName);
        const text = document.getText();
        const lines = text.split('\n');
        console.log(`scaneando ${lines.length} linhas...`);
        lines.forEach((lineText, lineIndex) => {
            const words = lineText.match(/\b\w+\b/g);
            if (!words)
                return;
            words.forEach(word => {
                if (this.reservedWords.has(word)) {
                    const column = lineText.indexOf(word);
                    events.push({
                        keyword: word,
                        timestamp: new Date().toISOString(),
                        file: fileName,
                        line: lineIndex + 1,
                        column: column + 1
                    });
                }
            });
        });
        console.log(`✓ Encontradas ${events.length} palavras reservadas`);
        return events;
    }
}
exports.LogadoGenerator = LogadoGenerator;
function activate(context) {
    console.log('Extensão Logado ativada!');
    const generator = new LogadoGenerator();
    generator.start(context);
}
function deactivate() {
    console.log('Extensão Logado desativada');
}
//# sourceMappingURL=extension.js.map