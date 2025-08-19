(function () {
    const vscode = acquireVsCodeApi();

    document.getElementById('configForm').addEventListener('submit', (event) => {
        event.preventDefault();

        const codigoEscola = document.getElementById('codigoEscola').value;
        const matricula = document.getElementById('matricula').value;
        const github = document.getElementById('github').value;
        const aceito = document.getElementById('aceito').checked;

        if (!codigoEscola || !matricula || !github || !aceito) {
            vscode.postMessage({
                command: 'alert',
                text: 'Por favor, preencha todos os campos e aceite os termos.'
            });
            return;
        }

        // Envia os dados para o VS Code
        vscode.postMessage({
            command: 'saveConfig',
            codigoEscola,
            matricula,
            github
        });
    });
})();