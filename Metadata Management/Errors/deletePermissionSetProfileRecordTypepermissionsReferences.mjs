import { promises as fs } from 'fs';
import path from 'path';

async function eliminarRecordTypeVisibilitiesPorPatron(rutaCarpeta, patronRecordType) {
    try {
        // Leer todos los archivos en la carpeta
        const archivos = await fs.readdir(rutaCarpeta);

        // Procesar cada archivo dentro de la carpeta
        for (const archivo of archivos) {
            const rutaArchivo = path.join(rutaCarpeta, archivo);

            // Leer el archivo completo
            const data = await fs.readFile(rutaArchivo, 'utf8');

            // Expresión regular para eliminar el bloque <recordTypeVisibilities> en perfiles
            const regexProfile = new RegExp(
                `<recordTypeVisibilities>\\s*(?:<default>.*?</default>\\s*)?<recordType>\\s*${patronRecordType}\\s*</recordType>\\s*<visible>.*?</visible>\\s*</recordTypeVisibilities>`,
                'g'
            );

            // Expresión regular para eliminar el bloque <recordTypeVisibilities> en permission sets
            const regexPermissionSet = new RegExp(
                `<recordTypeVisibilities>\\s*<recordType>\\s*${patronRecordType}\\s*</recordType>\\s*<visible>.*?</visible>\\s*</recordTypeVisibilities>`,
                'g'
            );

            // Aplicar las eliminaciones
            let archivoModificado = data.replace(regexProfile, '').replace(regexPermissionSet, '');

            // Solo eliminar líneas vacías si hubo cambios
            if (archivoModificado !== data) {
                archivoModificado = archivoModificado.replace(/^\s*[\r\n]/gm, ''); // Eliminar líneas vacías

                // Guardar el archivo modificado
                await fs.writeFile(rutaArchivo, archivoModificado, 'utf8');
                console.log(`${patronRecordType} eliminado correctamente`);
            }
        }
    } catch (err) {
        console.error('Error:', err);
    }
}

// Parámetros: ruta de la carpeta y patrón de RecordType
const [,, rutaCarpeta, patronRecordType] = process.argv;

eliminarRecordTypeVisibilitiesPorPatron(rutaCarpeta, patronRecordType);
