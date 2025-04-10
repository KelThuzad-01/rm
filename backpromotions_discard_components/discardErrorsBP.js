//1- Obtener json desde SF cambiando entorno e id:
//sfdx force:mdapi:deploy:report -i 0Af9Z00000RwWrDSAV -u mobility --json | Out-File -FilePath deployment-results.json -Encoding utf8
//2- ajustar rama más abajo para hacer checkout
//4- lanzar este script desde iberdrola-sfdx: 
// node "C:\Users\aberdun\Downloads\rm\backpromotions_discard_components\discardErrorsBP.js"
const { exec } = require('child_process');
const fs = require('fs');
const readline = require('readline');
const { promisify } = require('util');
const execAsync = promisify(exec);

const debugData = [];
const debugFilePath = 'debug-discard.json';
const deploymentJsonPath = 'deployment-results.json';
const gitEnv = { ...process.env, LANG: 'en_US.UTF-8', LC_ALL: 'en_US.UTF-8' };

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function preguntarUsuario(mensaje) {
    return new Promise((resolve) => {
        rl.question(mensaje, (respuesta) => {
            resolve(respuesta.trim().toLowerCase() === 's');
        });
    });
}

function getComponentPath(failure) {
    const { componentType, fileName, fullName } = failure;
    const safeName = fileName.split('/').pop();

    switch (componentType) {
        case 'CustomObject':
            return `force-app/main/default/objects/${fullName}`;
        case 'CustomField':
            return `force-app/main/default/objects/${fullName.split('.')[0]}/fields/${fullName.split('.')[1]}.field-meta.xml`;
        case 'RecordType':
            return `force-app/main/default/objects/${fullName.split('.')[0]}/recordTypes/${fullName.split('.')[1]}.recordType-meta.xml`;
        case 'ValidationRule':
            return `force-app/main/default/objects/${fullName.split('.')[0]}/validationRules/${fullName.split('.')[1]}.validationRule-meta.xml`;
        case 'ListView':
            return `force-app/main/default/objects/${fullName.split('.')[0]}/listViews/${fullName.split('.')[1]}.listView-meta.xml`;
        case 'StandardValueSet':
            return `force-app/main/default/standardValueSets/${fullName}.standardValueSet-meta.xml`;
        case 'Profile':
            return `force-app/main/default/profiles/${safeName}-meta.xml`;
        case 'PermissionSet':
            return `force-app/main/default/permissionsets/${safeName}-meta.xml`;
        case 'Layout':
            return `force-app/main/default/layouts/${safeName}-meta.xml`;
        case 'ApexClass':
            return `force-app/main/default/classes/${safeName}`;
        case 'CustomMetadata':
            return `force-app/main/default/customMetadata/${safeName}-meta.xml`;
        case 'Flow':
            return `force-app/main/default/flows/${safeName}-meta.xml`;
        case 'Report':
            return `force-app/main/default/reports/${fileName.split('/')[1]}`;
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
            const { stdout } = await execAsync(`git ls-tree origin/ci/mobility --name-only "${repoPath}"`, { env: gitEnv, maxBuffer: 1024 * 1024 });
            existeEnRama = stdout.trim() !== '';

            if (existeEnRama) {
                await execAsync(`git checkout origin/ci/mobility -- "${repoPath}"`, { env: gitEnv });
                mensaje = `✅ Descartado correctamente: ${repoPath}`;
            } else {
                mensaje = `⚠️  ${repoPath} no existe en origin/ci/mobility. No se descarta.`;

                if (fs.existsSync(repoPath)) {
                    const deseaEliminar = await preguntarUsuario(`¿Deseas eliminar localmente "${repoPath}"? (S/N): `);
                    if (deseaEliminar) {
                        fs.unlinkSync(repoPath);
                        mensaje += ' ✅ Eliminado localmente';
                    } else {
                        mensaje += ' ❎ Conservado localmente';
                    }
                } else {
                    mensaje += ' 🛈 Archivo no existe localmente. Omitido.';
                }
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
    rl.close();
}

async function main() {
    const raw = fs.readFileSync(deploymentJsonPath, 'utf8').replace(/^\uFEFF/, '').trim();
    const json = JSON.parse(raw);
    const failures = json.result.details.componentFailures.filter(f => f.success !== true);
    await processFailures(failures);
}

main();
