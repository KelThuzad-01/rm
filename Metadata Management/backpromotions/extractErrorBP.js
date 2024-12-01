const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const workingDirectory = 'C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx';
const resultJsonPath = path.join(workingDirectory, 'deploy-result.json'); // Ruta del resultado del despliegue

async function main() {
    // Comprobar si el archivo JSON existe
    if (fs.existsSync(resultJsonPath)) {
        console.log(`Found existing result file: ${resultJsonPath}`);
        // Leer y procesar el archivo JSON
        await processDeploymentResult();

    }

    // Lanzar el despliegue
    await runDeployment();
}

// Función para procesar el archivo JSON de resultados
async function processDeploymentResult() {
    console.log('Reading deployment result...');
    try {
        // Leer el archivo JSON
        const deployResult = JSON.parse(fs.readFileSync(resultJsonPath, 'utf-8'));
        const failedComponents = deployResult.result.details.componentFailures || [];

        console.log(`Found ${failedComponents.length} failed components.`);

        if (failedComponents.length > 0) {
            const failedFilePaths = failedComponents
                .map((failure) => failure.filePath || failure.fileName) // `filePath` o `fileName`
                .filter((filePath) => !!filePath); // Eliminar rutas no definidas

            if (failedFilePaths.length > 0) {
                console.log('Files to revert:', failedFilePaths);

                // Revertir los archivos problemáticos con git checkout
                revertFilesWithGitCheckout(failedFilePaths);
            } else {
                console.log('No valid file paths found to revert.');
            }
        } else {
            console.log('No failed components found. Deployment succeeded previously.');
        }
    } catch (error) {
        console.error('Error reading or processing deployment result:', error.message);
    }
}

// Función para revertir archivos con git checkout
function revertFilesWithGitCheckout(filePaths) {
    console.log('Reverting files...');
    try {
        filePaths.forEach((filePath) => {
            let relativePath = path.relative(workingDirectory, filePath); // Convertir a ruta relativa

            // Ajustar rutas para archivos .object
            if (relativePath.endsWith('.object')) {
                const objectName = path.basename(relativePath, '.object'); // Extraer el nombre del objeto
                relativePath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'objects',
                    objectName,
                    `${objectName}.object-meta.xml`
                );
            }else if (relativePath.endsWith('.cls')) {
                const objectName = path.basename(relativePath, '.object'); // Extraer el nombre del objeto
                relativePath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'classes',
                    `${objectName}`
                );
            }else if (relativePath.endsWith('.md')) {
                const objectName = path.basename(relativePath, '.object'); // Extraer el nombre del objeto
                relativePath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'customMetadata',
                    `${objectName}-meta.xml`
                );
            }else if (relativePath.endsWith('.profile')) {
                const objectName = path.basename(relativePath, '.object'); // Extraer el nombre del objeto
                relativePath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'profiles',
                    `"${objectName}"-meta.xml`
                );
            }

            // Comando para revertir archivo normal
            let checkoutCommand = `git checkout origin/ci/mobility C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\${relativePath}`;
            try {
                console.log(`Reverting file: C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\${relativePath}`);
                execSync(checkoutCommand, { cwd: workingDirectory });
                return;
            } catch (error) {
                if (error.message.includes('did not match any files')) {
                    console.warn(`File not found, skipping: ${relativePath}`);
                } else {
                    console.error(`Error reverting file: C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\${relativePath}`, error.message);
                }
            }
            //-meta.xml
            checkoutCommand = `git checkout origin/ci/mobility C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\${relativePath}-meta.xml`;
            try {
                console.log(`Reverting file: C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\${relativePath}-meta.xml`);
                execSync(checkoutCommand, { cwd: workingDirectory });
                return;
            } catch (error) {
                if (error.message.includes('did not match any files')) {
                    console.warn(`File not found, skipping: ${relativePath}-meta.xml`);
                } else {
                    console.error(`Error reverting file: C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\${relativePath}-meta.xml`, error.message);
                }
            }
            //perfiles
            //-meta.xml
            checkoutCommand = `git checkout origin/ci/mobility C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\"${relativePath}"-meta.xml`;
            try {
                console.log(`Reverting file: C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\"${relativePath}"-meta.xml`);
                execSync(checkoutCommand, { cwd: workingDirectory });
                return;
            } catch (error) {
                if (error.message.includes('did not match any files')) {
                    console.warn(`File not found, skipping: "${relativePath}"-meta.xml`);
                } else {
                    console.error(`Error reverting file: C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\"${relativePath}"-meta.xml`, error.message);
                }
            }
        });
        console.log('Reverted all valid failed files successfully.');
    } catch (error) {
        console.error('Unexpected error during file revert process:', error.message);
    }
}

// Función para ejecutar el despliegue
async function runDeployment() {
    console.log('Starting deployment...');
    let output;

    try {
        // Comando de despliegue
        const deployCommand = 'sf project deploy start --target-org mobility --manifest C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\package\\package.xml --ignore-conflicts --ignore-warnings --dry-run --json';
        output = execSync(deployCommand, { encoding: 'utf-8' });
        const deployResult = JSON.parse(output);

        // Guardar el resultado en un archivo JSON
        fs.writeFileSync(resultJsonPath, JSON.stringify(deployResult, null, 2), 'utf-8');
        console.log(`Deployment result saved to ${resultJsonPath}`);
    } catch (error) {
        console.error('Deployment failed. Saving error details...');

        if (error.stdout) {
            try {
                const deployResult = JSON.parse(error.stdout);
                fs.writeFileSync(resultJsonPath, JSON.stringify(deployResult, null, 2), 'utf-8');
                console.log(`Error deployment result saved to ${resultJsonPath}`);
            } catch (parseError) {
                console.error('Error parsing deployment result:', parseError.message);
            }
        }
    }
}

// Ejecutar el script
main();
