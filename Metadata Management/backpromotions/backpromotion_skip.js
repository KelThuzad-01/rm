
//tutor IB devuelve error grave


//let deployCommand = 'sf project deploy start --target-org IBD-prod --manifest C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\package\\package.xml --ignore-conflicts --ignore-warnings --dry-run';

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuración del despliegue
let deployCommand = 'sf project deploy start --target-org mobility --manifest C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\package\\package.xml --ignore-conflicts --ignore-warnings --dry-run --json';
const workingDirectory = 'C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx';
const packageXmlPath = path.join(workingDirectory, 'package', 'package.xml');

// Leer y modificar el archivo package.xml
fs.readFile(packageXmlPath, 'utf8', (err, data) => {
    if (err) {
        console.error('Error al leer el archivo:', err);
        return;
    }
    const blockToRemove = `
    <types>
        <members>en_GB</members>
        <members>en_US</members>
        <members>es</members>
        <members>fr</members>
        <members>it</members>
        <members>pt_PT</members>
        <name>Translations</name>
    </types>`;
    const updatedData = data.replace(blockToRemove, '');
    fs.writeFile(packageXmlPath, updatedData, 'utf8', (err) => {
        if (err) {
            console.error('Error al escribir el archivo:', err);
        } else {
            console.log('Bloque eliminado con éxito.');
        }
    });
});

async function main() {
    let deploymentAttempts = 0;
    let continueDeployment = true;

    while (continueDeployment) {
        deploymentAttempts++;
        console.log(`Starting deployment attempt #${deploymentAttempts}...`);
        let deploymentId;
        let deploymentStatus = 'Pending';

        try {
            // Ejecutar el despliegue inicial
            const deployOutput = execSync(deployCommand, { encoding: 'utf-8' });
            const deployResult = JSON.parse(deployOutput);
            deploymentId = deployResult.result.id;
            console.log('Deployment initiated with ID:', deploymentId);
        } catch (error) {
        }

        // Monitorizar el estado del despliegue
        while (deploymentStatus !== 'Succeeded' && deploymentStatus !== 'Failed') {
            console.log('Checking deployment status...');
            try {
                const statusOutput = execSync(`sf project deploy report --job-id ${deploymentId} --json`, {
                    encoding: 'utf-8',
                });
                const statusResult = JSON.parse(statusOutput);
                deploymentStatus = statusResult.result.status;

                console.log(`Deployment status: ${deploymentStatus}`);
                if (deploymentStatus === 'InProgress') {
                    console.log('Deployment still in progress...');
                    await sleep(10000); // Esperar 10 segundos antes de volver a verificar
                } else if (deploymentStatus === 'Failed') {
                    console.error('Deployment failed. Processing errors...');
                    const problematicNames = extractProblematicNames(statusResult.result.details.errors);
                    if (problematicNames.length > 0) {
                        console.log('Problematic metadata identified:', problematicNames);
                        commentLinesInPackageXml(problematicNames, packageXmlPath);
                    } else {
                        console.log('No problematic metadata found.');
                    }
                }
            } catch (error) {
                console.error('Error checking deployment status:', error.message);
                process.exit(1);
            }
        }

        if (deploymentStatus === 'Succeeded') {
            console.log('Deployment completed successfully.');
            continueDeployment = false; // Salir del bucle
        } else if (deploymentStatus === 'Failed') {
            console.log('Retrying deployment...');
        }
    }
}

// Función para extraer nombres problemáticos del reporte de errores
function extractProblematicNames(errors) {
    const problematicNames = [];
    if (Array.isArray(errors)) {
        errors.forEach((error) => {
            if (error.problemType === 'Error') {
                problematicNames.push(error.fileName);
            }
        });
    }
    return problematicNames;
}

// Función para comentar líneas en el archivo package.xml
function commentLinesInPackageXml(names, filePath) {
    const content = fs.readFileSync(filePath, 'utf-8');
    const updatedContent = content.replace(
        new RegExp(`(<members>(${names.join('|')})</members>)`, 'g'),
        '<!-- $1 -->'
    );
    fs.writeFileSync(filePath, updatedContent, 'utf-8');
    console.log('Updated package.xml with commented lines for problematic metadata.');
}

// Función para pausar la ejecución
function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

// Ejecutar el script
main();
