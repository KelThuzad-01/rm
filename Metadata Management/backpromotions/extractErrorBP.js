//node scripts/source/backpromotion-from-dev.js ci/mobility
//Tras preparar la rama con el script backpromotion-dev, se lanza este .js con node y se intentan reducir la cantidad de errores. Se realiza commit con los cambios
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const workingDirectory = 'C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx';
const resultJsonPath = path.join(workingDirectory, 'deploy-result.json');

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
            let adjustedPath;
    
            // Ajustar rutas para diferentes tipos de metadatos
            if (relativePath.endsWith('.object')) {
                const objectName = path.basename(relativePath, '.object');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'objects',
                    objectName,
                    `${objectName}.object-meta.xml`
                );
            } else if (relativePath.endsWith('.cls')) {
                const className = path.basename(relativePath, '.cls');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'classes',
                    `${className}.cls`
                );
            } else if (relativePath.endsWith('.trigger')) {
                const triggerName = path.basename(relativePath, '.trigger');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'triggers',
                    `${triggerName}.trigger`
                );
            } else if (relativePath.endsWith('.page')) {
                const pageName = path.basename(relativePath, '.page');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'pages',
                    `${pageName}.page-meta.xml`
                );
            } else if (relativePath.endsWith('.cmp')) {
                const componentName = path.basename(relativePath, '.cmp');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'aura',
                    componentName,
                    `${componentName}.cmp-meta.xml`
                );
            } else if (relativePath.endsWith('.app')) {
                const appName = path.basename(relativePath, '.app');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'aura',
                    appName,
                    `${appName}.app-meta.xml`
                );
            } else if (relativePath.endsWith('.permissionset')) {
                const permissionSetName = path.basename(relativePath, '.permissionset');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'permissionsets',
                    `${permissionSetName}.permissionset-meta.xml`
                );
            } else if (relativePath.endsWith('.profile')) {
                const profileName = path.basename(relativePath, '.profile');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'profiles',
                    `${profileName}.profile-meta.xml`
                );
            } else if (relativePath.endsWith('.md')) {
                const metadataName = path.basename(relativePath, '.md'); // Extraer el nombre del archivo sin la extensión
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'customMetadata',
                    `${metadataName}.md-meta.xml`
                );    
            } else if (relativePath.endsWith('.flow')) {
                const flowName = path.basename(relativePath, '.flow'); // Extraer el nombre del flujo sin extensión
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'flows',
                    `${flowName}.flow-meta.xml`
                );    
            } else if (relativePath.endsWith('.layout')) {
                const layoutName = path.basename(relativePath, '.layout');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'layouts',
                    `${layoutName}.layout-meta.xml`
                );
            } else if (relativePath.endsWith('.tab')) {
                const tabName = path.basename(relativePath, '.tab');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'tabs',
                    `${tabName}.tab-meta.xml`
                );
            } else if (relativePath.endsWith('.flexipage')) {
                const flexiPageName = path.basename(relativePath, '.flexipage');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'flexipages',
                    `${flexiPageName}.flexipage-meta.xml`
                );
            } else if (relativePath.endsWith('.globalValueSet')) {
                const valueSetName = path.basename(relativePath, '.globalValueSet');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'globalValueSets',
                    `${valueSetName}.globalValueSet-meta.xml`
                );
            } else if (relativePath.endsWith('.labels')) {
                const labelName = path.basename(relativePath, '.labels');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'labels',
                    `${labelName}.labels-meta.xml`
                );
            } else if (relativePath.endsWith('.sharingRules')) {
                const sharingRulesName = path.basename(relativePath, '.sharingRules');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'sharingRules',
                    `${sharingRulesName}.sharingRules-meta.xml`
                );
            } else if (relativePath.endsWith('.quickAction')) {
                const quickActionName = path.basename(relativePath, '.quickAction');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'quickActions',
                    `${quickActionName}.quickAction-meta.xml`
                );
            } else if (relativePath.endsWith('.validationRule')) {
                const validationRuleName = path.basename(relativePath, '.validationRule');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'validationRules',
                    `${validationRuleName}.validationRule-meta.xml`
                );
            } else if (relativePath.endsWith('.recordType')) {
                // Manejar RecordType
                const objectName = relativePath.split(path.sep)[2]; // Extraer el nombre del objeto desde la ruta
                const recordTypeName = path.basename(relativePath, '.recordType'); // Extraer el nombre del RecordType
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'objects',
                    objectName,
                    'recordTypes',
                    `${recordTypeName}.recordType-meta.xml`
                );
            } else {
                // Para otros tipos de archivos o casos desconocidos
                adjustedPath = relativePath; // Usar la ruta relativa sin cambios
            }
    
                    // Comando para revertir archivo con Git
        let checkoutCommand = `git checkout origin/ci/solar-develop -- "${adjustedPath}"`;
        //let checkoutCommand = `git checkout origin/ci/mobility -- "${adjustedPath}"`;

        try {
            console.log(`Reverting file: ${adjustedPath}`);
            execSync(checkoutCommand, { cwd: workingDirectory });
        } catch (error) {
            if (error.message.includes('did not match any files')) {
                console.warn(`File not found in origin/ci/solar-develop, deleting locally: ${adjustedPath}`);
                //console.warn(`File not found in origin/ci/mobility, deleting locally: ${adjustedPath}`);
                try {
                    // Eliminar el archivo localmente si no existe en la rama de destino
                    const deleteCommand = `git rm --cached "${adjustedPath}"`; // Usa --cached si no quieres eliminar el archivo físicamente
                    execSync(deleteCommand, { cwd: workingDirectory });
                    console.log(`Deleted file: ${adjustedPath}`);
                } catch (deleteError) {
                    console.error(`Error deleting file: ${adjustedPath}`, deleteError.message);
                }
            } else {
                console.error(`Error reverting file: ${adjustedPath}`, error.message);
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
    try {
        // Comando de despliegue
        const deployCommand = 'sf project deploy start --target-org solar-develop --manifest C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\package\\package.xml --ignore-conflicts --ignore-warnings --dry-run --json';
        //const deployCommand = 'sf project deploy start --target-org mobility --manifest C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\package\\package.xml --ignore-conflicts --ignore-warnings --dry-run --json';
        output = execSync(deployCommand, { encoding: 'utf-8' });
        const deployResult = JSON.parse(output);

        // Guardar el resultado en un archivo JSON
        fs.writeFileSync(resultJsonPath, JSON.stringify(deployResult, null, 2), 'utf-8');
        console.log(`Deployment result saved to ${resultJsonPath}`);
        console.log('Genera un nuevo delta con los cambios');
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
