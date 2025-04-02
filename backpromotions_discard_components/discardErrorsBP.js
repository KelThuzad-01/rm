//1- Obtener json desde SF cambiando entorno e id:
//sfdx force:mdapi:deploy:report -i 0AfKN00000DH4he -u solar-develop --json | Out-File -FilePath deployment-results.json -Encoding utf8
//2- ajustar rama más abajo para hacer checkout
//3 lanzar chcp 65001
//4- lanzar este script desde iberdrola-sfdx: 
// chcp 65001; node "C:\Users\aberdun\Downloads\rm\backpromotions_discard_components\discardErrorsBP.js"

//1- Obtener json desde SF cambiando entorno e id:
//sfdx force:mdapi:deploy:report -i 0AfKN00000DH4he -u solar-develop --json | Out-File -FilePath deployment-results.json -Encoding utf8
//2- ajustar rama más abajo para hacer checkout
//3- lanzar este script desde iberdrola-sfdx: node "C:\Users\aberdun\Downloads\rm\backpromotions_discard_components\discardErrorsBP.js"

const { exec } = require('child_process');
const fs = require('fs');
const { promisify } = require('util');
const execAsync = promisify(exec);

const debugData = [];
const debugFilePath = 'debug-discard.json';
const deploymentJsonPath = 'deployment-results.json';

function normalizePath(path) {
    return path.normalize('NFC');
}

function getComponentPath(failure) {
    const { componentType, fileName, fullName } = failure;
    const safeName = fileName.split('/').pop();

    switch (componentType) {
        case 'CustomObject':
            return normalizePath(`force-app/main/default/objects/${fullName}`);
        case 'CustomField':
            return normalizePath(`force-app/main/default/objects/${fullName.split('.')[0]}/fields/${fullName.split('.')[1]}.field-meta.xml`);
        case 'RecordType':
            return normalizePath(`force-app/main/default/objects/${fullName.split('.')[0]}/recordTypes/${fullName.split('.')[1]}.recordType-meta.xml`);
        case 'ValidationRule':
            return normalizePath(`force-app/main/default/objects/${fullName.split('.')[0]}/validationRules/${fullName.split('.')[1]}.validationRule-meta.xml`);
        case 'Profile':
            return normalizePath(`force-app/main/default/profiles/${safeName}-meta.xml`);
        case 'PermissionSet':
            return normalizePath(`force-app/main/default/permissionsets/${safeName}-meta.xml`);
        case 'Layout':
            return normalizePath(`force-app/main/default/layouts/${safeName}-meta.xml`);
        case 'ApexClass':
            return normalizePath(`force-app/main/default/classes/${safeName}`);
        case 'CustomMetadata':
            return normalizePath(`force-app/main/default/customMetadata/${safeName}-meta.xml`);
        case 'Flow':
            return normalizePath(`force-app/main/default/flows/${safeName}-meta.xml`);
        case 'Report':
            return normalizePath(`force-app/main/default/reports/${fileName.split('/')[1]}`);
        default:
            return null;
    }
}

async function processFailures(failures) {
    const processed = new Set();

    for (const failure of failures) {
        const repoPath = getComponentPath(failure);
        if (!repoPath || processed.has(repoPath)) continue;
        processed.add(repoPath);

        let existeEnRama = false;
        let mensaje = '';

        try {
            const { stdout } = await execAsync(`git ls-tree origin/ci/mobility --name-only "${repoPath}"`, {
                maxBuffer: 1024 * 1024
            });
            const output = Buffer.from(stdout, 'utf8').toString().trim().normalize('NFC');
            existeEnRama = output !== '';

            mensaje = existeEnRama
                ? `✅ Descartado correctamente: ${repoPath}`
                : `⚠️  ${repoPath} no existe en origin/ci/mobility. No se descarta.`;

            if (existeEnRama) {
                await execAsync(`git checkout origin/ci/mobility -- "${repoPath}"`);
            }
        } catch (e) {
            mensaje = `❌ Error verificando ${repoPath}: ${e.message}`;
        }

        console.log(mensaje);
        debugData.push({
            originalFileName: failure.fileName,
            componentType: failure.componentType,
            fullName: failure.fullName,
            repoPath,
            existeEnRama,
            mensaje
        });
    }

    fs.writeFileSync(debugFilePath, JSON.stringify(debugData, null, 2), 'utf8');
}

async function main() {
    const raw = fs.readFileSync(deploymentJsonPath, 'utf8').replace(/^\uFEFF/, '').trim();
    const json = JSON.parse(raw);
    const failures = json.result.details.componentFailures.filter(f => f.success !== true);
    await processFailures(failures);
}

main();
