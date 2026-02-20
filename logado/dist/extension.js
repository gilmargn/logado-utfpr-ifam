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
        'let', 'const', 'var', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue',
        'function', 'return', 'new', 'this', 'class', 'try', 'catch', 'finally', 'throw', 'null', 'undefined', 'true', 'false',
        'typeof', 'instanceof', 'console', 'log', 'error', 'warn', 'parseInt', 'parseFloat', 'Number', 'String', 'Boolean', 'Array', 'Object',
        'Math', 'Date', 'JSON', 'push', 'pop', 'shift', 'unshift', 'length', 'forEach', 'map', 'filter', 'reduce', 'indexOf', 'includes',
        'join', 'slice', 'splice', 'charAt', 'concat', 'includes', 'indexOf', 'replace', 'slice', 'split', 'substring', 'toLowerCase',
        'toUpperCase', 'trim', 'prompt', 'alert', 'confirm', 'toFixed', 'toPrecision', 'toString', 'toExponential', 'toLocaleString', 'valueOf',
        'Math', 'floor', 'ceil', 'round', 'random', 'max', 'min', 'abs', 'sqrt', 'pow', 'PI', 'E', 'sin', 'cos', 'tan', 'asin', 'acos',
        'atan', 'atan2', 'exp', 'log', 'log10', 'log2', 'sign', 'trunc', 'cbrt', 'hypot'
    ]);
    eventsCache = new Map();
    start(context) {
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
        vscode.window.showInformationMessage('LOGADO - UTFPR.IFAM', 'OK');
    }
    handleTextChange(event) {
        const document = event.document;
        const fileName = document.fileName;
        event.contentChanges.forEach(change => {
            if (change.text.length > 0) {
                this.processAddedText(document, change);
            }
        });
    }
    processAddedText(document, change) {
        const fileName = document.fileName;
        const addedText = change.text;
        const words = addedText.match(/\b\w+\b/g);
        if (!words)
            return;
        words.forEach(word => {
            if (this.reservedWords.has(word)) {
                const position = document.positionAt(change.rangeOffset + addedText.indexOf(word));
                const event = {
                    keyword: word,
                    timestamp: this.getBrasiliaTime(),
                    file: path.basename(fileName),
                    line: position.line + 1,
                    column: position.character + 1
                };
                if (!this.eventsCache.has(fileName)) {
                    this.eventsCache.set(fileName, []);
                }
                this.eventsCache.get(fileName).push(event);
            }
        });
    }
    getBrasiliaTime() {
        const now = new Date();
        const brasiliaTime = new Date(now.toLocaleString('en-US', {
            timeZone: 'America/Sao_Paulo'
        }));
        const pad = (num) => num.toString().padStart(2, '0');
        return `${brasiliaTime.getFullYear()}-${pad(brasiliaTime.getMonth() + 1)}-${pad(brasiliaTime.getDate())} ${pad(brasiliaTime.getHours())}:${pad(brasiliaTime.getMinutes())}:${pad(brasiliaTime.getSeconds())}`;
    }
    saveJsonFile(document) {
        try {
            const fileName = document.fileName;
            const jsonFile = fileName.replace(/\.js$/, '.json');
            const newEvents = this.eventsCache.get(fileName) || [];
            if (newEvents.length > 0) {
                let allEvents = [];
                if (fs.existsSync(jsonFile)) {
                    const content = fs.readFileSync(jsonFile, 'utf-8');
                    try {
                        allEvents = JSON.parse(content);
                    }
                    catch (e) {
                        // Se JSON corrompido, começa novo
                        console.warn(`JSON corrompido, criando novo: ${jsonFile}`);
                    }
                }
                allEvents.push(...newEvents);
                fs.writeFileSync(jsonFile, JSON.stringify(allEvents, null, 2), 'utf-8');
                this.eventsCache.delete(fileName);
            }
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
                        timestamp: this.getBrasiliaTime(),
                        file: fileName,
                        line: lineIndex + 1,
                        column: column + 1,
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