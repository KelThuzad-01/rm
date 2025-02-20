import { promises as fs } from 'fs';
import path from 'path';

async function eliminarCustomMetadataAccessesPorNombre(rutaCarpeta, nombreMetadata) {
    try {
        // Leer todos los archivos en la carpeta
        const archivos = await fs.readdir(rutaCarpeta);

        // Procesar cada archivo dentro de la carpeta
        for (const archivo of archivos) {
            const rutaArchivo = path.join(rutaCarpeta, archivo);

            // Leer el archivo completo
            const data = await fs.readFile(rutaArchivo, 'utf8');

            // Crear la expresión regular para encontrar solo el bloque específico con el nombre exacto
            const regex = new RegExp(
                `<customMetadataTypeAccesses>\\s*<enabled>.*?</enabled>\\s*<name>${nombreMetadata}</name>\\s*</customMetadataTypeAccesses>`,
                'g'
            );

            // Eliminar solo el bloque específico que coincide con el nombre exacto
            let archivoModificado = data.replace(regex, '');

            // Solo eliminar líneas vacías si hubo cambios
            if (archivoModificado !== data) {
                // Eliminar líneas vacías resultantes
                archivoModificado = archivoModificado.replace(/^\s*[\r\n]/gm, '');

                // Guardar el archivo modificado
                await fs.writeFile(rutaArchivo, archivoModificado, 'utf8');
                console.log(`${nombreMetadata} OK`);
            }
        }
    } catch (err) {
        console.error('Error:', err);
    }
}

// Parámetros: ruta de la carpeta y nombre del metadata
const [,, rutaCarpeta, nombreMetadata] = process.argv;

eliminarCustomMetadataAccessesPorNombre(rutaCarpeta, nombreMetadata);
