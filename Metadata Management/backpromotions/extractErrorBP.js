import { spawn } from 'child_process';

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
        let errorOutput = '';

        sfdxProcess.stdout.on('data', (data) => {
            const text = data.toString();
            deploymentOutput += text;
            console.log(text); // Mostrar salida en tiempo real
        });

        sfdxProcess.stderr.on('data', (data) => {
            const text = data.toString();
            errorOutput += text;
            console.error(text); // Mostrar errores y advertencias
        });

        sfdxProcess.on('close', (code) => {
            console.log("Despliegue finalizado con código:", code);

            try {
                const deploymentData = JSON.parse(deploymentOutput);
                resolve({ code, deploymentData });
            } catch (parseError) {
                console.error("Error analizando el JSON de salida:", parseError.message);
                console.error("Salida capturada:", deploymentOutput);
                resolve({ code, deploymentData: null });
            }
        });
    });
}

function extractFailedComponents(deploymentData) {
    try {
        const failedComponents = deploymentData.details.componentFailures || [];
        return Array.isArray(failedComponents) ? failedComponents : [failedComponents];
    } catch (error) {
        console.error("Error extrayendo componentes fallidos:", error.message);
        return [];
    }
}

async function main() {
    const { code, deploymentData } = await deployToSalesforce();

    if (!deploymentData) {
        console.error("El despliegue no fue exitoso y no se pudo analizar el JSON.");
        return;
    }

    console.log("JSON devuelto por Salesforce CLI:", JSON.stringify(deploymentData, null, 2));

    const failedComponents = extractFailedComponents(deploymentData).filter(
        (component) => component.state === 'Failed'
    );

    if (failedComponents.length > 0) {
        console.error("Componentes fallidos detectados:");
        failedComponents.forEach((failure) => {
            console.error(`- Archivo: ${failure.filePath}`);
            console.error(`  Error: ${failure.error}`);
            console.error(`  Línea: ${failure.lineNumber || 'N/A'}, Columna: ${failure.columnNumber || 'N/A'}`);
        });
    } else {
        console.log("No se detectaron componentes con estado 'Failed'.");
    }

    if (deploymentData.status === 'Succeeded') {
        console.log("Despliegue completado exitosamente.");
    } else {
        console.warn("El despliegue no fue exitoso.");
    }

    console.log("Continuando con el flujo principal...");
}

main();
