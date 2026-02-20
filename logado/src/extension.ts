import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

interface CodeEvent {
  keyword: string;
  timestamp: string;
  file: string;
  line: number;
  column: number;
}

export class LogadoGenerator {
  private readonly reservedWords = new Set([
    'let', 'const', 'var','if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue',
    'function', 'return', 'new', 'this', 'class','try', 'catch', 'finally', 'throw', 'null', 'undefined', 'true', 'false',
    'typeof', 'instanceof', 'console', 'log', 'error', 'warn','parseInt', 'parseFloat', 'Number', 'String', 'Boolean', 'Array', 'Object',
    'Math', 'Date', 'JSON','push', 'pop', 'shift', 'unshift', 'length','forEach', 'map', 'filter', 'reduce',     'indexOf', 'includes', 
    'join', 'slice', 'splice', 'charAt', 'concat', 'includes', 'indexOf', 'replace', 'slice', 'split', 'substring','toLowerCase', 
    'toUpperCase', 'trim','prompt', 'alert', 'confirm','toFixed', 'toPrecision', 'toString', 'toExponential', 'toLocaleString','valueOf',
    'Math', 'floor', 'ceil', 'round', 'random', 'max', 'min', 'abs', 'sqrt', 'pow','PI', 'E', 'sin', 'cos', 'tan', 'asin', 'acos', 
    'atan', 'atan2', 'exp', 'log', 'log10', 'log2', 'sign', 'trunc', 'cbrt', 'hypot'
  ]);

  private eventsCache = new Map<string, CodeEvent[]>();
  
   start(context: vscode.ExtensionContext) {
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
      'LOGADO - UTFPR.IFAM', 
      'OK'
    );
  }

  private handleTextChange(event: vscode.TextDocumentChangeEvent) {
    const document = event.document;
    const fileName = document.fileName;

    event.contentChanges.forEach(change => {

      if(change.text.length>0){
        this.processAddedText(document,change);
      }
    });
  }
   private processAddedText(document: vscode.TextDocument, change: vscode.TextDocumentContentChangeEvent) {
    const fileName = document.fileName;
    const addedText = change.text;
    const words = addedText.match(/\b\w+\b/g);
    
    if (!words) return;

    words.forEach(word => {
      if (this.reservedWords.has(word)) {
        const position = document.positionAt(change.rangeOffset + addedText.indexOf(word));
        
        const event: CodeEvent = {
          keyword: word,
          timestamp: this.getBrasiliaTime(),
          file: path.basename(fileName),
          line: position.line + 1,
          column: position.character + 1
        };

        if (!this.eventsCache.has(fileName)) {
          this.eventsCache.set(fileName, []);
        }
        this.eventsCache.get(fileName)!.push(event);
      }
    });
  }
  private getBrasiliaTime(): string {
    const now = new Date();
    const brasiliaTime = new Date(now.toLocaleString('en-US', { 
      timeZone: 'America/Sao_Paulo' 
    }));

    const pad = (num: number) => num.toString().padStart(2, '0');
    
    return `${brasiliaTime.getFullYear()}-${pad(brasiliaTime.getMonth() + 1)}-${pad(brasiliaTime.getDate())} ${pad(brasiliaTime.getHours())}:${pad(brasiliaTime.getMinutes())}:${pad(brasiliaTime.getSeconds())}`;
  }

  private saveJsonFile(document: vscode.TextDocument) {
    try {
      const fileName = document.fileName;
      const jsonFile = fileName.replace(/\.js$/, '.json');
      
      const newEvents = this.eventsCache.get(fileName) || [];
      
      if (newEvents.length > 0) {
         let allEvents: CodeEvent[] = [];
      if (fs.existsSync(jsonFile)) {
        const content = fs.readFileSync(jsonFile, 'utf-8');
        try {
          allEvents = JSON.parse(content);
        } catch (e) {
          // Se JSON corrompido, começa novo
          console.warn(`JSON corrompido, criando novo: ${jsonFile}`);
        }
      }

      allEvents.push(...newEvents);
          
      fs.writeFileSync(jsonFile, JSON.stringify(allEvents, null, 2), 'utf-8');
            
      this.eventsCache.delete(fileName);
    }
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

export function activate(context: vscode.ExtensionContext) {
  const generator = new LogadoGenerator();
  generator.start(context);
}

export function deactivate() {}