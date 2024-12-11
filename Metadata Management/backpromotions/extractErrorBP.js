//node scripts/source/backpromotion-from-dev.js ci/mobility
//Tras preparar la rama con el script backpromotion-dev, se lanza este .js con node y se intentan reducir la cantidad de errores. Se realiza commit con los cambios
//Antes de lanzar, situar en backpromotion/xxx y lanzar delta sfdx contra entorno destino sgd:source:delta --from origin/develop --output C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx
//retomar sf project deploy resume --job-id 0AfKN00000CWu1J0AT --json --verbose |  ForEach-Object { $_ -replace "[^ -~]", "" } |  | ConvertFrom-Json | ConvertTo-Json -Depth 10 -Compress | Set-Content -Path $ResultJsonPath
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
        if (relativePath.endsWith('.object') || relativePath.endsWith('.object-meta.xml')) {
            const objectName = path.basename(relativePath, relativePath.endsWith('.object-meta.xml') ? '.object-meta.xml' : '.object');
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
        } else if (relativePath.endsWith('.page') || relativePath.endsWith('.page-meta.xml')) {
            const pageName = path.basename(relativePath, relativePath.endsWith('.page-meta.xml') ? '.page-meta.xml' : '.page');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'pages',
                `${pageName}.page-meta.xml`
            );
        } else if (relativePath.endsWith('.cmp') || relativePath.endsWith('.cmp-meta.xml')) {
            const componentName = path.basename(relativePath, relativePath.endsWith('.cmp-meta.xml') ? '.cmp-meta.xml' : '.cmp');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'aura',
                componentName,
                `${componentName}.cmp-meta.xml`
            );
        } else if (relativePath.endsWith('.app') || relativePath.endsWith('.app-meta.xml')) {
            const appName = path.basename(relativePath, relativePath.endsWith('.app-meta.xml') ? '.app-meta.xml' : '.app');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'aura',
                appName,
                `${appName}.app-meta.xml`
            );
        } else if (relativePath.endsWith('.permissionset') || relativePath.endsWith('.permissionset-meta.xml')) {
            const permissionSetName = path.basename(relativePath, relativePath.endsWith('.permissionset-meta.xml') ? '.permissionset-meta.xml' : '.permissionset');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'permissionsets',
                `${permissionSetName}.permissionset-meta.xml`
            );
        } else if (relativePath.endsWith('.profile') || relativePath.endsWith('.profile-meta.xml')) {
            const profileName = path.basename(relativePath, relativePath.endsWith('.profile-meta.xml') ? '.profile-meta.xml' : '.profile');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'profiles',
                `${profileName}.profile-meta.xml`
            );
        } else if (relativePath.endsWith('.md') || relativePath.endsWith('.md-meta.xml')) {
            const metadataName = path.basename(relativePath, relativePath.endsWith('.md-meta.xml') ? '.md-meta.xml' : '.md');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'customMetadata',
                `${metadataName}.md-meta.xml`
            );
        } else if (relativePath.endsWith('.flow') || relativePath.endsWith('.flow-meta.xml')) {
            const flowName = path.basename(relativePath, relativePath.endsWith('.flow-meta.xml') ? '.flow-meta.xml' : '.flow');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'flows',
                `${flowName}.flow-meta.xml`
            );
        } else if (relativePath.endsWith('.layout') || relativePath.endsWith('.layout-meta.xml')) {
            const layoutName = path.basename(relativePath, relativePath.endsWith('.layout-meta.xml') ? '.layout-meta.xml' : '.layout');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'layouts',
                `${layoutName}.layout-meta.xml`
            );
        } else if (relativePath.endsWith('.tab') || relativePath.endsWith('.tab-meta.xml')) {
            const tabName = path.basename(relativePath, relativePath.endsWith('.tab-meta.xml') ? '.tab-meta.xml' : '.tab');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'tabs',
                `${tabName}.tab-meta.xml`
            );
        } else if (relativePath.endsWith('.flexipage') || relativePath.endsWith('.flexipage-meta.xml')) {
            const flexiPageName = path.basename(relativePath, relativePath.endsWith('.flexipage-meta.xml') ? '.flexipage-meta.xml' : '.flexipage');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'flexipages',
                `${flexiPageName}.flexipage-meta.xml`
            );
        } else if (relativePath.endsWith('.globalValueSet') || relativePath.endsWith('.globalValueSet-meta.xml')) {
            const valueSetName = path.basename(relativePath, relativePath.endsWith('.globalValueSet-meta.xml') ? '.globalValueSet-meta.xml' : '.globalValueSet');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'globalValueSets',
                `${valueSetName}.globalValueSet-meta.xml`
            );
        } else if (relativePath.endsWith('.labels') || relativePath.endsWith('.labels-meta.xml')) {
            const labelName = path.basename(relativePath, relativePath.endsWith('.labels-meta.xml') ? '.labels-meta.xml' : '.labels');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'labels',
                `${labelName}.labels-meta.xml`
            );
        } else if (relativePath.endsWith('.sharingRules') || relativePath.endsWith('.sharingRules-meta.xml')) {
            const sharingRulesName = path.basename(relativePath, relativePath.endsWith('.sharingRules-meta.xml') ? '.sharingRules-meta.xml' : '.sharingRules');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'sharingRules',
                `${sharingRulesName}.sharingRules-meta.xml`
            );
        } else if (relativePath.endsWith('.quickAction') || relativePath.endsWith('.quickAction-meta.xml')) {
            const quickActionName = path.basename(relativePath, relativePath.endsWith('.quickAction-meta.xml') ? '.quickAction-meta.xml' : '.quickAction');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'quickActions',
                `${quickActionName}.quickAction-meta.xml`
            );
        } else if (relativePath.endsWith('.validationRule') || relativePath.endsWith('.validationRule-meta.xml')) {
            const validationRuleName = path.basename(relativePath, relativePath.endsWith('.validationRule-meta.xml') ? '.validationRule-meta.xml' : '.validationRule');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'validationRules',
                `${validationRuleName}.validationRule-meta.xml`
            );
        } else if (relativePath.endsWith('.recordType') || relativePath.endsWith('.recordType-meta.xml')) {
            const objectName = relativePath.split(path.sep)[2]; // Extraer el nombre del objeto desde la ruta
            const recordTypeName = path.basename(relativePath, relativePath.endsWith('.recordType-meta.xml') ? '.recordType-meta.xml' : '.recordType');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'objects',
                objectName,
                'recordTypes',
                `${recordTypeName}.recordType-meta.xml`
            );
        } else if (relativePath.endsWith('.email') || relativePath.endsWith('.email-meta.xml')) {
            const emailTemplateName = path.basename(relativePath, relativePath.endsWith('.email-meta.xml') ? '.email-meta.xml' : '.email');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'email',
                `${emailTemplateName}.email-meta.xml`
            );
        } else if (relativePath.endsWith('.resource') || relativePath.endsWith('.resource-meta.xml')) {
            const resourceName = path.basename(relativePath, relativePath.endsWith('.resource-meta.xml') ? '.resource-meta.xml' : '.resource');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'staticresources',
                `${resourceName}.resource-meta.xml`
            );
        } else if (relativePath.endsWith('.workflow') || relativePath.endsWith('.workflow-meta.xml')) {
            const workflowName = path.basename(relativePath, relativePath.endsWith('.workflow-meta.xml') ? '.workflow-meta.xml' : '.workflow');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'workflows',
                `${workflowName}.workflow-meta.xml`
            );
        } else if (relativePath.endsWith('.report') || relativePath.endsWith('.report-meta.xml')) {
            const parts = relativePath.split(path.sep);
            const folderName = parts[1]; // Nombre de la carpeta del reporte
            const reportName = path.basename(relativePath, relativePath.endsWith('.report-meta.xml') ? '.report-meta.xml' : '.report');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'reports',
                folderName,
                `${reportName}.report-meta.xml`
            );
        } else if (relativePath.endsWith('.dashboard') || relativePath.endsWith('.dashboard-meta.xml')) {
            const dashboardName = path.basename(relativePath, relativePath.endsWith('.dashboard-meta.xml') ? '.dashboard-meta.xml' : '.dashboard');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'dashboards',
                dashboardName,
                `${dashboardName}.dashboard-meta.xml`
            );
        } else if (relativePath.endsWith('.app') || relativePath.endsWith('.app-meta.xml')) {
            const appName = path.basename(relativePath, relativePath.endsWith('.app-meta.xml') ? '.app-meta.xml' : '.app');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'applications',
                `${appName}.app-meta.xml`
            );
        } else if (relativePath.endsWith('.js') || relativePath.endsWith('.js-meta.xml')) {
            const lwcName = relativePath.split(path.sep)[1]; // Nombre del componente LWC
            const fileName = path.basename(relativePath);
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'lwc',
                lwcName,
                fileName.endsWith('.js-meta.xml') ? `${lwcName}.js-meta.xml` : fileName
            );
        } else if (relativePath.endsWith('.theme') || relativePath.endsWith('.theme-meta.xml')) {
            const themeName = path.basename(relativePath, relativePath.endsWith('.theme-meta.xml') ? '.theme-meta.xml' : '.theme');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'themes',
                `${themeName}.theme-meta.xml`
            );
        } else if (relativePath.endsWith('.permissionsetgroup') || relativePath.endsWith('.permissionsetgroup-meta.xml')) {
            const groupName = path.basename(relativePath, relativePath.endsWith('.permissionsetgroup-meta.xml') ? '.permissionsetgroup-meta.xml' : '.permissionsetgroup');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'permissionsetgroups',
                `${groupName}.permissionsetgroup-meta.xml`
            );
        } else if (relativePath.endsWith('.remoteSite') || relativePath.endsWith('.remoteSite-meta.xml')) {
            const remoteSiteName = path.basename(relativePath, relativePath.endsWith('.remoteSite-meta.xml') ? '.remoteSite-meta.xml' : '.remoteSite');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'remoteSiteSettings',
                `${remoteSiteName}.remoteSite-meta.xml`
            );
        } else if (relativePath.endsWith('.connectedApp') || relativePath.endsWith('.connectedApp-meta.xml')) {
            const connectedAppName = path.basename(relativePath, relativePath.endsWith('.connectedApp-meta.xml') ? '.connectedApp-meta.xml' : '.connectedApp');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'connectedApps',
                `${connectedAppName}.connectedApp-meta.xml`
            );
        } else if (relativePath.endsWith('.site') || relativePath.endsWith('.site-meta.xml')) {
            const siteName = path.basename(relativePath, relativePath.endsWith('.site-meta.xml') ? '.site-meta.xml' : '.site');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'sites',
                `${siteName}.site-meta.xml`
            );
        } else if (relativePath.endsWith('.translation') || relativePath.endsWith('.translation-meta.xml')) {
            const translationName = path.basename(relativePath, relativePath.endsWith('.translation-meta.xml') ? '.translation-meta.xml' : '.translation');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'translations',
                `${translationName}.translation-meta.xml`
            );
        } else if (relativePath.startsWith('experiences')) {
            const experienceName = relativePath.split(path.sep)[1]; // Nombre de la experiencia
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'experiences',
                experienceName
            );
            } else {
                system.log(`Archivo desconocido: "${adjustedPath}"`);
                // Para otros tipos de archivos o casos desconocidos
                adjustedPath = relativePath; // Usar la ruta relativa sin cambios
            }
    
                    // Comando para revertir archivo con Git
        let checkoutCommand = `git checkout origin/ci/solar-develop -- "${adjustedPath}"`;

        //let checkoutCommand = `git checkout origin/ci/mobility -- "${adjustedPath}"`;

        try {
            execSync(checkoutCommand, { cwd: workingDirectory });
        } catch (error) {
                //console.warn(`File not found in origin/ci/mobility, deleting locally: ${adjustedPath}`);
                try {
                    // Eliminar el archivo localmente si no existe en la rama de destino
                    const deleteCommand = `git rm "${adjustedPath}"`; // Usa si no quieres eliminar el archivo físicamente
                    execSync(deleteCommand, { cwd: workingDirectory });
                } catch (deleteError) {
                    console.error(`Error deleting file: ${adjustedPath}`, deleteError.message);
                }
        }
        checkoutCommand = `git checkout origin/ci/solar-develop -- "${adjustedPath}"-meta.xml`;
        try {
            execSync(checkoutCommand, { cwd: workingDirectory });
        } catch (error) {
                //console.warn(`File not found in origin/ci/mobility, deleting locally: ${adjustedPath}`);
                try {
                    // Eliminar el archivo localmente si no existe en la rama de destino
                    const deleteCommand = `git rm "${adjustedPath}"`; // Usa si no quieres eliminar el archivo físicamente
                    execSync(deleteCommand, { cwd: workingDirectory });
                } catch (deleteError) {
                    console.error(`Error deleting file: ${adjustedPath}`, deleteError.message);
                }
        }
        });
        console.log('DONE');
    } catch (error) {
        console.error('Unexpected error during file revert process:', error.message);
    }    
}

// Función para ejecutar el despliegue
async function runDeployment() {
    console.log('Deployment in progress...');
    try {
        // Comando de despliegue
        const deployCommand = 'sf project deploy start --target-org solar-develop --manifest C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\package\\package.xml --ignore-conflicts --ignore-warnings --dry-run --json --verbose --wait 120';
        //const deployCommand = 'sf project deploy start --target-org mobility --manifest C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\package\\package.xml --ignore-conflicts --ignore-warnings --dry-run --json --verbose --wait 120';
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
