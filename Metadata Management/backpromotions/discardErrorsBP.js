const { spawn } = require('child_process');
const fs = require('fs');
//Obtener json desde SF
//sfdx force:mdapi:deploy:report -i 0AfKN00000DH4he -u mobility --json | Out-File -FilePath deployment-results.json -Encoding utf8

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

function extractFailedComponents() {
    const fs = require('fs');
    const { exec } = require('child_process');
    
    // Leer el JSON con los datos de componentFailures
    fs.readFile('deployment-results.json', 'utf8', (err, data) => {
      if (err) {
        console.error('Error al leer el archivo:', err);
        return;
      }
    
      try {
        // Limpiar y parsear el JSON
        const cleanedData = data.replace(/^\uFEFF/, '').trim();
        const json = JSON.parse(cleanedData);
    
        // Procesar carpetas y archivos específicos
        const tasks = [...new Set([
          ...json.result.details.componentFailures
            .filter(failure => failure.fileName.endsWith('.object')) // Filtrar archivos .object
            .map(failure => ({
              type: 'folder',
              path: `force-app\\main\\default\\objects\\${failure.fileName.split('/').slice(-1)[0].replace('.object', '')}`
            })),
          ...json.result.details.componentFailures
            .filter(failure => failure.fileName.endsWith('.report')) // Filtrar archivos .report
            .map(failure => ({
              type: 'folder',
              path: `force-app\\main\\default\\reports\\${failure.fileName.split('/')[1]}`
            })),
          ...json.result.details.componentFailures
            .filter(failure => failure.fileName.endsWith('.md')) // Filtrar archivos .md
            .map(failure => ({
              type: 'file',
              path: `force-app\\main\\default\\customMetadata\\${failure.fileName.split('/').slice(-1)[0]}-meta.xml`
            })),
          ...json.result.details.componentFailures
            .filter(failure => failure.fileName.endsWith('.cls')) // Filtrar archivos .cls
            .map(failure => ({
              type: 'file',
              path: `force-app\\main\\default\\classes\\${failure.fileName.split('/').slice(-1)[0]}-meta.xml`
            })),
          ...json.result.details.componentFailures
            .filter(failure => failure.fileName.endsWith('.profile')) // Filtrar archivos .profile
            .map(failure => ({
              type: 'file',
              path: `force-app\\main\\default\\profiles\\${failure.fileName.split('/').slice(-1)[0]}-meta.xml`
            })),
          ...json.result.details.componentFailures
            .filter(failure => failure.fileName.endsWith('.audience')) // Filtrar archivos .audience
            .map(failure => ({
              type: 'file',
              path: `force-app\\main\\default\\audience\\${failure.fileName.split('/').slice(-1)[0]}-meta.xml`
            })),
          ...json.result.details.componentFailures
            .filter(failure => failure.fileName.endsWith('.js')) // Filtrar archivos .js
            .map(failure => ({
              type: 'folder',
              path: `force-app\\main\\default\\lwc\\${failure.fileName.split('/')[1]}`
            })),
          ...json.result.details.componentFailures
            .filter(failure => failure.fileName.endsWith('.layout')) // Filtrar archivos .layout
            .map(failure => ({
              type: 'file',
              path: `force-app\\main\\default\\layouts\\${failure.fileName.split('/').slice(-1)[0]}-meta.xml`
            })),
          ...json.result.details.componentFailures
            .filter(failure => failure.fileName.endsWith('.flow')) // Filtrar archivos .flow
            .map(failure => ({
              type: 'file',
              path: `force-app\\main\\default\\flows\\${failure.fileName.split('/').slice(-1)[0]}-meta.xml`
            })),
          ...json.result.details.componentFailures
            .filter(failure => failure.fileName.endsWith('.permissionset')) // Filtrar archivos .permissionset
            .map(failure => ({
              type: 'file',
              path: `force-app\\main\\default\\permissionsets\\${failure.fileName.split('/').slice(-1)[0]}-meta.xml`
            }))
        ])]; // Usar Set para evitar duplicados
    
        // Procesar cada tarea secuencialmente
        const processTasks = async () => {
          for (const task of tasks) {
            const gitCommand = `git checkout ci/mobility -- "${task.path}"`; // Envolver la ruta en comillas
    
            await new Promise((resolve) => {
              exec(gitCommand, (error, stdout, stderr) => {
                if (error) {
                  console.error(`Error al ejecutar git checkout para ${task.path}:`, stderr);
                }
                resolve();
              });
            });
    
            // Eliminar archivos huérfanos solo para carpetas
            if (task.type === 'folder') {
              await new Promise((resolve) => {
                exec(`git ls-files --others --exclude-standard "${task.path}"`, (error, stdout, stderr) => {
                  if (error) {
                    console.error(`Error al listar archivos no rastreados en ${task.path}:`, stderr);
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

    //const { code, deploymentData } = await deployToSalesforce();

}
main();
