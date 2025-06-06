import { promises as fs } from 'fs';
import path from 'path';


//Elimina los fieldPermission en PermissionSet/Perfiles a partir de un objeto o un campo

//node .\deletePermissionSetFieldpermissionsReferencesByObject.mjs C:\Users\aberdun\Downloads\iberdrola-sfdx\force-app\main\default\profiles IBD_OpportunityRelationship__c.IBD_SourceOpportunityStage__c (solo este campo)

//node .\deletePermissionSetFieldpermissionsReferencesByObject.mjs C:\Users\aberdun\Downloads\iberdrola-sfdx\force-app\main\default\profiles IBD_OpportunityRelationship__c (todas las referencias del objeto)


async function eliminarFieldPermissionsPorPatron(rutaCarpeta, patronField) {
    try {
        // Leer todos los archivos en la carpeta
        const archivos = await fs.readdir(rutaCarpeta);

        // Procesar cada archivo dentro de la carpeta
        for (const archivo of archivos) {
            const rutaArchivo = path.join(rutaCarpeta, archivo);

            // Leer el archivo completo
            const data = await fs.readFile(rutaArchivo, 'utf8');

            // Crear la expresión regular para encontrar solo el bloque <fieldPermissions> específico que contiene el patrón en <field>
            const regex = new RegExp(
                `<tabVisibilities>\\s*<tab>.*?${patronField}.*?</tab>\\s*<visibility>.*?</visibility>\\s*</tabVisibilities>`,
                'g'
            );

            // Eliminar solo los bloques <fieldPermissions> que coincidan con el patrón en <field>
            let archivoModificado = data.replace(regex, '');

            // Solo eliminar líneas vacías si hubo cambios
            if (archivoModificado !== data) {
                // Eliminar líneas vacías resultantes
                archivoModificado = archivoModificado.replace(/^\s*[\r\n]/gm, '');

                // Guardar el archivo modificado
                await fs.writeFile(rutaArchivo, archivoModificado, 'utf8');
                console.log(`${patronField} OK`);
            } 
        }

    } catch (err) {
        console.error('Error:', err);
    }
}

// Parámetros: ruta de la carpeta y patrón de field
const [,, rutaCarpeta, patronField] = process.argv;

eliminarFieldPermissionsPorPatron(rutaCarpeta, patronField);
