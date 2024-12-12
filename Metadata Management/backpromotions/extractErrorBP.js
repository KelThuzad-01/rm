//node scripts/source/backpromotion-from-dev.js ci/mobility
//Tras preparar la rama con el script backpromotion-dev, se lanza este .js con node y se intentan reducir la cantidad de errores. Se realiza commit con los cambios
//Antes de lanzar, situar en backpromotion/xxx y lanzar delta sfdx contra entorno destino sgd:source:delta --from origin/develop --output C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx
//retomar sf project deploy resume --job-id 0AfKN00000CeuDs0AJ --json --verbose |  ForEach-Object { $_ -replace "[^ -~]", "" } | ConvertFrom-Json | ConvertTo-Json -Depth 10 -Compress | Set-Content -Path $ResultJsonPath
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
let adjustedPath;
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
                    
                    // Ajustar rutas para diferentes tipos de metadatos
        // Ajustar rutas para diferentes tipos de metadatos
            // Ajustar rutas para diferentes tipos de metadatos
            if (/\.object(-meta\.xml)?$/.test(relativePath)) {
                const objectName = path.basename(relativePath, relativePath.endsWith('.object-meta.xml') ? '.object-meta.xml' : '.object');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'objects',
                    objectName,
                    relativePath.endsWith('.object-meta.xml') ? `${objectName}.object-meta.xml` : `${objectName}.object`
                );
            }
            else if (/\.cls(-meta\.xml)?$/.test(relativePath)) {
                const className = path.basename(relativePath, relativePath.endsWith('.cls-meta.xml') ? '.cls-meta.xml' : '.cls');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'classes',
                    relativePath.endsWith('.cls-meta.xml') ? `${className}.cls-meta.xml` : `${className}.cls`
                );
            }
            else if (/\.trigger(-meta\.xml)?$/.test(relativePath)) {
                const triggerName = path.basename(relativePath, relativePath.endsWith('.trigger-meta.xml') ? '.trigger-meta.xml' : '.trigger');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'triggers',
                    relativePath.endsWith('.trigger-meta.xml') ? `${triggerName}.trigger-meta.xml` : `${triggerName}.trigger`
                );
            } else if (/\.page(-meta\.xml)?$/.test(relativePath)) {
                const pageName = path.basename(relativePath, relativePath.endsWith('.page-meta.xml') ? '.page-meta.xml' : '.page');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'pages',
                    relativePath.endsWith('.page-meta.xml') ? `${pageName}.page-meta.xml` : `${pageName}.page`
                );
            } else if (/\.cmp(-meta\.xml)?$/.test(relativePath)) {
                const componentName = path.basename(relativePath, relativePath.endsWith('.cmp-meta.xml') ? '.cmp-meta.xml' : '.cmp');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'aura',
                    componentName,
                    relativePath.endsWith('.cmp-meta.xml') ? `${componentName}.cmp-meta.xml` : `${componentName}.cmp`
                );
            } else if (/\.app(-meta\.xml)?$/.test(relativePath)) {
                const appName = path.basename(relativePath, relativePath.endsWith('.app-meta.xml') ? '.app-meta.xml' : '.app');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'aura',
                    appName,
                    relativePath.endsWith('.app-meta.xml') ? `${appName}.app-meta.xml` : `${appName}.app`
                );
            } else if (/\.permissionset(-meta\.xml)?$/.test(relativePath)) {
                const permissionSetName = path.basename(relativePath, relativePath.endsWith('.permissionset-meta.xml') ? '.permissionset-meta.xml' : '.permissionset');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'permissionsets',
                    relativePath.endsWith('.permissionset-meta.xml') ? `${permissionSetName}.permissionset-meta.xml` : `${permissionSetName}.permissionset`
                );
            } else if (/\.profile(-meta\.xml)?$/.test(relativePath)) {
                const profileName = path.basename(relativePath, relativePath.endsWith('.profile-meta.xml') ? '.profile-meta.xml' : '.profile');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'profiles',
                    relativePath.endsWith('.profile-meta.xml') ? `${profileName}.profile-meta.xml` : `${profileName}.profile`
                );
            } else if (/\.md(-meta\.xml)?$/.test(relativePath)) {
                const metadataName = path.basename(relativePath, relativePath.endsWith('.md-meta.xml') ? '.md-meta.xml' : '.md');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'customMetadata',
                    relativePath.endsWith('.md-meta.xml') ? `${metadataName}.md-meta.xml` : `${metadataName}.md`
                );
            } else if (/\.flow(-meta\.xml)?$/.test(relativePath)) {
                const flowName = path.basename(relativePath, relativePath.endsWith('.flow-meta.xml') ? '.flow-meta.xml' : '.flow');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'flows',
                    relativePath.endsWith('.flow-meta.xml') ? `${flowName}.flow-meta.xml` : `${flowName}.flow`
                );
            } else if (/\.layout(-meta\.xml)?$/.test(relativePath)) {
                const layoutName = path.basename(relativePath, relativePath.endsWith('.layout-meta.xml') ? '.layout-meta.xml' : '.layout');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'layouts',
                    relativePath.endsWith('.layout-meta.xml') ? `${layoutName}.layout-meta.xml` : `${layoutName}.layout`
                );
            } else if (/\.tab(-meta\.xml)?$/.test(relativePath)) {
                const tabName = path.basename(relativePath, relativePath.endsWith('.tab-meta.xml') ? '.tab-meta.xml' : '.tab');
                adjustedPath = path.join(
                    'force-app',
                    'main',
                    'default',
                    'tabs',
                    relativePath.endsWith('.tab-meta.xml') ? `${tabName}.tab-meta.xml` : `${tabName}.tab`
                );
            }else if (/\.flexipage(-meta\.xml)?$/.test(relativePath)) {
            const flexiPageName = path.basename(relativePath, relativePath.endsWith('.flexipage-meta.xml') ? '.flexipage-meta.xml' : '.flexipage');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'flexipages',
                relativePath.endsWith('.flexipage-meta.xml') ? `${flexiPageName}.flexipage-meta.xml` : `${flexiPageName}.flexipage`
            );
        } else if (/\.globalValueSet(-meta\.xml)?$/.test(relativePath)) {
            const valueSetName = path.basename(relativePath, relativePath.endsWith('.globalValueSet-meta.xml') ? '.globalValueSet-meta.xml' : '.globalValueSet');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'globalValueSets',
                relativePath.endsWith('.globalValueSet-meta.xml') ? `${valueSetName}.globalValueSet-meta.xml` : `${valueSetName}.globalValueSet`
            );
        } else if (/\.labels(-meta\.xml)?$/.test(relativePath)) {
            const labelName = path.basename(relativePath, relativePath.endsWith('.labels-meta.xml') ? '.labels-meta.xml' : '.labels');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'labels',
                relativePath.endsWith('.labels-meta.xml') ? `${labelName}.labels-meta.xml` : `${labelName}.labels`
            );
        } else if (/\.sharingRules(-meta\.xml)?$/.test(relativePath)) {
            const sharingRulesName = path.basename(relativePath, relativePath.endsWith('.sharingRules-meta.xml') ? '.sharingRules-meta.xml' : '.sharingRules');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'sharingRules',
                relativePath.endsWith('.sharingRules-meta.xml') ? `${sharingRulesName}.sharingRules-meta.xml` : `${sharingRulesName}.sharingRules`
            );
        } else if (/\.quickAction(-meta\.xml)?$/.test(relativePath)) {
            const quickActionName = path.basename(relativePath, relativePath.endsWith('.quickAction-meta.xml') ? '.quickAction-meta.xml' : '.quickAction');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'quickActions',
                relativePath.endsWith('.quickAction-meta.xml') ? `${quickActionName}.quickAction-meta.xml` : `${quickActionName}.quickAction`
            );
        } else if (/\.validationRule(-meta\.xml)?$/.test(relativePath)) {
            const validationRuleName = path.basename(relativePath, relativePath.endsWith('.validationRule-meta.xml') ? '.validationRule-meta.xml' : '.validationRule');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'validationRules',
                relativePath.endsWith('.validationRule-meta.xml') ? `${validationRuleName}.validationRule-meta.xml` : `${validationRuleName}.validationRule`
            );
        } else if (/\.recordType(-meta\.xml)?$/.test(relativePath)) {
            const objectName = relativePath.split(path.sep)[2]; // Extract object name from path
            const recordTypeName = path.basename(relativePath, relativePath.endsWith('.recordType-meta.xml') ? '.recordType-meta.xml' : '.recordType');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'objects',
                objectName,
                'recordTypes',
                relativePath.endsWith('.recordType-meta.xml') ? `${recordTypeName}.recordType-meta.xml` : `${recordTypeName}.recordType`
            );
        } else if (/\.email(-meta\.xml)?$/.test(relativePath)) {
            const emailTemplateName = path.basename(relativePath, relativePath.endsWith('.email-meta.xml') ? '.email-meta.xml' : '.email');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'email',
                relativePath.endsWith('.email-meta.xml') ? `${emailTemplateName}.email-meta.xml` : `${emailTemplateName}.email`
            );
        } else if (/\.resource(-meta\.xml)?$/.test(relativePath)) {
            const resourceName = path.basename(relativePath, relativePath.endsWith('.resource-meta.xml') ? '.resource-meta.xml' : '.resource');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'staticresources',
                relativePath.endsWith('.resource-meta.xml') ? `${resourceName}.resource-meta.xml` : `${resourceName}.resource`
            );
        } else if (/\.workflow(-meta\.xml)?$/.test(relativePath)) {
            const workflowName = path.basename(relativePath, relativePath.endsWith('.workflow-meta.xml') ? '.workflow-meta.xml' : '.workflow');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'workflows',
                relativePath.endsWith('.workflow-meta.xml') ? `${workflowName}.workflow-meta.xml` : `${workflowName}.workflow`
            );
        } else if (/\.report(-meta\.xml)?$/.test(relativePath)) {
            const parts = relativePath.split(path.sep);
            const folderName = parts[1]; // Folder name
            const reportName = path.basename(relativePath, relativePath.endsWith('.report-meta.xml') ? '.report-meta.xml' : '.report');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'reports',
                folderName,
                relativePath.endsWith('.report-meta.xml') ? `${reportName}.report-meta.xml` : `${reportName}.report`
            );
        } else if (/\.dashboard(-meta\.xml)?$/.test(relativePath)) {
            const dashboardName = path.basename(relativePath, relativePath.endsWith('.dashboard-meta.xml') ? '.dashboard-meta.xml' : '.dashboard');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'dashboards',
                relativePath.endsWith('.dashboard-meta.xml') ? `${dashboardName}.dashboard-meta.xml` : `${dashboardName}.dashboard`
            );
        } else if (/\.js(-meta\.xml)?$/.test(relativePath)) {
            const lwcName = relativePath.split(path.sep)[1]; // LWC component name
            const fileName = path.basename(relativePath);
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'lwc',
                lwcName,
                fileName.endsWith('.js-meta.xml') ? `${lwcName}.js-meta.xml` : fileName
            );
        } else if (/\.theme(-meta\.xml)?$/.test(relativePath)) {
            const themeName = path.basename(relativePath, relativePath.endsWith('.theme-meta.xml') ? '.theme-meta.xml' : '.theme');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'themes',
                relativePath.endsWith('.theme-meta.xml') ? `${themeName}.theme-meta.xml` : `${themeName}.theme`
            );
        } else if (/\.permissionsetgroup(-meta\.xml)?$/.test(relativePath)) {
            const groupName = path.basename(relativePath, relativePath.endsWith('.permissionsetgroup-meta.xml') ? '.permissionsetgroup-meta.xml' : '.permissionsetgroup');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'permissionsetgroups',
                relativePath.endsWith('.permissionsetgroup-meta.xml') ? `${groupName}.permissionsetgroup-meta.xml` : `${groupName}.permissionsetgroup`
            );
        } else if (/\.remoteSite(-meta\.xml)?$/.test(relativePath)) {
            const remoteSiteName = path.basename(relativePath, relativePath.endsWith('.remoteSite-meta.xml') ? '.remoteSite-meta.xml' : '.remoteSite');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'remoteSiteSettings',
                relativePath.endsWith('.remoteSite-meta.xml') ? `${remoteSiteName}.remoteSite-meta.xml` : `${remoteSiteName}.remoteSite`
            );
        } else if (/\.connectedApp(-meta\.xml)?$/.test(relativePath)) {
            const connectedAppName = path.basename(relativePath, relativePath.endsWith('.connectedApp-meta.xml') ? '.connectedApp-meta.xml' : '.connectedApp');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'connectedApps',
                relativePath.endsWith('.connectedApp-meta.xml') ? `${connectedAppName}.connectedApp-meta.xml` : `${connectedAppName}.connectedApp`
            );
        } else if (/\.site(-meta\.xml)?$/.test(relativePath)) {
            const siteName = path.basename(relativePath, relativePath.endsWith('.site-meta.xml') ? '.site-meta.xml' : '.site');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'sites',
                relativePath.endsWith('.site-meta.xml') ? `${siteName}.site-meta.xml` : `${siteName}.site`
            );
        } else if (/\.translation(-meta\.xml)?$/.test(relativePath)) {
            const translationName = path.basename(relativePath, relativePath.endsWith('.translation-meta.xml') ? '.translation-meta.xml' : '.translation');
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'translations',
                relativePath.endsWith('.translation-meta.xml') ? `${translationName}.translation-meta.xml` : `${translationName}.translation`
            );
        } else if (relativePath.startsWith('experiences')) {
            const experienceName = relativePath.split(path.sep)[1]; // Experience name
            adjustedPath = path.join(
                'force-app',
                'main',
                'default',
                'experiences',
                experienceName
            );
        }                          
        else {
        console.log(`Archivo desconocido : ${relativePath}`);
        adjustedPath = relativePath;
    }
        // Comando para revertir archivo con Git
        let checkoutCommand = `git checkout origin/ci/solar-develop -- "${adjustedPath}"`;
        //let checkoutCommand = `git checkout origin/ci/mobility -- "${adjustedPath}"`;

        try {
            execSync(checkoutCommand, { cwd: workingDirectory });
        } catch (error) {
                //console.warn(`File not found in origin/ci/mobility, deleting locally: ${adjustedPath}`);
        }
        checkoutCommand = `git checkout origin/ci/solar-develop -- "${adjustedPath}"-meta.xml`;
       // checkoutCommand = `git checkout origin/ci/mobility -- "${adjustedPath}"-meta.xml`;
        try {
            execSync(checkoutCommand, { cwd: workingDirectory });
        } catch (error) {
                //console.warn(`File not found in origin/ci/mobility, deleting locally: ${adjustedPath}`);
        }
        });
        
try {
    const gitLsRemote = execSync(`git ls-tree origin/ci/solar-develop --name-only "${adjustedPath}"`, { cwd: workingDirectory, encoding: 'utf-8' }).trim();
    //const gitLsRemote = execSync(`git ls-tree origin/ci/mobility --name-only "${adjustedPath}"`, { cwd: workingDirectory, encoding: 'utf-8' }).trim();
    if (!gitLsRemote) {

        // Eliminar el archivo si no existe en la rama de destino
        try {
            const deleteCommand = `git rm "${adjustedPath}"`;
            execSync(deleteCommand, { cwd: workingDirectory });
            console.log(`Deleted file: ${adjustedPath}`);
        } catch (deleteError) {
            console.error(`Error deleting file: ${adjustedPath}`, deleteError.message);
        }
    } else {
        console.log(`File exists in origin/ci/solar-develop: ${adjustedPath}. Skipping deletion.`);
        //console.log(`File exists in origin/ci/mobility: ${adjustedPath}. Skipping deletion.`);
    }
} catch (statusError) {
    console.warn(`Unable to determine if file exists in origin/ci/solar-develop: ${adjustedPath}. Proceeding with caution.`);
    //console.warn(`Unable to determine if file exists in origin/ci/mobility: ${adjustedPath}. Proceeding with caution.`);
}   
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
