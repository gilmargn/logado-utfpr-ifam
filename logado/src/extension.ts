import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

interface CodeEvent {
  keyword: string;
  timestamp: string;
  file: string;
  line: number;
  column: number;
  sessionId?: string;
}

export class LogadoGenerator {
  private readonly reservedWords = new Set([
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

  private eventsCache = new Map<string, CodeEvent[]>();
  private sessionId: string;

  constructor() {
    this.sessionId = new Date().toISOString().slice(0,10) + '_' + 
                     Math.random().toString(36).substring(2, 8);
  }
  
  start(context: vscode.ExtensionContext) {
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

  private showStartupMessage() {
    vscode.window.showInformationMessage(
      'LOGADO: Coletando rastros acadêmicos para pesquisa', 
      'OK'
    );
  }

  private handleTextChange(event: vscode.TextDocumentChangeEvent) {
    const document = event.document;
    const fileName = document.fileName;

    event.contentChanges.forEach(change => {
      const changedText = change.text;
      const words = changedText.match(/\b\w+\b/g);
      if (!words) return;

      words.forEach(word => {
        if (this.reservedWords.has(word)) {
          const position = document.positionAt(change.rangeOffset + changedText.indexOf(word));
          
          const event: CodeEvent = {
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
          this.eventsCache.get(fileName)!.push(event);
        }
      });
    });
  }

  private getFormattedLocalTime(): string {
    const now = new Date();
    const pad = (num: number) => num.toString().padStart(2, '0');
    return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
  }

  private saveJsonFile(document: vscode.TextDocument) {
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
      
    } catch (error) {
      vscode.window.showErrorMessage(` LOGADO: Erro ao salvar dados - ${error}`);
      console.error('Erro detalhado:', error);
    }
  }

  private scanFullDocument(document: vscode.TextDocument): CodeEvent[] {
    const events: CodeEvent[] = [];
    const fileName = path.basename(document.fileName);
    const text = document.getText();
    const lines = text.split('\n');

    lines.forEach((lineText, lineIndex) => {
      const words = lineText.match(/\b\w+\b/g);
      if (!words) return;

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

export function activate(context: vscode.ExtensionContext) {
  const generator = new LogadoGenerator();
  generator.start(context);
}

export function deactivate() {}