const { spawn } = require('child_process');
const fs = require('fs');
const { exec } = require('child_process');
//1- Obtener json desde SF cambiando entorno e id:
//sfdx force:mdapi:deploy:report -i 0AfKN00000DH4he -u solar-develop --json | Out-File -FilePath deployment-results.json -Encoding utf8
//2- ajustar rama más abajo para hacer checkout
//3- lanzar este script desde iberdrola-sfdx: node "C:\Users\aberdun\Downloads\rm\Metadata Management\backpromotions\discardErrorsBP.js"

function extractFailedComponents() {
    fs.readFile('deployment-results.json', 'utf8', (err, data) => {
        if (err) {
            console.error('Error al leer el archivo:', err);
            return;
        }

        try {
            const cleanedData = data.replace(/^\uFEFF/, '').trim();
            const json = JSON.parse(cleanedData);

            // Excluir componentes con success:true
            const filteredFailures = json.result.details.componentFailures
                .filter(failure => failure.success !== true);

            const tasks = [...new Set(
                filteredFailures.map(failure => {
                    let filePath = failure.fileName;
                    let repoPath = '';

                    if (filePath.endsWith('.object')) {
                        repoPath = `force-app/main/default/objects/${filePath.split('/').pop().replace('.object', '')}`;
                    } else if (filePath.endsWith('.report')) {
                        repoPath = `force-app/main/default/reports/${filePath.split('/')[1]}`;
                    } else if (filePath.endsWith('.md')) {
                        repoPath = `force-app/main/default/customMetadata/${filePath.split('/').pop()}-meta.xml`;
                    } else if (filePath.endsWith('.cls')) {
                        repoPath = `force-app/main/default/classes/${filePath.split('/').pop()}`;
                    } else if (filePath.endsWith('.profile')) {
                        repoPath = `force-app/main/default/profiles/${filePath.split('/').pop()}-meta.xml`;
                    } else if (filePath.endsWith('.audience')) {
                        repoPath = `force-app/main/default/audience/${filePath.split('/').pop()}-meta.xml`;
                    } else if (filePath.endsWith('.js')) {
                        repoPath = `force-app/main/default/lwc/${filePath.split('/')[1]}`;
                    } else if (filePath.endsWith('.layout')) {
                        repoPath = `force-app/main/default/layouts/${filePath.split('/').pop()}-meta.xml`;
                    } else if (filePath.endsWith('.permissionset')) {
                        repoPath = `force-app/main/default/permissionsets/${filePath.split('/').pop()}-meta.xml`;
                    } else if (filePath.endsWith('.standardValueSet')) {
                        repoPath = `force-app/main/default/standardValueSets/${filePath.split('/').pop()}-meta.xml`;
                    } else if (filePath.endsWith('.flow')) {
                        repoPath = `force-app/main/default/flows/${filePath.split('/').pop()}-meta.xml`;
                    }

                    return repoPath ? { type: 'file', path: repoPath } : null;
                }).filter(task => task !== null)
            )];

            // **Reemplazar espacios en los nombres de archivos por la versión correcta**
            const normalizeFilePath = (filePath) => {
                return filePath.replace(/ /g, '\\ '); // Escape para espacios
            };

            // Procesar cada tarea secuencialmente
            const processTasks = async () => {
                for (const task of tasks) {
                    const safePath = normalizeFilePath(task.path);
                    const gitCommand = `git checkout origin/ci/mobility -- "${safePath}"`;

                    await new Promise((resolve) => {
                        exec(gitCommand, (error, stdout, stderr) => {
                            if (error) {
                                console.error(`Error al ejecutar git checkout para ${safePath}:`, stderr);
                            } else {
                                console.log(`Recuperado: ${safePath}`);
                            }
                            resolve();
                        });
                    });

                    if (task.type === 'folder') {
                        await new Promise((resolve) => {
                            exec(`git ls-files --others --exclude-standard "${safePath}"`, (error, stdout, stderr) => {
                                if (error) {
                                    console.error(`Error al listar archivos no rastreados en ${safePath}:`, stderr);
                                } else {
                                    const orphanFiles = stdout.split('\n').filter(file => file.trim() !== '');
                                    orphanFiles.forEach(orphanFile => {
                                        console.log(`Eliminando archivo huérfano: ${orphanFile}`);
                                        fs.unlink(orphanFile, unlinkErr => {
                                            if (unlinkErr) {
                                                console.error(`Error al eliminar ${orphanFile}:`, unlinkErr);
                                            } else {
                                                console.log(`Archivo eliminado: ${orphanFile}`);
                                            }
                                        });
                                    });
                                }
                                resolve();
                            });
                        });
                    }
                }
            };

            processTasks();
        } catch (parseError) {
            console.error('Error al procesar el JSON:', parseError);
        }
    });
}

async function main() {
    extractFailedComponents();
}
main();
