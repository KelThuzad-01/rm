import { spawn } from 'child_process';
import { execSync } from 'child_process';
import { readFileSync } from 'fs';
import { checkoutBranchFrom, commit, findMergeCommitsOneLineSync, pushChanges } from './git-utils.js';
const MAX_ATTEMPTS = 4;
let attempt = 0;
function getCurrentBranch() {
    try {
        return execSync(`git rev-parse --abbrev-ref HEAD`).toString().trim();
    } catch (error) {
        console.error(`Error obteniendo la rama actual: ${error.message}`);
        process.exit(1); // Finaliza el script si no puede obtener la rama
    }
}

function deployToSalesforce() {
    const commandArguments = [
        'force:source:deploy',
        '--target-org', 'mobility',
        '-x', 'deploy-manifest/package/package.xml',
        '--postdestructivechanges', 'deploy-manifest/destructiveChanges/destructiveChanges.xml',
        '--wait', '120',
        '--ignorewarnings',
        '--json',
        '--verbose',
        '-c'
    ];

    console.log("Iniciando despliegue en Salesforce...");

    return new Promise((resolve, reject) => {
        const sfdxProcess = spawn('sfdx', commandArguments, { shell: true });

        let deploymentOutput = '';

        sfdxProcess.stdout.on('data', (data) => {
            const text = data.toString();
            deploymentOutput += text;
            console.log(text); // Mostrar salida en tiempo real
        });

        sfdxProcess.stderr.on('data', (data) => {
            console.error(data.toString());
        });

        sfdxProcess.on('close', (code) => {
            console.log("Despliegue finalizado con código:", code);

            // Buscar componentes fallidos
            const failedComponents = extractFailedComponents(deploymentOutput);
            resolve({ failedComponents, code });
        });
    });
}

function extractFailedComponents(output) {
    const lines = output.split('\n');
    const failedComponents = new Set(); // Usar un conjunto para evitar duplicados

    for (let i = 0; i < lines.length; i++) {
        if (lines[i].includes('"state": "Failed"')) {
            // Buscar el siguiente "filePath"
            const filePathLine = lines.slice(i + 1).find(line => line.includes('"filePath"'));
            if (filePathLine) {
                const match = filePathLine.match(/"filePath":\s*"(.*?)"/);
                if (match) {
                    failedComponents.add(match[1]);
                }
            }
        }
    }

    return Array.from(failedComponents); // Convertir el conjunto a una lista
}


async function main() {
    while (attempt < MAX_ATTEMPTS) {
        console.log(`Attempt ${attempt + 1} of ${MAX_ATTEMPTS}`);
    try {
        const { failedComponents, code } = await deployToSalesforce();
        
        if (code !== 0) {
            console.error("El despliegue no fue exitoso.");
        }

        if (failedComponents.length > 0) {
            console.log("Componentes fallidos detectados:");
            failedComponents.forEach((filePath) => {
                try {
                    console.log(`Realizando checkout de ${filePath} para restaurar a la versión de la rama ci/mobility...`);
                    execSync(`git checkout origin/ci/mobility ${filePath}`);
                    console.log(`Componente restaurado: ${filePath}`);
                } catch (checkoutError) {
                    console.error(`Error al restaurar el componente ${filePath}: ${checkoutError.message}`);
                }
            });
        } else {
            console.log("No se detectaron componentes fallidos. Finalizado");
            process.exit(0);
        }
    } catch (error) {
        console.error("Error durante el despliegue:", error.message);
    }
    const commitMessage = `Backpromotion Scheduled Partial - Discard components with error`;
            commit(commitMessage, true);
            const branchName = getCurrentBranch();
            pushChanges(branchName);
            console.log("Generando delta");
            execSync(`sfdx sgd:source:delta -f origin/ci/mobility -o deploy-manifest --ignore .deltaignore -W`);

    attempt++;

    // Si alcanzamos el último intento, salir con un mensaje
    if (attempt === MAX_ATTEMPTS) {
        console.error('Maximum deployment attempts reached. Exiting.');
    } else {
        console.log('Retrying...');
    }
}
}

main();
