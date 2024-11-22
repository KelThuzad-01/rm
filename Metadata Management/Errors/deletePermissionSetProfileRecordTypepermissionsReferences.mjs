import { promises as fs } from 'fs';
import path from 'path';


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
                `<recordTypeVisibilities>\\s*<default>.*?</default>\\s*<recordType>.*?${patronField}.*?</recordType>\\s*<visible>.*?</visible>\\s*</recordTypeVisibilities>`,
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
                console.log(`Se ha eliminado correctamente el bloque(s) de recordTypeVisibilities que contienen el patrón ${patronField} en ${archivo}.`);
            } 
        }

    } catch (err) {
        console.error('Error:', err);
    }
}

// Parámetros: ruta de la carpeta y patrón de field
const [,, rutaCarpeta, patronField] = process.argv;

eliminarFieldPermissionsPorPatron(rutaCarpeta, patronField);
