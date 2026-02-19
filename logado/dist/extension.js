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
        // Declaração de variáveis
        'let', 'const', 'var',
        // Estruturas de controle
        'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue',
        // Funções e classes
        'function', 'return', 'new', 'this', 'class',
        // Tratamento de erros
        'try', 'catch', 'finally', 'throw',
        // Valores literais
        'null', 'undefined', 'true', 'false',
        // Operadores
        'typeof', 'instanceof',
        // Console
        'console', 'log', 'error', 'warn',
        // Conversão e parsing
        'parseInt', 'parseFloat', 'Number', 'String', 'Boolean', 'Array', 'Object',
        'Math', 'Date', 'JSON',
        // Array - métodos
        'push', 'pop', 'shift', 'unshift', 'length',
        'forEach', 'map', 'filter', 'reduce',
        'indexOf', 'includes', 'join', 'slice', 'splice',
        // String - métodos
        'charAt', 'concat', 'includes', 'indexOf',
        'replace', 'slice', 'split', 'substring',
        'toLowerCase', 'toUpperCase', 'trim',
        // Interação
        'prompt', 'alert', 'confirm',
        // Number - métodos
        'toFixed', 'toPrecision', 'toString', 'toExponential', 'toLocaleString',
        'valueOf',
        // Math - objeto e métodos
        'Math', 'floor', 'ceil', 'round', 'random', 'max', 'min', 'abs', 'sqrt', 'pow',
        'PI', 'E', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2',
        'exp', 'log', 'log10', 'log2', 'sign', 'trunc', 'cbrt', 'hypot'
    ]);
    eventsCache = new Map();
    sessionId;
    constructor() {
        this.sessionId = new Date().toISOString().slice(0, 10) + '_' +
            Math.random().toString(36).substring(2, 8);
    }
    start(context) {
        // Monitora mudanças
        vscode.workspace.onDidChangeTextDocument((event) => {
            if (event.document.languageId === 'javascript') {
                this.handleTextChange(event);
            }
        }, null, context.subscriptions);
        vscode.workspace.onDidSaveTextDocument((document) => {
            if (document.languageId === 'javascript') {
                this.saveJsonFile(document);
            }
        }, null, context.subscriptions);
        this.showStartupMessage();
    }
    showStartupMessage() {
        vscode.window.showInformationMessage('LOGADO: Coletando rastros acadêmicos para pesquisa', 'OK');
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
                    const event = {
                        keyword: word,
                        timestamp: this.getFormattedLocalTime(),
                        file: path.basename(fileName),
                        line: position.line + 1,
                        column: position.character + 1,
                        sessionId: this.sessionId
                    };
                    if (!this.eventsCache.has(fileName)) {
                        this.eventsCache.set(fileName, []);
                    }
                    this.eventsCache.get(fileName).push(event);
                }
            });
        });
    }
    getFormattedLocalTime() {
        const now = new Date();
        const pad = (num) => num.toString().padStart(2, '0');
        return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
    }
    saveJsonFile(document) {
        try {
            const fileName = document.fileName;
            const jsonFile = fileName.replace(/\.js$/, '.json');
            let events = this.eventsCache.get(fileName) || [];
            if (events.length === 0) {
                events = this.scanFullDocument(document);
            }
            events = events.map(e => ({
                ...e,
                sessionId: e.sessionId || this.sessionId
            }));
            fs.writeFileSync(jsonFile, JSON.stringify(events, null, 2), 'utf-8');
            this.eventsCache.delete(fileName);
        }
        catch (error) {
            vscode.window.showErrorMessage(` LOGADO: Erro ao salvar dados - ${error}`);
            console.error('Erro detalhado:', error);
        }
    }
    scanFullDocument(document) {
        const events = [];
        const fileName = path.basename(document.fileName);
        const text = document.getText();
        const lines = text.split('\n');
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
                        column: column + 1,
                        sessionId: this.sessionId
                    });
                }
            });
        });
        return events;
    }
}
exports.LogadoGenerator = LogadoGenerator;
function activate(context) {
    const generator = new LogadoGenerator();
    generator.start(context);
}
function deactivate() { }
//# sourceMappingURL=extension.js.map