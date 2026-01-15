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
    'let', 'const', 'var', 'if', 'else', 'for', 'while', 'function',
    'return', 'parseInt', 'parseFloat', 'prompt', 'alert', 'document', 
    'writeln', 'console', 'log', 'typeof', 'instanceof', 'new', 'class'
  ]);

  private eventsCache = new Map<string, CodeEvent[]>();

  start(context: vscode.ExtensionContext) {
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
            timestamp: new Date().toISOString(),
            file: path.basename(fileName),
            line: position.line + 1,
            column: position.character + 1
          };

          if (!this.eventsCache.has(fileName)) {
            this.eventsCache.set(fileName, []);
          }
          this.eventsCache.get(fileName)!.push(event);

          console.log(`✓ "${word}" em ${event.file}:${event.line}:${event.column}`);
        }
      });
    });
  }

  private saveJsonFile(document: vscode.TextDocument) {
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
      
      vscode.window.showInformationMessage(`✓ ${events.length} eventos salvos em ${path.basename(jsonFile)}`);
      console.log(`✓ JSON salvo: ${jsonFile}`);
      
      this.eventsCache.delete(fileName);
      
    } catch (error) {
      console.error('ERRO:', error);
      vscode.window.showErrorMessage(`Erro: ${error}`);
    }
  }

  private scanFullDocument(document: vscode.TextDocument): CodeEvent[] {
    const events: CodeEvent[] = [];
    const fileName = path.basename(document.fileName);
    const text = document.getText();
    const lines = text.split('\n');

    console.log(`scaneando ${lines.length} linhas...`);

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
            column: column + 1
          });
        }
      });
    });

    console.log(`✓ Encontradas ${events.length} palavras reservadas`);
    return events;
  }
}

export function activate(context: vscode.ExtensionContext) {
  console.log('Extensão Logado ativada!');
  const generator = new LogadoGenerator();
  generator.start(context);
}

export function deactivate() {
  console.log('Extensão Logado desativada');
}